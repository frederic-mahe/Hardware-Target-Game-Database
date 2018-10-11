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
from collections import defaultdict
from glob import glob



__author__ = "aquaman"
__date__ = "2017/11/17"
__version__ = "$Revision: 3.1"


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
                        required=False,
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
                        choices=["copy", "hardlink"],
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

    # Valid uses of this flag include: -l, -l true, -l yes, --new_line=1
    parser.add_argument("-l", "--new_line",
                        dest="new_line",
                        default=False,
                        # nargs and const below allow us to accept the
                        # zero-argument form of --skip_existing
                        nargs="?",
                        const=True,
                        type='bool',
                        help=("Changes the way the stdout is printed, and "
                              "allows for UI subprocess monitoring."))

    ARGS = parser.parse_args()


def copy_file(source, dest):
    """Get a file from source to destination, with a configurable strategy.

    This method makes a file at source additionally appear at dest. The way
    this is accomplished is controlled via the --file_strategy command.

    Args:
      source - The file to copy/hardlink
      dest - The destination that the new file should appear at
    """
    if ARGS.file_strategy == "copy":
        copy_fn = shutil.copyfile
    elif ARGS.file_strategy == "hardlink":
        copy_fn = os.link
    else:
        raise Exception("Unknown copy strategy {}".format(ARGS.file_strategy))

    try:
        # copy the file to the new directory
        copy_fn(source, dest)
    except FileNotFoundError:
        # Windows' default API is limited to paths of 260 characters
        fixed_dest = u'\\\\?\\' + os.path.abspath(dest)
        copy_fn(source, fixed_dest)


def parse_database(target_database=None):
    """
    store hash values and filenames in a database.
    """
    db = defaultdict(list)
    number_of_entries = 0

    if not target_database:
        target_database = [l for f in glob('./EverDrive Pack SMDBs/*.txt') for l in open(os.path.abspath(f))]
    else:
        target_database = [l for l in open(target_database)]

    for line in target_database:
        hash_value, filename, other_hash = line.strip().split("\t", 2)
        number_of_entries += 1
        db[hash_value].append(filename)

    return db, number_of_entries


def print_progress(current, end):
    print_function("processing file: {:>9}".format(current), end=end)


def print_function(text, end, file=sys.stdout, flush=True):
    print(text, end=end, file=file, flush=flush)


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
                        for b in iter(lambda: f.read(128 * 1024), b''):
                            h.update(b)
                except FileNotFoundError:
                    with open(absolute_filename, "rb", buffering=0) as f:
                        # use a small buffer to compute hash to
                        # avoid memory overload
                        for b in iter(lambda: f.read(128 * 1024), b''):
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
                print_progress(i, END_LINE)
    else:
        print_progress(i, END_LINE)

    return found_entries


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
    DATABASE, NUMBER_OF_ENTRIES = parse_database(TARGET_DATABASE)
    FOUND_ENTRIES = parse_folder(SOURCE_FOLDER, DATABASE, OUTPUT_FOLDER)
    if MISSING_FILES:
        list_of_missing_files = [(os.path.basename(DATABASE[entry][0]), entry)
                                 for entry in DATABASE]
        if list_of_missing_files:
            list_of_missing_files.sort()
            with open(MISSING_FILES, "w") as missing_files:
                for missing_file, entry in list_of_missing_files:
                    print(missing_file, entry, sep="\t", file=missing_files)
        else:
            print("no missing file")

    COVERAGE = round(100.0 * FOUND_ENTRIES / NUMBER_OF_ENTRIES, 2)
    if not ARGS.new_line:
        print('coverage: {}/{} ({}%)'.format(FOUND_ENTRIES,
                                             NUMBER_OF_ENTRIES,
                                             COVERAGE),
              file=sys.stdout)

    sys.exit(0)
