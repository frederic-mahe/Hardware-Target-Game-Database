#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game backup basic sorter.
"""
import argparse
import shutil
import os
import re
import sys

__author__ = "BuraBure"
__date__ = "2022/05/16"
__version__ = "$Revision: 1.0"


# *********************************************************************#
#                                                                      #
#                            CONSTANTS                                 #
#                                                                      #
# *********************************************************************#

REVISION_REGEX = ' \(Rev(\s\d)?\)'
REVISIONS_DIR = '4 Beta, Prototypes, Revisions/Revisions/'
BETAS_REGEX = ' \(Beta(\s\d)?\)'
BETAS_DIR = '4 Beta, Prototypes, Revisions/Betas/'
DEMOS_REGEX = ' \(Demo(\s\d)?\)'
DEMOS_DIR = '4 Beta, Prototypes, Revisions/Samples/'
USA_REGEX = ' \([^\)]*USA[^\)]*\)'
USA_TMP_DIR = '1 USA - TMP/'
JAPAN_REGEX = ' \([^\)]*Japan[^\)]*\)'
JAPAN_DIR = '2 Japan - A-Z/'
EUROPE_REGEX = ' \([^\)]*Europe[^\)]*\)'
EUROPE_DIR = '2 Europe - A-Z/'
OTHERS_DIR = '2 Other Regions - A-Z/'
DISC_REGEX = '(^.*)\s\(Disc \d\)'
RESERVED_DIRS = [
    '^1 USA',
    '^2 Japan',
    '^2 Europe',
    '^2 Other Regions',
    '^2 Unlicensed',
    '^4 Beta, Prototypes, Revisions',
    '^4 Game Series Collection',
    '^4 Hacks',
    '^4 Homebrew',
    '^4 Translations',
    '^5 Tools & Service Test Carts',
]

blue = "\x1b[94;20m"
green = "\x1b[92;20m"
reset = "\x1b[0m"


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
        description="Game backup basic sorting.")

    # Add support for boolean arguments. Allows us to accept 1-argument forms
    # of boolean flags whose values are any of "yes", "true", "t" or "1".
    parser.register('type', 'bool', (lambda x: x.lower() in
                                     ("yes", "true", "t", "1")))

    parser.add_argument("--debug",
                        dest="debug",
                        required=False,
                        nargs="?",
                        const=True,
                        type='bool',
                        help="debug output")

    parser.add_argument("-d", "--discs",
                        dest="discs",
                        required=False,
                        nargs="?",
                        const=True,
                        type='bool',
                        help="put discs into folders")

    parser.add_argument("-i", "--input_folder",
                        dest="source_dir",
                        required=True,
                        help="set source dir")

    parser.add_argument("-g", "--alphabetical_group_min_count",
                        dest="alphabetical_group_min_count",
                        required=False,
                        default=149,
                        help="the minimun file count for the alphabetical group dirs")

    parser.add_argument("-t", "--file_type",
                        dest="file_type",
                        required=False,
                        default=None,
                        help="only operate on a certain file type")

    ARGS = parser.parse_args()


def debug_banner(msg):
    if DEBUG:
        print(green, '============================', reset)
        print(green, '+', msg.center(24, ' '), '+', reset)
        print(green, '============================', reset)


def get_file_list(dir):
    files = sorted(os.listdir(dir), key=str.lower)
    reserved_dir_regex = '|'.join(RESERVED_DIRS)
    safe_files = filter(lambda file: False if re.search(
        reserved_dir_regex, file) else True, files)

    if FILE_TYPE == None:
        return safe_files
    else:
        return filter(lambda file: True if re.search(FILE_TYPE + '$', file) else False, safe_files)


def move_files(file_list, destination, process_discs=False):
    """
    Moves a list of files to a destination
    """
    if process_discs:
        move_disc_files(file_list, destination)
        return

    __move_files(file_list, destination)


def __move_files(file_or_file_list, destination):
    for file in file_or_file_list if isinstance(file_or_file_list, list) else [file_or_file_list]:
        result_path = shutil.move(file, destination)
        if DEBUG:
            print('Moved: "', reset, blue, file, reset, '" => "',
                  reset, blue, result_path, reset, '"', reset, sep='')


def move_disc_files(file_list, destination):
    """
    Groups discs into folders and Moves them to a destination
    """
    for file in file_list:
        (_, filename) = os.path.split(file)
        (extensionless, _) = os.path.splitext(filename)
        discless_match = re.search(DISC_REGEX, filename)
        discless_name = discless_match.group(
            1) if discless_match != None else extensionless
        disc_dir = os.path.join(destination, discless_name)
        os.makedirs(disc_dir, mode=511, exist_ok=True)
        __move_files(file, disc_dir)


def is_revision(prev_file, curr_file):
    return re.sub(REVISION_REGEX, '', prev_file) == re.sub(REVISION_REGEX, '', curr_file)


def get_earlier_revision(file_a, file_b):
    """
    Returns filepath that is the lower/earliest revision
    """
    rev_a_match = re.search(REVISION_REGEX, file_a)
    rev_b_match = re.search(REVISION_REGEX, file_b)

    rev_a = int(rev_a_match.group(1)) if rev_a_match != None else 0
    rev_b = int(rev_b_match.group(1)) if rev_b_match != None else 0

    if rev_a < rev_b:
        return file_a
    else:
        return file_b


def move_revisions(source_dir):
    """
    Moves all early revisions to the revisions dir
    """
    files = get_file_list(source_dir)
    prev_file = ''
    early_revisions = []
    revisions_dir = os.path.abspath(
        os.path.join(source_dir, REVISIONS_DIR))

    for file in files:
        file_abs = os.path.join(source_dir, file)
        if is_revision(prev_file, file_abs):
            early_revisions.append(
                get_earlier_revision(prev_file, file_abs))
        prev_file = file_abs

    os.makedirs(revisions_dir, mode=511, exist_ok=True)
    move_files(early_revisions, revisions_dir, DISCS)


def is_beta(file):
    return True if re.search(BETAS_REGEX, file) != None else False


def is_demo(file):
    return True if re.search(DEMOS_REGEX, file) != None else False


def is_USA(file):
    return True if re.search(USA_REGEX, file) != None else False


def is_Japan(file):
    return True if re.search(JAPAN_REGEX, file) != None else False


def is_Europe(file):
    return True if re.search(EUROPE_REGEX, file) != None else False


def is_other_regions(file):
    return False if is_USA(file) | is_Japan(file) | is_Europe(file) else True


def move_files_conditionally(source_dir, destination_dir, predicate_fn):
    """
    Moves files to destination if the predicate returns true
    """
    files = get_file_list(source_dir)
    abs_paths = []

    os.makedirs(destination_dir, mode=511, exist_ok=True)

    for file in files:
        file_abs = os.path.join(source_dir, file)
        if predicate_fn(file_abs):
            abs_paths.append(file_abs)

    move_files(abs_paths, destination_dir, DISCS)


def move_alphabetical_batch(batch, base_dir, dir_prefix, batch_starting_letter, batch_ending_letter):
    batch_dir_name = dir_prefix + ' - ' + \
        batch_starting_letter + '-' + batch_ending_letter

    batch_dir_path = os.path.abspath(
        os.path.join(base_dir, batch_dir_name))

    os.makedirs(batch_dir_path, mode=511, exist_ok=True)
    move_files(batch, batch_dir_path, False)


def group_files_alphabetically(base_dir, dir_prefix, destination_dir=None):
    """
    Groups files into alphabetical dirs
    """
    files = get_file_list(base_dir)
    batch = []
    prev_file_name = '0'
    batch_starting_letter = 'A'
    destination_dir = base_dir if destination_dir == None else destination_dir

    for file in files:
        file_abs = os.path.join(base_dir, file)
        if (len(batch) >= int(ALPHABETICAL_GROUP_MIN_COUNT)) & (prev_file_name.lower()[0] != file.lower()[0]):
            move_alphabetical_batch(
                batch, destination_dir, dir_prefix, batch_starting_letter, prev_file_name.upper()[0])
            batch = []
            batch_starting_letter = file.upper()[0]

        batch.append(file_abs)
        prev_file_name = file

    if len(batch) > 0:
        move_alphabetical_batch(
            batch, destination_dir, dir_prefix, batch_starting_letter, prev_file_name.upper()[0])


# *********************************************************************#
#                                                                      #
#                              Body                                    #
#                                                                      #
# *********************************************************************#

if __name__ == '__main__':
    DEBUG = ARGS.debug
    FILE_TYPE = ARGS.file_type
    ALPHABETICAL_GROUP_MIN_COUNT = ARGS.alphabetical_group_min_count
    DISCS = ARGS.discs
    SOURCE_DIR = os.path.abspath(ARGS.source_dir)

    debug_banner('MOVING REVISIONS')
    move_revisions(SOURCE_DIR)

    debug_banner('MOVING BETAS')
    move_files_conditionally(SOURCE_DIR, os.path.abspath(
        os.path.join(SOURCE_DIR, BETAS_DIR)), is_beta)

    debug_banner('MOVING DEMOS')
    move_files_conditionally(SOURCE_DIR, os.path.abspath(
        os.path.join(SOURCE_DIR, DEMOS_DIR)), is_demo)

    debug_banner('MOVING USA')
    move_files_conditionally(SOURCE_DIR, os.path.abspath(
        os.path.join(SOURCE_DIR, USA_TMP_DIR)), is_USA)

    debug_banner('MOVING JAPAN')
    move_files_conditionally(SOURCE_DIR, os.path.abspath(
        os.path.join(SOURCE_DIR, JAPAN_DIR)), is_Japan)

    debug_banner('MOVING EUROPE')
    move_files_conditionally(SOURCE_DIR, os.path.abspath(
        os.path.join(SOURCE_DIR, EUROPE_DIR)), is_Europe)

    debug_banner('MOVING OTHER REGIONS')
    move_files_conditionally(SOURCE_DIR, os.path.abspath(
        os.path.join(SOURCE_DIR, OTHERS_DIR)), is_other_regions)

    debug_banner('GROUPING USA')
    usa_tmp_dir_abs = os.path.join(SOURCE_DIR, USA_TMP_DIR)
    group_files_alphabetically(usa_tmp_dir_abs, '1 USA', SOURCE_DIR)
    os.rmdir(usa_tmp_dir_abs)

    debug_banner('GROUPING JAPAN')
    group_files_alphabetically(os.path.abspath(
        os.path.join(SOURCE_DIR, JAPAN_DIR)), 'Japan')

    debug_banner('GROUPING EUROPE')
    group_files_alphabetically(os.path.abspath(
        os.path.join(SOURCE_DIR, EUROPE_DIR)), 'Europe')

    debug_banner('GROUPING OTHER REGIONS')
    group_files_alphabetically(os.path.abspath(
        os.path.join(SOURCE_DIR, OTHERS_DIR)), 'Other Regions')

    sys.exit(0)
