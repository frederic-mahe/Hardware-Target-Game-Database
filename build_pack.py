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

def option_parse():
    """
    Parse arguments from command line.
    """
    parser = argparse.ArgumentParser(description="use a database to identify and organize files.")

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
    
    args = parser.parse_args()
    return args.source_folder, args.target_database, args.output_folder, args.missing_files


def parse_database(target_database):
    """
    store hash values and filenames in a database.
    """
    db = dict()
    with open(target_database, "r") as target_database:
        number_of_entries = 0
        for line in target_database:
            hash_value, filename = line.strip().split("\t", 1)
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
                        try:
                            # copy the file to the new directory
                            shutil.copyfile(filename,
                                            os.path.join(output_folder,
                                                         entry))
                        except FileNotFoundError:
                            # Windows' default API is limited to paths of 260 characters
                            new_file = u'\\\\?\\' + os.path.abspath(os.path.join(output_folder, entry))
                            shutil.copyfile(absolute_filename, new_file)
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

    SOURCE_FOLDER, TARGET_DATABASE, OUTPUT_FOLDER, MISSING_FILES = option_parse()
    DATABASE, NUMBER_OF_ENTRIES = parse_database(TARGET_DATABASE)
    FOUND_ENTRIES = parse_folder(SOURCE_FOLDER, DATABASE, OUTPUT_FOLDER)
    if MISSING_FILES:
        list_of_missing_files = [os.path.basename(DATABASE[entry][0])
                                 for entry in DATABASE]
        if list_of_missing_files:
            list_of_missing_files.sort()
            with open(MISSING_FILES, "w") as missing_files:
                for missing_file in list_of_missing_files:
                    print(missing_file, file=missing_files)
        else:
            print("no missing file")
    COVERAGE = round(100.0 * FOUND_ENTRIES / NUMBER_OF_ENTRIES, 2)
    print("coverage is ", COVERAGE, "%", sep="")

sys.exit(0)
