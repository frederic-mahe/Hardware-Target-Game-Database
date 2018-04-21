#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
use a database to identify and organize files.
"""

__author__ = "aquaman"
__date__ = "2017/11/17"
__version__ = "$Revision: 3.1"


import os
import sys
import shutil
import hashlib
import argparse


#**********************************************************************#
#                                                                      #
#                            Functions                                 #
#                                                                      #
#**********************************************************************#

if __name__ == '__main__':
    """
    Parse arguments from command line.
    """
    parser = argparse.ArgumentParser(description="use a database to identify and organize files.")
    # Add support for boolean arguments. Allows us to accept 1-argument forms of
    # boolean flags whose values are any of "yes", "true", "t" or "1".
    parser.register('type', 'bool', (lambda x: x.lower() in ("yes", "true", "t", "1")))

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
                        choices=["copy", "hardlink", "symlink"],
                        dest="file_strategy",
                        default="copy",
                        help=("Strategy for how to get files into the output "
                              "folder."))

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

    ARGS = parser.parse_args()

def copy_file(source, dest):
    """Get a file from source to destination, with a configurable strategy.

    This method makes a file at source additionally appear at dest. The way this
    is accomplished is controlled via the --file_strategy command.

    Args:
      source - The file to copy/symlink/etc.
      dest - The destination that the new file should appear at
    """
    if ARGS.file_strategy == "copy":
        copy_fn = shutil.copyfile
    elif ARGS.file_strategy == "hardlink":
        copy_fn = os.link
    elif ARGS.file_strategy == "symlink":
        copy_fn = os.symlink
    else:
        raise Exception("Unknown copy strategy {}".format(ARGS.file_strategy))

    try:
        # copy the file to the new directory
        copy_fn(source, dest)
    except FileNotFoundError:
        # Windows' default API is limited to paths of 260 characters
        fixed_dest = u'\\\\?\\' + os.path.abspath(dest)
        copy_fn(absolute_filename, fixed_dest)

def parse_database(target_database):
    """
    store hash values and filenames in a database.
    """
    db = dict()
    with open(target_database, "r") as target_database:
        number_of_entries = 0
        for line in target_database:
            hash_value, filename, other_hash = line.strip().split("\t", 2)
            number_of_entries += 1
            if hash_value not in db:
                db[hash_value] = [filename]
            else:
                db[hash_value].append(filename)

    return db, number_of_entries


def parse_folder(source_folder, db, output_folder):
    """
    read each file, produce a hash value and place it in the directory tree.
    """
    found_entries = 0
    i = 0
    for dirpath, dirnames, filenames in os.walk(source_folder):
        if filenames:
            for f in filenames:
                filename = os.path.join(os.path.normpath(dirpath), f)
                absolute_filename = u'\\\\?\\' + os.path.abspath(filename)
                h = hashlib.sha256()
                try:
                    with open(filename, "rb", buffering=0) as f:
                        # use a small buffer to compute hash to
                        # avoid memory overload
                        for b in iter(lambda : f.read(128 * 1024), b''):
                            h.update(b)
                except FileNotFoundError:
                    with open(absolute_filename, "rb", buffering=0) as f:
                        # use a small buffer to compute hash to
                        # avoid memory overload
                        for b in iter(lambda : f.read(128 * 1024), b''):
                            h.update(b)
                if h.hexdigest() in db:
                    # we have a hit
                    for entry in db[h.hexdigest()]:
                        found_entries += 1
                        new_path = os.path.join(output_folder,
                                                os.path.dirname(entry))
                        # create directory structure if need be
                        if not os.path.exists(new_path):
                            os.makedirs(new_path, exist_ok=True)
                        new_file = os.path.join(output_folder, entry)
                        if (not ARGS.skip_existing or not
                                os.path.exists(new_file)):
                            # copy the file to the new directory
                            copy_file(filename, new_file)
                    # remove the hit from the database
                    del db[h.hexdigest()]
                i += 1
                print("processing file: {:>9}".format(i),
                      end="\r", file=sys.stdout, flush=True)
    else:
        print('processing file: {:>9}'.format(i), file=sys.stdout)


    return found_entries


#**********************************************************************#
#                                                                      #
#                              Body                                    #
#                                                                      #
#**********************************************************************#

if __name__ == '__main__':
    SOURCE_FOLDER = ARGS.source_folder
    TARGET_DATABASE = ARGS.target_database
    OUTPUT_FOLDER = ARGS.output_folder
    MISSING_FILES = ARGS.missing_files
    DATABASE, NUMBER_OF_ENTRIES = parse_database(TARGET_DATABASE)
    FOUND_ENTRIES = parse_folder(SOURCE_FOLDER, DATABASE, OUTPUT_FOLDER)
    if MISSING_FILES:
        list_of_missing_files = [(os.path.basename(DATABASE[entry][0]), entry)
                                 for entry in DATABASE]
        if list_of_missing_files:
            list_of_missing_files.sort()
            with open(MISSING_FILES, "w") as missing_files:
                for missing_file, entry in list_of_missing_files:
                    print(missing_file, entry, sep = "\t", file=missing_files)
        else:
            print("no missing file")

    COVERAGE = round(100.0 * FOUND_ENTRIES / NUMBER_OF_ENTRIES, 2)
    print('coverage: {}/{} ({}%)'.format(FOUND_ENTRIES, NUMBER_OF_ENTRIES, COVERAGE),
          file=sys.stdout)

sys.exit(0)
