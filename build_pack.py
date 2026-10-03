#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
use a database to identify and organize files.
"""
import os
import sys
import shutil
import argparse
import struct
import zipfile
import tempfile
try:
    import py7zr
except ImportError:
    # py7zr is an optional dependency: without it, SevenZipArchive is never
    # defined, and .7z files are treated like any other unsupported file type.
    py7zr = None
from collections import defaultdict
from collections import Counter
from pathlib import Path

from htgdb import cli, hashing, progress, smdb


__author__ = "aquaman"
__date__ = "2021/07/25"
__version__ = "$Revision: 3.7"


# *********************************************************************#
#                                                                      #
#                            Functions                                 #
#                                                                      #
# *********************************************************************#

def parse_args(argv=None):
    """
    Parse arguments from command line.
    """
    parser = argparse.ArgumentParser(
        description="use a database to identify and organize files.")
    # Add support for the shared boolean flags.
    cli.register_bool_type(parser)

    parser.add_argument("-i", "--input_folder",
                        dest="source_folder",
                        required=True,
                        help="set source folder")

    parser.add_argument("-d", "--database",
                        dest="target_database",
                        required=True,
                        help="set target database")

    parser.add_argument("-o", "--output_folder",
                        dest="output_folder",
                        required=True,
                        help="set output folder")

    parser.add_argument("-m", "--missing",
                        dest="missing_files",
                        default=None,
                        help="list missing files")

    parser.add_argument("--file_strategy",
                        choices=["copy", "hardlink", "smart"],
                        dest="file_strategy",
                        default="copy",
                        help=("Strategy for how to get files into the output "
                              "folder. Smart uses copy for first instance of "
                              "a file and hardlinks to that first one for "
                              "successive files."))

    # Valid uses of this flag include: -s, -s true, -s yes, --skip_existing=1
    cli.add_skip_existing_argument(parser)

    # Valid uses of this flag include: -l, -l true, -l yes, --new_line=1
    cli.add_new_line_argument(parser)

    # Valid uses of this flag include: -x, -x true, -x yes,
    # --drop_initial_directory=1
    cli.add_drop_initial_directory_argument(parser)

    return parser.parse_args(argv)


def write_empty_file(dest, skip_existing):
    """
    Creates an empty file at the destination path

    Arguments:
      dest          - The destination where the empty file will be located
      skip_existing - Leave an already-present file untouched
    """

    dest_path = Path(dest)

    # When destination file exists...
    # Do nothing if skip_existing is set, otherwise remove file (to
    # avoid FileExistsError when writing new file).
    if dest_path.exists():
        if skip_existing:
            return
        else:
            dest_path.unlink()

    # Create directories if needed
    base_dir = Path(os.path.abspath(dest)).parent
    if not base_dir.exists():
        try:
            base_dir.mkdir(parents=True, exist_ok=True)
        except (FileNotFoundError, OSError):
            # Windows long-path fallback uses the string \\?\ prefix.
            os.makedirs(u'\\\\?\\' + str(base_dir), exist_ok=True)

    # Create empty file
    try:
        dest_path.touch()
    except (FileNotFoundError, OSError):
        fixed_dest = u'\\\\?\\' + os.path.abspath(dest)
        open(fixed_dest, 'a').close()


def copy_file(source, dest, original, file_strategy, skip_existing):
    """
    Copy a file from source to destination using a configurable file copy
    strategy controlled by the --file_strategy command.

    Arguments:
      source        - The file to copy/hardlink
      dest          - The destination where the new file will be located
      original      - The first file associated with a specific hash value
      file_strategy - One of "copy", "hardlink" or "smart"
      skip_existing - Leave an already-present file untouched
    """

    if (file_strategy == "copy"):
        copy_fn = shutil.copyfile
    elif (file_strategy == "hardlink"):
        copy_fn = os.link
    elif (file_strategy == "smart"):
        if original == dest:
            copy_fn = shutil.copyfile
        else:
            copy_fn = os.link
            source = original
    else:
        raise Exception(f"Unknown copy strategy {file_strategy}")

    # When destination file exists...
    # Do nothing if skip_existing is set, otherwise remove file (to
    # avoid FileExistsError when writing new file).
    dest_path = Path(dest)
    if dest_path.exists():
        if skip_existing:
            return
        else:
            dest_path.unlink()

    try:
        # copy the file to the new directory
        copy_fn(source, dest)
    except FileNotFoundError:
        # Windows' default API is limited to paths of 260 characters
        fixed_dest = u'\\\\?\\' + os.path.abspath(dest)
        copy_fn(source, fixed_dest)
    except OSError:
        try:
            shutil.copyfile(source, dest)
        except FileNotFoundError:
            # Windows' default API is limited to paths of 260 characters
            fixed_dest = u'\\\\?\\' + os.path.abspath(dest)
            shutil.copyfile(source, fixed_dest)


class BaseArchive:
    # Every direct subclass is automatically discovered as a supported archive
    # format via the __subclasses__() method (see get_archive_handler() and
    # extract_file() below). Adding a new format just entails writing its subclass.
    archive_type = None
    # Exceptions we should handle internally rather than letting propagate.
    handled_exceptions = (OSError,)

    def __init__(self, filename):
        self.filename = filename

    @staticmethod
    def looks_like(filename):
        """Return True if filename appears to be this archive format."""
        raise NotImplementedError

    def get_entries(self):
        """Yields (entry_name, crc32_hex), handling known failure modes
        internally."""
        try:
            yield from self._read_entries()
        except self.handled_exceptions:
            self.handle_error()

    def _read_entries(self):
        """Subclasses implement the actual per-format parsing/iteration."""
        raise NotImplementedError

    def extract_entry(self, entry, dest):
        """Extracts a specific entry to the destination path"""
        raise NotImplementedError

    def handle_error(self):
        """Report a failure caught via handled_exceptions. Does nothing by
        default; subclasses can override to warn the user as needed (e.g. an
        erroneously detected archive type)."""
        pass


class ZipArchive(BaseArchive):
    archive_type = 'zip'
    handled_exceptions = (OSError, UnicodeDecodeError, zipfile.BadZipFile)

    @staticmethod
    def looks_like(filename):
        return zipfile.is_zipfile(filename)

    def _read_entries(self):
        with zipfile.ZipFile(self.filename, 'r') as z:
            for info in z.infolist():
                yield info.filename, '{0:08x}'.format(info.CRC & 0xffffffff)

    def extract_entry(self, entry, dest):
        # Stolen shamelessly from https://stackoverflow.com/a/4917469
        # Eliminates the random directories that appear when a file is
        # extracted from a zip file
        with zipfile.ZipFile(self.filename) as zip_file:
            for member in zip_file.namelist():
                # skip other files in the zip
                if member != entry:
                    continue

                basename = os.path.basename(member)
                # skip directories
                if not basename:
                    continue

                # copy file (taken from zipfile's extract)
                source = zip_file.open(member)
                target = open(dest, "wb")
                with source, target:
                    shutil.copyfileobj(source, target)

    def handle_error(self):
        # Possible normal file containing a zip magic number?
        print('**** ERROR ****')
        print('**** Attempted to parse {} as a zip archive.'.format(
              self.filename))
        print('**** If this file is not a zip archive, you may safely'
              ' ignore this error.')
        print('***************')


# SevenZipArchive is only defined when py7zr is actually installed; otherwise,
# the class is absent from BaseArchive.__subclasses__().
if py7zr:
    class SevenZipArchive(BaseArchive):
        archive_type = '7z'
        # py7zr's header parser can raise a bare struct.error (rather than
        # one of its own ArchiveError subclasses) on a truncated/corrupt file.
        handled_exceptions = (OSError, py7zr.exceptions.ArchiveError,
                              struct.error)

        @staticmethod
        def looks_like(filename):
            return py7zr.is_7zfile(filename)

        def _read_entries(self):
            with py7zr.SevenZipFile(self.filename) as z:
                for name in z.getnames():
                    yield name, f"{z.getinfo(name).crc32:08x}"

        def extract_entry(self, entry, dest):
            with py7zr.SevenZipFile(self.filename) as z:
                with tempfile.TemporaryDirectory() as tmpdir:
                    z.extract(path=tmpdir, targets=[entry])
                    extracted_file = Path(tmpdir) / entry
                    with open(extracted_file, "rb") as source, open(dest, "wb") as target:
                        shutil.copyfileobj(source, target)

        def handle_error(self):
            # Unlike zip's end-of-central-directory scan, py7zr's is_7zfile()
            # check is an exact magic-number match, so a false positive is very
            # unlikely. A failure therefore almost certainly indicates that the file
            # is corrupt or uses an unsupported feature.
            print('**** ERROR ****')
            print('**** Failed to read {} as a 7z archive.'.format(
                  self.filename))
            print('**** The file may be corrupt or use an unsupported feature '
                  '(e.g. encryption).')
            print('***************')


def get_archive_handler(filename):
    for archive_class in BaseArchive.__subclasses__():
        if archive_class.looks_like(filename):
            return archive_class(filename)
    return None


def extract_file(filename, entry, method, dest):
    """
    extracts entry from archive to given destination directory
    """
    archive_classes = {cls.archive_type: cls
                       for cls in BaseArchive.__subclasses__()}
    if method not in archive_classes:
        raise ValueError(f"Unknown archive method {method!r}")
    archive_classes[method](filename).extract_entry(entry, dest)


def parse_database(target_database, drop_initial_directory):
    """
    Store hash values and filenames in a database keyed by both SHA256 and
    CRC32 (so files can be matched either way, including zip entries).
    """
    db = defaultdict(list)  # missing key's default value is an empty list
    number_of_entries = 0
    for entry in smdb.read_entries(target_database, drop_initial_directory):
        number_of_entries += 1
        db[entry.sha256].append(entry.path)
        if entry.crc32:
            db[entry.crc32].append(entry.path)
    return db, number_of_entries


def parse_folder(source_folder, db, output_folder, file_strategy,
                 skip_existing, end_line, new_line):
    """
    read each file, produce a hash value and place it in the directory tree.
    """
    i = 0
    total = len([os.path.join(dp, f) for dp, dn, fn in
                 os.walk(os.path.expanduser(source_folder)) for f in fn])
    for dirpath, dirnames, filenames in os.walk(source_folder):
        if filenames:
            for f in filenames:
                filename = os.path.join(os.path.normpath(dirpath),
                                        os.path.normpath(f))
                absolute_filename = u'\\\\?\\' + os.path.abspath(filename)
                try:
                    hashes = get_hashes(filename)
                except FileNotFoundError:
                    hashes = get_hashes(absolute_filename)

                for h, info in hashes.items():
                    if h in db:
                        # we have a hit
                        loop = 0
                        for entry in db[h]:
                            loop += 1
                            new_path = Path(output_folder) / Path(entry).parent
                            # create directory structure if need be
                            if not new_path.exists():
                                new_path.mkdir(parents=True, exist_ok=True)
                            new_file = Path(output_folder) / entry
                            if loop == 1:
                                original = new_file
                            if (not skip_existing or not
                                    new_file.exists()):
                                if info['archive']:
                                    # extract file from archive to directory
                                    extract_file(info['filename'],
                                                 info['archive']['entry'],
                                                 info['archive']['type'],
                                                 new_file)
                                else:
                                    # copy the file to the new directory
                                    copy_file(info['filename'],
                                              new_file,
                                              original,
                                              file_strategy,
                                              skip_existing)
                        # remove the hit from the database
                        del db[h]

                i += 1
                progress.print_message(progress.format_progress(i, total),
                                       end_line)
    else:
        if not new_line:
            progress.print_message(progress.format_progress(i, total), "\n")


def get_hashes(filename):
    """
    return dictionary of hashes containing:
        - sha256 hash of the file itself
        - additional hashes if the file is a compressed archive
    """
    hashes = {}

    # add the file's own SHA256 hash to dict
    hashes[hashing.sha256_file(filename)] = {
        'filename': filename,
        'archive': None
    }

    archive = get_archive_handler(filename)
    if archive:
        for name, crc in archive.get_entries():
            hashes[crc] = {
                'filename': filename,
                'archive': {
                    'entry': name,
                    'type': archive.archive_type
                }
            }

    return hashes


# *********************************************************************#
#                                                                      #
#                              Body                                    #
#                                                                      #
# *********************************************************************#

# An empty file always has the following hashes:
# SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
# SHA1:   da39a3ee5e6b4b0d3255bfef95601890afd80709
# MD5SUM: d41d8cd98f00b204e9800998ecf8427e
# CRC32:  00000000
EMPTY_FILE_SHA256 = \
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
EMPTY_FILE_CRC32 = "00000000"


def create_missing_empty_files(db, output_folder, skip_existing):
    """
    Observed files have their SHA256 and/or CRC32 entry removed from the
    database. A still-present empty-file hash (both SHA256 and CRC32) means
    the empty file was missing, so it is (re)created here.
    """
    if EMPTY_FILE_SHA256 in db and EMPTY_FILE_CRC32 in db:
        for file in db[EMPTY_FILE_CRC32]:
            empty_file = Path(output_folder) / file
            write_empty_file(empty_file, skip_existing)


def collect_missing_files(db, number_of_entries):
    """
    Return ``(missing_file_list, found_entries)``.

    Missing files appear in the database twice (their SHA256 and CRC32 both
    survive), so only the 64-character SHA256 entry is kept to avoid counting
    them more than once.
    """
    file_counts = Counter([str(i) for i in db.values()])
    duplicate_files = set([str(i) for i in file_counts if file_counts[i] == 2])

    missing_file_list = [(Path(db[entry][0]).name, entry)
                         for entry in db
                         if (str(db[entry]) in duplicate_files
                         and len(entry) == 64)]

    missing_entry_count = sum([len(db[missing_file[1]])
                               for missing_file in missing_file_list])

    found_entries = number_of_entries - missing_entry_count
    return missing_file_list, found_entries


def main(argv=None):
    """Entry point: build an organized pack from a source folder and SMDB."""
    args = parse_args(argv)
    end_line = "\n" if args.new_line else "\r"

    database, number_of_entries = parse_database(args.target_database,
                                                 args.drop_initial_directory)
    parse_folder(args.source_folder, database, args.output_folder,
                 args.file_strategy, args.skip_existing, end_line,
                 args.new_line)

    create_missing_empty_files(database, args.output_folder,
                               args.skip_existing)

    missing_file_list, found_entries = collect_missing_files(
        database, number_of_entries)

    if missing_file_list:
        missing_file_list.sort()
        if args.missing_files:
            with Path(args.missing_files).open("w") as missing_files:
                for missing_file, entry in missing_file_list:
                    print(missing_file, entry, sep="\t", file=missing_files)
    else:
        print("no missing file")

    coverage = round(100.0 * found_entries / number_of_entries, 2)
    print(f"coverage: {found_entries}/{number_of_entries} ({coverage}%)",
          file=sys.stdout)

    return 0


if __name__ == '__main__':
    sys.exit(main())
