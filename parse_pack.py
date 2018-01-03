#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
for a given folder, produce a list of file names with relative
paths and hash values.
"""

__author__ = "aquaman"
__date__ = "2017/11/17"
__version__ = "$Revision: 3.1"


import os
import sys
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
    parser = argparse.ArgumentParser(description="list file names and produce hash values.")

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


def parse_folder(target_folder, output_file):
    """
    read each file and produce a hash value.
    """
    # list folders and files to exclude
    banned_folders = ("/AUTO/", "/CPAK/", "/Documentation/", "/ED64/", "/EDFC/",
                      "/EDGB/", "/EDMD/",
                      "/Extended SSF Dev Demo Sample - Krikzz/src/",
                      "/Firmware Backup/", "/GBASYS/",
                      "/Images/", "/MEGA/", "/Manuals/", "/PALETTE/",
                      "/PATTERN/", "/SAVE/", "/SNAP/", "/SOUNDS/",
                      "/SPED/", "/SYSTEM/", "/System Test Images/",
                      "/TBED/", "/TEXT/", "/_PREVIEW/", "/menu/",
                      "/ntm_firmware_ver", "/sd2snes Themes/", "/sd2snes/")
    banned_suffixes = (".7z", ".aps", ".asm", ".bps", ".BPS", ".c",
                       ".dat", ".db", ".exe", ".ips", ".jpg", ".mso",
                       ".ods", ".odt", ".pc", ".png", ".sav", ".srm",
                       ".sto", ".txt", ".zip", "OS.PCE", "Thumbs.db",
                       "menu.bin")
    with open(output_file, "w") as output_file:
        i = 0
        # make sure subfolders are alphanumerically sorted
        for dirpath, dirnames, filenames in sorted(os.walk(target_folder)):
            if filenames:
                # make sure files are alphanumerically sorted
                filenames.sort()                
                for f in filenames:
                    filename = os.path.join(os.path.normpath(dirpath), f)
                    absolute_filename = os.path.abspath(filename)
                    os.path.isfile(absolute_filename)
                    # convert to Unix format by default
                    filename = filename.replace("\\", "/")
                    h = hashlib.sha256()
                    # exclude certain folders and files
                    if not (any(s in filename for s in banned_folders) or filename.endswith(banned_suffixes)):
                        try:
                            with open(absolute_filename, "rb", buffering=0) as f:
                                # use a small buffer to compute hash
                                # values to avoid storing large files
                                # in memory (changing buffer size does
                                # not change parsing speed much)
                                for b in iter(lambda : f.read(128 * 1024), b''):
                                    h.update(b)
                        except FileNotFoundError:
                            # Windows' default API is limited to paths of 260 characters
                            absolute_filename = u'\\\\?\\' + absolute_filename
                            with open(absolute_filename, "rb", buffering=0) as f:
                                for b in iter(lambda : f.read(128 * 1024), b''):
                                    h.update(b)
                        print(h.hexdigest(), filename, sep="\t", file=output_file)
                        i += 1
                        print("processing file: {:>9}".format(i),
                              end="\r", file=sys.stdout, flush=True)
        else:
            print('processing file: {:>9}'.format(i), file=sys.stdout)

    return None


#**********************************************************************#
#                                                                      #
#                              Body                                    #
#                                                                      #
#**********************************************************************#

if __name__ == '__main__':

    TARGET_FOLDER, OUTPUT_FILE = option_parse()
    if os.path.lexists(TARGET_FOLDER):
        TARGET_FOLDER = os.path.normpath(TARGET_FOLDER)
        parse_folder(TARGET_FOLDER, OUTPUT_FILE)


sys.exit(0)
