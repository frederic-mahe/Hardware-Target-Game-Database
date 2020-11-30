#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Use a database to verify files.
"""
import os
import sys
import hashlib
import argparse
from collections import defaultdict


__author__ = "Steve Matos (parts by aquaman)"
__date__ = "2020/11/28"
__version__ = "$Revision: 1.0"


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
        description="Use a database to verify files.")
    # Add support for boolean arguments. Allows us to accept 1-argument forms
    # of boolean flags whose values are any of "yes", "true", "t" or "1".
    parser.register('type', 'bool', (lambda x: x.lower() in
                                     ("yes", "true", "t", "1")))

    parser.add_argument("-f", "--folder",
                        dest="target_folder",
                        required=True,
                        help="set target folder")

    parser.add_argument("-d", "--database",
                        dest="target_database",
                        required=True,
                        help="set target database")

    parser.add_argument("-m", "--mismatch",
                        dest="mismatch_files",
                        default=None,
                        help="list mismatch files")

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


def parse_database(target_database, drop_initial_directory):
    """
    Store hash values and filenames in a database.
    """
    db = defaultdict(list)  # missing key's default value is an empty list
    number_of_entries = 0
    with open(target_database, "r") as target_database:
        for line in target_database:
            hash_sha256, filename, other_hash = line.strip().split("\t", 2)
            number_of_entries += 1

            if drop_initial_directory:
                first_level, filename = filename.split("/", 1)

            filename = os.path.normpath(filename)
            db[hash_sha256].append(filename)

    return db, number_of_entries


def print_progress(current, total, end):
    print_function("processing file: {:>9} / {}".format(current, total), end=end)


def print_function(text, end, file=sys.stdout, flush=True):
    print(text, end=end, file=file, flush=flush)


def parse_folder(target_folder, db):
    """
    Read each file, produce a hash value and determine if it is in the correct location.
    """
    current_file = 0
    total_files = len([os.path.join(dp, f) for dp, dn, fn in
                       os.walk(os.path.expanduser(target_folder)) for f in fn])

    bad_location_files = []
    extra_files = []
    for dirpath, dirnames, filenames in os.walk(target_folder):
        if filenames:
            for f in filenames:
                filename = os.path.join(os.path.normpath(dirpath),
                                        os.path.normpath(f))
                absolute_filename = u'\\\\?\\' + os.path.abspath(filename)
                try:
                    hash_sha256 = get_hash(filename)
                except FileNotFoundError:
                    hash_sha256 = get_hash(absolute_filename)

                if hash_sha256 in db:
                    rel_path = os.path.relpath(filename, target_folder)

                    if rel_path in db[hash_sha256]:
                        # file found (correct location)
                        # remove file name from database
                        db[hash_sha256].remove(rel_path)
                    else:
                        # hash in database (file in bad location)
                        bad_location_files.append((filename, hash_sha256))
                else:
                    # hash not in database (extra file)
                    extra_files.append((filename, hash_sha256))

                current_file += 1
                print_progress(current_file, total_files, END_LINE)
    else:
        if not ARGS.new_line:
            print_progress(current_file, total_files, "\n")

    return bad_location_files, extra_files


def get_hash(filename):
    """
    Return sha256 hash of the file.
    """
    h = hashlib.sha256()
    with open(filename, "rb", buffering=0) as f:
        # use a small buffer to compute hash to
        # avoid memory overload
        for b in iter(lambda: f.read(128 * 1024), b''):
            h.update(b)

    return h.hexdigest()


# *********************************************************************#
#                                                                      #
#                              Body                                    #
#                                                                      #
# *********************************************************************#

if __name__ == '__main__':
    TARGET_FOLDER = ARGS.target_folder
    TARGET_DATABASE = ARGS.target_database
    MISMATCH_FILES = ARGS.mismatch_files
    END_LINE = "\n" if ARGS.new_line else "\r"
    DROP_INITIAL_DIRECTORY = ARGS.drop_initial_directory

    DATABASE, NUMBER_OF_ENTRIES = parse_database(TARGET_DATABASE, DROP_INITIAL_DIRECTORY)
    BAD_LOCATION_FILES, EXTRA_FILES = parse_folder(TARGET_FOLDER, DATABASE)

    MISSING_FILES = []
    for key in DATABASE:
        for file in DATABASE[key]:
            MISSING_FILES.append((file, key))

    # write information to log file only if there are any bad, extra or missing files to report
    if MISMATCH_FILES and (BAD_LOCATION_FILES or EXTRA_FILES or MISSING_FILES):
        BAD_LOCATION_FILES.sort()
        EXTRA_FILES.sort()
        MISSING_FILES.sort()

        with open(MISMATCH_FILES, "w") as mismatch_files:
            if BAD_LOCATION_FILES:
                print("Incorrect Location Files:", file=mismatch_files)
                for file, hash_sha256 in BAD_LOCATION_FILES:
                    print(os.path.abspath(file), hash_sha256, sep="\t", file=mismatch_files)
                print("\n", file=mismatch_files)

            if EXTRA_FILES:
                print("Extra Files:", file=mismatch_files)
                for file, hash_sha256 in EXTRA_FILES:
                    print(os.path.abspath(file), hash_sha256, sep="\t", file=mismatch_files)
                print("\n", file=mismatch_files)

            if MISSING_FILES:
                print("Missing Files:", file=mismatch_files)
                for file, hash_sha256 in MISSING_FILES:
                    print(file, hash_sha256, sep="\t", file=mismatch_files)
                print("\n", file=mismatch_files)

    print("incorrect location: {}".format(len(BAD_LOCATION_FILES)), file=sys.stdout)
    print("extra: {}".format(len(EXTRA_FILES)), file=sys.stdout)
    print("missing: {}".format(len(MISSING_FILES)), file=sys.stdout)

    sys.exit(0)
