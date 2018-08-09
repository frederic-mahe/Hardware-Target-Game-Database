#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
for a given folder, produce a list of file names with relative
paths and hash values.
"""
import os
import sys
import time
import zlib
import hashlib
import argparse
import logging


__author__ = "aquaman"
__date__ = "2018/01/22"
__version__ = "$Revision: 4.0"


# *********************************************************************#
#                                                                      #
#                            Functions                                 #
#                                                                      #
# *********************************************************************#

def option_parse():
    """
    Parse arguments from command line.
    """
    parser = argparse.ArgumentParser(
        description="list file names and produce hash values.")

    parser.add_argument("-f", "--folder",
                        dest="target_folder",
                        required=True,
                        help="set target folder")

    parser.add_argument("-o", "--output",
                        dest="output_file",
                        required=True,
                        help="set output file")

    args = parser.parse_args()
    return args.target_folder, args.output_file


def parse_folder(target_folder, output_file, progress_function=None):
    """
    read each file and produce a hash value.
    """
    # list folders and files to exclude
    banned_folders = ("/AUTO/", "/CPAK/",
                      "/Documentation/", "/ED64/",
                      "/EDFC/", "/EDGB/",
                      "/EDMD/", "/Extended SSF Dev Demo Sample - Krikzz/src/",
                      "/Firmware Backup/", "/GBASYS/",
                      "/Images/", "/MEGA/",
                      "/Manuals/", "/PALETTE/",
                      "/PATTERN/", "/SAVE/",
                      "/SNAP/", "/SOUNDS/",
                      "/SPED/", "/SYSTEM/",
                      "/System Test Images/",
                      "/TBED/", "/TEXT/",
                      "/_PREVIEW/", "/menu/",
                      "/ntm_firmware_ver", "/sd2snes Themes/",
                      "/sd2snes/")
    banned_suffixes = (".001", ".002", ".003", ".004", ".005", ".006",
                       ".007", ".008", ".009", ".7z", ".aps", ".asm",
                       ".bak", ".bat", ".bsa", ".bps", ".BPS",
                       ".bst", ".c", ".cht", ".dat", ".db", ".docx",
                       ".exe", ".ips", ".jpg", ".json", ".mso",
                       ".ods", ".odt", ".pc", ".pdf", ".png", ".sav", ".srm",
                       ".sto", ".txt", ".xdelta", ".xls", ".zip",
                       "OS.PCE", "Thumbs.db", "menu.bin")
    with open(output_file, "w") as output_file:
        i = 0
        # make sure subfolders are alphanumerically sorted
        sorted_files = sorted(os.walk(target_folder))
        # files_total = len(sorted_files)
        for dirpath, dirnames, filenames in sorted_files:
            if filenames:
                # make sure files are alphanumerically sorted
                filenames.sort()
                for f in filenames:
                    filename = os.path.join(os.path.normpath(dirpath), f)
                    absolute_filename = os.path.abspath(filename)
                    os.path.isfile(absolute_filename)
                    # convert to Unix format by default
                    filename = filename.replace("\\", "/")
                    # Report filenames with non-ASCII characters
                    try:
                        filename.encode('ascii')
                    except UnicodeEncodeError:
                        # logging.error("Error (non-ASCII character):",
                        #               filename)
                        print("Error (non-ASCII character):", filename,
                              file=sys.stdout)
                        time.sleep(10)  # alternatively: sys.exit(1)
                    sha256 = hashlib.sha256()
                    sha1 = hashlib.sha1()
                    md5 = hashlib.md5()
                    crc = 0
                    # exclude certain folders and files
                    if not (any(s in filename for s in banned_folders) or
                            filename.endswith(banned_suffixes)):
                        try:
                            with open(absolute_filename,
                                      "rb",
                                      buffering=0) as f:
                                # use a small buffer to compute hash
                                # values to avoid storing large files
                                # in memory (changing buffer size does
                                # not change parsing speed much)
                                for b in iter(lambda: f.read(128 * 1024), b''):
                                    sha256.update(b)
                                    sha1.update(b)
                                    md5.update(b)
                                    crc = zlib.crc32(b, crc)
                        except FileNotFoundError:
                            # Windows default API is limited to paths of
                            # 260 characters
                            absolute_filename = u'\\\\?\\' + absolute_filename
                            with open(absolute_filename,
                                      "rb",
                                      buffering=0) as f:
                                for b in iter(lambda: f.read(128 * 1024), b''):
                                    sha256.update(b)
                                    sha1.update(b)
                                    md5.update(b)
                                    crc = zlib.crc32(b, crc)
                        print(sha256.hexdigest(),
                              filename,
                              sha1.hexdigest(),
                              md5.hexdigest(),
                              hex(crc & 0xffffffff)[2:],
                              sep="\t",
                              file=output_file)
                        i += 1
                        # logging.info("processing file: {:>9}".format(i))
                        print_progress(i)
                        # print("processing/ file: {:>9}".format(i),
                        #       end="\r",
                        #       file=sys.stdout,
                        #       flush=True)
        else:
            print_progress(i)
            # print('processing file: {:>9}'.format(i), file=sys.stdout)
            # logging.info("processing file: {:>9}".format(i))

    return None


def print_progress2(current, total):
    print("{:>9}/{:>9}".format(current, total),
          end="\r", file=sys.stdout, flush=True)


def print_progress(current):
    print("processing/ file: {:>9}".format(current),
          file=sys.stdout, flush=True)


# *********************************************************************#
#                                                                      #
#                              Body                                    #
#                                                                      #
# *********************************************************************#

if __name__ == '__main__':

    TARGET_FOLDER, OUTPUT_FILE = option_parse()
    if os.path.lexists(TARGET_FOLDER):
        TARGET_FOLDER = os.path.normpath(TARGET_FOLDER)
        parse_folder(TARGET_FOLDER, OUTPUT_FILE)

    sys.exit(0)
