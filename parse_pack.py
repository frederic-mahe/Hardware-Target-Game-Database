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
    # list folders to exclude
    banned = ["/MEGA/", "/EDMD/", "/EDFC/", "/EDGB/",
              "/SYSTEM/", "/PALETTE/", "/PATTERN/",
              "/SPED/", "/TBED/", "/TEXT/", "/SNAP/",
              "/sd2snes/", "/sd2snes Themes/", "/Firmware Backup/",
              "/Images/", "/Manuals/", "/System Test Images/", "/menu/",
              "/_PREVIEW/", "/Documentation/", "/SOUNDS/", "/ED64/",
              "/SAVE/", "/AUTO/", "/CPAK/", "/GBASYS/",
              "menu.bin", "OS.PCE", "FlashBoy 2010-11-02.exe",
              "FlashBoy Manual.7z", ".png"]
    with open(output_file, "w") as output_file:
        for dirpath, dirnames, filenames in os.walk(target_folder):
            if filenames:
                for f in filenames:
                    filename = os.path.join(os.path.normpath(dirpath), f)
                    absolute_filename = os.path.abspath(filename)
                    os.path.isfile(absolute_filename)
                    # convert to Unix format by default
                    filename = filename.replace("\\", "/")
                    h = hashlib.sha256()
                    # exclude certain folders
                    if not any(s in filename for s in banned):
                        try:
                            with open(absolute_filename, "rb", buffering=0) as f:
                                # use a small buffer to compute hash
                                # values to avoid memory overload
                                for b in iter(lambda : f.read(128 * 1024), b''):
                                    h.update(b)
                        except FileNotFoundError:
                            # Windows' default API is limited to paths of 260 characters
                            absolute_filename = u'\\\\?\\' + absolute_filename
                            with open(absolute_filename, "rb", buffering=0) as f:
                                for b in iter(lambda : f.read(128 * 1024), b''):
                                    h.update(b)
                        print(h.hexdigest(), filename, sep="\t", file=output_file)
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
