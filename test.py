#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graphical User Iterface for build_pack and parse_pack scripts.
"""
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import os


__author__ = "aleyr"
__date__ = "2018/08/03"
__version__ = "$Revision: 0.1"


# *********************************************************************#
#                                                                      #
#                            Functions                                 #
#                                                                      #
# *********************************************************************#

def calculate(*args):
    try:
        value = float(feet.get())
        meters.set((0.3048 * value * 10000.0 + 0.5) / 10000.0)
    except ValueError:
        pass


def select_folder(directory, title):
    directory = filedialog.askdirectory(initialdir=os.getcwd(), title=title)
    # directory_wrp[0] = filedialog.askdirectory(initialdir=os.getcwd(),
    #                                            title=title)
    print(directory_wrp[0])
    # return directory


def select_file_open(filename, title):
    filename = filedialog.askopenfilename(initialdir=os.getcwd(), title=title)
    # filename_wrp[0] = filedialog.askopenfilename(initialdir=os.getcwd(),
    #                                              title=title)
    print(filename_wrp[0])
    # return filename


def select_file_save(filename, title):
    filename = filedialog.asksaveasfilename(initialdir=os.getcwd(),
                                            title=title)
    print(filename)
    return filename


# *********************************************************************#
#                                                                      #
#                              Body                                    #
#                                                                      #
# *********************************************************************#

if __name__ == '__main__':
    root = Tk()
    root.title("EverDrive-Packs-Lists-Database")

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    root.path_dir_roms = StringVar()
    root.path_pack_file = StringVar()
    root.path_dir_pack = StringVar()
    root.path_missing_file = StringVar()
    root.file_strategy = StringVar()
    root.overwrite = BooleanVar()

    # ROMs directory
    textbox_roms = Entry(mainframe, textvariable=root.path_dir_roms)
    textbox_roms.grid(column=2, row=1, sticky=E)
    # textbox_roms.pack(pady=10, padx=10)
    ttk.Label(mainframe, text="ROMs folder: ").grid(column=1, row=1, sticky=E)
    ttk.Button(mainframe, text="Browse",
               command=lambda:
               select_folder([root.path_dir_roms], "Select ROMs folder")
               ).grid(column=3, row=1, sticky=W)

    # Pack file
    textbox_pack_file = Entry(mainframe, textvariable=root.path_pack_file)
    textbox_pack_file.grid(column=2, row=2, sticky=E)
    # textbox_roms.pack(pady=10, padx=10)
    ttk.Label(mainframe, text="SMDB/pack file: ").grid(column=1, row=2,
                                                       sticky=E)
    ttk.Button(mainframe, text="Browse",
               command=lambda:
               select_file_open([root.path_pack_file], "Select SMDB/pack file")
               ).grid(column=3, row=2, sticky=W)

    textbox_roms.focus_set()

    # feet = StringVar()
    # meters = StringVar()

    # feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
    # feet_entry.grid(column=2, row=1, sticky=(W, E))

    # ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2,
    #                                                sticky=(W, E))

    # ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
    # ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2,
    #                                                    sticky=E)
    # ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)
    # ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3,
    #                                                                 row=3,
    #                                                                 sticky=W)

    # for child in mainframe.winfo_children():
    #     child.grid_configure(padx=5, pady=5)

    # feet_entry.focus()
    # root.bind('<Return>', calculate)

    root.mainloop()
