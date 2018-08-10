#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graphical User Iterface for build_pack and parse_pack scripts.
"""


from tkinter import *
from tkinter import filedialog as fd
import os
from pathlib import Path


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
    # cmd = sys.executable
    # if folder:
    #     cmd += " " + os.path.join(os.getcwd(), "parse_pack.py")
    #     cmd += " -f \"" + folder + "\""
    #     cmd += " -o \"" + output + "\""
    # else:
    #     cmd += " " + os.path.join(os.getcwd(), "build_pack.py")
    #     cmd += " -i \"" + input_folder + "\""
    #     cmd += " -d " + database
    #     cmd += (" -o \"" + output_folder + "\"") if output_folder else ""
    #     cmd += (" -m \"" + missing + "\"") if missing else ""
    #     if file_strategy == 0:
    #         cmd += " --file_strategy copy"
    #     else:
    #         cmd += " --file_strategy hardlink"
    #     cmd += " --skip_existing" if skip_eisting else ""

    arr = create_command_array(folder=folder,
                               output=output,
                               input_folder=input_folder,
                               database=database,
                               output_folder=output_folder,
                               missing=missing,
                               file_strategy=file_strategy,
                               skip_eisting=skip_eisting,
                               new_line=False,
                               add_quotes=True)
    cmd = " ".join(arr)

    return cmd


def get_abs_path(path, add_quotes=False):
    out = os.path.abspath(str(path))
    if add_quotes:
        out = "\"" + out + "\""

    return out


def create_command_array(folder=None, output=None, input_folder=None,
                         database=None, output_folder=None, missing=None,
                         file_strategy=None, skip_eisting=None, new_line=True,
                         add_quotes=False):
    python_path = Path(sys.executable)
    current_dir = Path(os.getcwd())
    cmd = [get_abs_path(python_path, add_quotes)]
    if folder:
        cmd.append(get_abs_path(current_dir / "parse_pack.py", add_quotes))
        cmd.append("-f")
        cmd.append(get_abs_path(Path(folder), add_quotes))
        cmd.append("-o")
        cmd.append(get_abs_path(Path(output), add_quotes))
    else:
        cmd.append(get_abs_path(current_dir / "build_pack.py", add_quotes))
        cmd.append("-i")
        cmd.append(get_abs_path(Path(input_folder), add_quotes))
        cmd.append("-d")
        cmd.append(get_abs_path(Path(database), add_quotes))
        cmd.append("-o")
        cmd.append(get_abs_path(Path(output_folder), add_quotes))
        if missing and len(missing) > 0:
            cmd.append("-m")
            cmd.append(get_abs_path(Path(missing), add_quotes))
        if file_strategy == 0:
            cmd.append("--file_strategy")
            cmd.append("copy")
        else:
            cmd.append("--file_strategy")
            cmd.append("hardlink")
        if skip_eisting:
            cmd.append("--skip_existing")
        if new_line:
            cmd.append("--new_line")

    return cmd


def iter_except(function, exception):
    """Works like builtin 2-argument `iter()`, but stops on `exception`."""
    try:
        while True:
            yield function()
    except exception:
        return
