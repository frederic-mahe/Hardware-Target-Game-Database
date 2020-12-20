#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
use a database to identify and organize files.
"""
import os
import sys
import shutil
import hashlib
import argparse
import zipfile
from collections import defaultdict
from collections import Counter


__author__ = "aquaman"
__date__ = "2020/12/20"
__version__ = "$Revision: 3.6"


# *********************************************************************#
#                                                                      #
#                            Functions                                 #
#                                                                      #
# *********************************************************************#

if __name__ == '__main__':
    """
    Parse arguments from command line.
    """
    parser = argparse.ArgumentParser(
        description="use a database to identify and organize files.")
    # Add support for boolean arguments. Allows us to accept 1-argument forms
    # of boolean flags whose values are any of "yes", "true", "t" or "1".
    parser.register('type', 'bool', (lambda x: x.lower() in
                                     ("yes", "true", "t", "1")))

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
                              "of a file and hardlinks to that first one for "
                              "successive files."))

    # Valid uses of this flag include: -s, -s true, -s yes, --skip_existing=1
    parser.add_argument("-s", "--skip_existing",
                        dest="skip_existing",
                        default=False,
                        # nargs and const below allow us to accept the
                        # zero-argument form of --skip_existing
                        nargs="?",
                        const=True,
                        type='bool',
                        help=("Skip files which already exist at the "
                              "destination without overwriting them."))

    # Valid uses of this flag include: -l, -l true, -l yes, --new_line=1
    parser.add_argument("-l", "--new_line",
                        dest="new_line",
                        default=False,
                        # nargs and const below allow us to accept the
                        # zero-argument form of --new_line
                        nargs="?",
                        const=True,
                        type='bool',
                        help=("Changes the way the stdout is printed, and "
                              "allows for UI subprocess monitoring."))

    # Valid uses of this flag include: -x, -x true, -x yes,
    # --drop_initial_directory=1
    parser.add_argument("-x", "--drop_initial_directory",
                        dest="drop_initial_directory",
                        default=False,
                        # nargs and const below allow us to accept the
                        # zero-argument form of --drop_initial_directory
                        nargs="?",
                        const=True,
                        type='bool',
                        help=("Drops the 1st directory path in the SMDB file "
                              "so you can customize the name."))

    ARGS = parser.parse_args()


def write_empty_file(dest):
    """
    Creates an empty file at the destination path

    Arguments:
      dest - The destination where the empty file will be located
    """

    # When destination file exists...
    # Do nothing if skip_existing is set, otherwise remove file (to
    # avoid FileExistsError when writing new file).
    if os.path.exists(dest):
        if ARGS.skip_existing:
            return
        else:
            os.remove(dest)

    # Create directories if needed
    base_dir = os.path.dirname(os.path.abspath(dest))
    if not os.path.exists(base_dir):
        try:
            os.makedirs(base_dir, exist_ok=True)
        except (FileNotFoundError, OSError):
            fixed_base_dir = u'\\\\?\\' + base_dir
            os.makedirs(fixed_base_dir, exist_ok=True)

    # Create empty file
    try:
        open(dest, 'a').close()
    except (FileNotFoundError, OSError):
        fixed_dest = u'\\\\?\\' + os.path.abspath(dest)
        open(fixed_dest, 'a').close()


def copy_file(source, dest, original):
    """
    Copy a file from source to destination using a configurable file copy
    strategy controlled by the --file_strategy command.

    Arguments:
      source   - The file to copy/hardlink
      dest     - The destination where the new file will be located
      original - The first file associated with a specific hash value
    """

    if (ARGS.file_strategy == "copy"):
        copy_fn = shutil.copyfile
    elif (ARGS.file_strategy == "hardlink"):
        copy_fn = os.link
    elif (ARGS.file_strategy == "smart"):
        if original == dest:
            copy_fn = shutil.copyfile
        else:
            copy_fn = os.link
            source = original
    else:
        raise Exception("Unknown copy strategy {}".format(ARGS.file_strategy))

    # When destination file exists...
    # Do nothing if skip_existing is set, otherwise remove file (to
    # avoid FileExistsError when writing new file).
    if os.path.exists(dest):
        if ARGS.skip_existing:
            return
        else:
            os.remove(dest)

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


def extract_file(filename, entry, method, dest):
    """
    extracts entry from archive to given destination directory
    """
    if method == 'zip':
        # Stolen shamelessly from https://stackoverflow.com/a/4917469
        # Eliminates the random directories that appear when a file is
        # extracted from a zip file
        with zipfile.ZipFile(filename) as zip_file:
            for member in zip_file.namelist():
                filename = os.path.basename(member)
                # skip directories
                if not filename:
                    continue

                # copy file (taken from zipfile's extract)
                source = zip_file.open(member)
                target = open(dest, "wb")
                with source, target:
                    shutil.copyfileobj(source, target)


def parse_database(target_database, drop_initial_directory):
    """
    store hash values and filenames in a database.
    """
    db = defaultdict(list)  # missing key's default value is an empty list
    number_of_entries = 0
    with open(target_database, "r") as target_database:
        for line in target_database:
            hash_sha256, filename, _, _, hash_crc = line.strip().split("\t", 4)
            number_of_entries += 1
            if drop_initial_directory:
                first_level, filename = filename.split("/", 1)
            filename = os.path.normpath(filename)
            db[hash_sha256].append(filename)
            db[hash_crc].append(filename)
    return db, number_of_entries


def print_progress(current, total, end):
    print_function("processing file: {:>9} / {}".format(current, total),
                   end=end)


def print_function(text, end, file=sys.stdout, flush=True):
    print(text, end=end, file=file, flush=flush)


def parse_folder(source_folder, db, output_folder):
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
                            new_path = os.path.join(output_folder,
                                                    os.path.dirname(entry))
                            # create directory structure if need be
                            if not os.path.exists(new_path):
                                os.makedirs(new_path, exist_ok=True)
                            new_file = os.path.join(output_folder, entry)
                            if loop == 1:
                                original = new_file
                            if (not ARGS.skip_existing or not
                                    os.path.exists(new_file)):
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
                                              original)
                        # remove the hit from the database
                        del db[h]

                i += 1
                print_progress(i, total, END_LINE)
    else:
        if not ARGS.new_line:
            print_progress(i, total, "\n")


def get_hashes(filename):
    """
    return dictionary of hashes containing:
        - sha256 hash of the file itself
        - additional hashes if the file is a compressed archive
    """
    hashes = {}
    h = hashlib.sha256()

    # hash the file itself
    with open(filename, "rb", buffering=0) as f:
        # use a small buffer to compute hash to
        # avoid memory overload
        for b in iter(lambda: f.read(128 * 1024), b''):
            h.update(b)

    # add file hash to dict
    hashes[h.hexdigest()] = {
        'filename': filename,
        'archive': None
    }

    # if this is a zipfile, extract CRCs from header
    if zipfile.is_zipfile(filename):
        try:
            with zipfile.ZipFile(filename, 'r') as z:
                for info in z.infolist():
                    # add archive entry hash to dict
                    crc_formatted_hex = '{0:08x}'.format(info.CRC & 0xffffffff)
                    hashes[crc_formatted_hex] = {
                        'filename': filename,
                        'archive': {
                            'entry': info.filename,
                            'type': 'zip'
                        }
                    }
        except (OSError, UnicodeDecodeError, zipfile.BadZipFile):
            # Possible normal file containing a zip magic number?
            print('**** ERROR ****')
            print('**** Attempted to parse {} as a zip archive.'.format(
                  filename))
            print('**** If this file is not a zip archive, you may safely'
                  ' ignore this error.')
            print('***************')
            pass

    return hashes


# *********************************************************************#
#                                                                      #
#                              Body                                    #
#                                                                      #
# *********************************************************************#

if __name__ == '__main__':
    SOURCE_FOLDER = ARGS.source_folder
    TARGET_DATABASE = ARGS.target_database
    OUTPUT_FOLDER = ARGS.output_folder
    MISSING_FILES = ARGS.missing_files
    END_LINE = "\n" if ARGS.new_line else "\r"
    DROP_INITIAL_DIRECTORY = ARGS.drop_initial_directory

    DATABASE, NUMBER_OF_ENTRIES = parse_database(TARGET_DATABASE,
                                                 DROP_INITIAL_DIRECTORY)
    parse_folder(SOURCE_FOLDER, DATABASE, OUTPUT_FOLDER)

    # Observed files will have either their SHA256 or their CRC32 entry
    # deleted (or both) from the database. For missing files, both entries
    # will still be present. If the hash for an empty file exists as both
    # SHA256 and CRC32, then it is missing and will be created below.
    #
    # For reference, an empty file will always have the following hashes:
    # SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    # SHA1:   da39a3ee5e6b4b0d3255bfef95601890afd80709
    # MD5SUM: d41d8cd98f00b204e9800998ecf8427e
    # CRC32:  00000000
    if (('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
            in DATABASE) and ('00000000' in DATABASE)):
        for file in DATABASE['00000000']:
            empty_file = os.path.join(OUTPUT_FOLDER, file)
            write_empty_file(empty_file)

    # Since missing files will be in the database twice as explained above,
    # only keep the SHA256 entry (64 char length hash) when listing out the
    # missing files. This will prevent missing files from being counted more
    # than once.
    file_counts = Counter([str(i) for i in DATABASE.values()])
    duplicate_files = set([str(i) for i in file_counts if file_counts[i] == 2])

    missing_file_list = [(os.path.basename(DATABASE[entry][0]), entry)
                         for entry in DATABASE
                         if (str(DATABASE[entry]) in duplicate_files
                         and len(entry) == 64)]

    missing_entry_count = sum([len(DATABASE[missing_file[1]])
                               for missing_file in missing_file_list])

    FOUND_ENTRIES = NUMBER_OF_ENTRIES - missing_entry_count

    if missing_file_list:
        missing_file_list.sort()
        if MISSING_FILES:
            with open(MISSING_FILES, "w") as missing_files:
                for missing_file, entry in missing_file_list:
                    print(missing_file, entry, sep="\t", file=missing_files)
    else:
        print("no missing file")

    COVERAGE = round(100.0 * FOUND_ENTRIES / NUMBER_OF_ENTRIES, 2)
    print('coverage: {}/{} ({}%)'.format(FOUND_ENTRIES,
                                         NUMBER_OF_ENTRIES,
                                         COVERAGE),
          file=sys.stdout)

    sys.exit(0)
