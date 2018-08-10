#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graphical User Iterface for build_pack and parse_pack scripts.
"""


from tkinter import *
from tkinter import filedialog as fd
import os


__author__ = "aleyr"
__date__ = "2018/08/09"
__version__ = "$Revision: 0.8"


def select_folder(directory, title):
    path = fd.askdirectory(initialdir=os.getcwd(), title=title)
    if path:
        directory.set(path)


def select_file_open(filename, title):
    path = fd.askopenfilename(initialdir=os.getcwd(), title=title)
    if path:
        filename.set(path)


def select_file_save(filename, title):
    path = fd.asksaveasfilename(initialdir=os.getcwd(), title=title)
    if path:
        filename.set(path)


def create_command(folder=None, output=None, input_folder=None,
                   database=None, output_folder=None, missing=None,
                   file_strategy=None, skip_eisting=None):
    cmd = sys.executable
    if folder:
        cmd += " " + os.path.join(os.getcwd(), "parse_pack.py")
        cmd += " -f \"" + folder + "\""
        cmd += " -o \"" + output + "\""
    else:
        cmd += " " + os.path.join(os.getcwd(), "build_pack.py")
        cmd += " -i " + input_folder
        cmd += " -d " + database
        cmd += (" -o " + output_folder) if output_folder else ""
        cmd += (" -m " + missing) if missing else ""
        if file_strategy == 0:
            cmd += " --file_strategy copy"
        else:
            cmd += " --file_strategy hardlink"
        cmd += " --skip_existing" if skip_eisting else ""

    # cmd += "\n\n\nExecute above command on the folder where the script "
    # cmd += "is located."

    return cmd


def create_command_array(folder=None, output=None, input_folder=None,
                         database=None, output_folder=None, missing=None,
                         file_strategy=None, skip_eisting=None):
    # cmd = ["cmd", "/k", sys.executable]
    cmd = [sys.executable]
    if folder:
        cmd.append(os.path.join(os.getcwd(), "parse_pack.py"))
        cmd.append("-f")
        cmd.append(folder)
        cmd.append("-o")
        cmd.append(output)
    else:
        cmd.append(os.path.join(os.getcwd(), "build_pack.py"))
        cmd.append("-i")
        cmd.append(input_folder)
        cmd.append("-d")
        cmd.append(database)
        cmd.append("-o")
        cmd.append(output_folder)
        cmd.append("-m")
        cmd.append(missing)
        if file_strategy == 0:
            cmd.append("--file_strategy")
            cmd.append("copy")
        else:
            cmd.append("--file_strategy")
            cmd.append("hardlink")
        if skip_eisting:
            cmd.append("--skip_existing")

    return cmd


def iter_except(function, exception):
    """Works like builtin 2-argument `iter()`, but stops on `exception`."""
    try:
        while True:
            yield function()
    except exception:
        return
