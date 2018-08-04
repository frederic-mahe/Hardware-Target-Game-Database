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
#                             Classes                                  #
#                                                                      #
# *********************************************************************#

class ParseFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.path_dir_roms = StringVar()
        self.path_pack_file = StringVar()
        self.path_dir_pack = StringVar()
        self.path_missing_file = StringVar()
        self.file_strategy = StringVar()
        self.overwrite = BooleanVar()

        # ROMs directory
        textbox_roms = Entry(self, width=50, textvariable=self.path_dir_roms)
        textbox_roms.grid(column=2, row=1, sticky=E)
        # textbox_roms.pack(pady=10, padx=10)
        ttk.Label(self, text="ROMs folder: ").grid(column=1, row=1, sticky=E)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   select_folder(self.path_dir_roms,
                                 "Select ROMs folder")
                   ).grid(column=3, row=1, sticky=W)

        # Pack file
        textbox_pack_file = Entry(self, width=50,
                                  textvariable=self.path_pack_file)
        textbox_pack_file.grid(column=2, row=2, sticky=E)
        # textbox_roms.pack(pady=10, padx=10)
        ttk.Label(self, text="New pack file: ").grid(column=1, row=2,
                                                     sticky=E)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   select_file_save(self.path_pack_file,
                                    "Select SMDB/pack file")
                   ).grid(column=3, row=2, sticky=W)

        textbox_roms.focus_set()


class BuildFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.path_dir_roms = StringVar()
        self.path_pack_file = StringVar()
        self.path_dir_pack = StringVar()
        self.path_missing_file = StringVar()
        self.file_strategy = StringVar()
        self.overwrite = BooleanVar()

        # ROMs directory
        textbox_roms = Entry(self, width=50, textvariable=self.path_dir_roms)
        textbox_roms.grid(column=2, row=1, sticky=E)
        # textbox_roms.pack(pady=10, padx=10)
        ttk.Label(self, text="ROMs folder: ").grid(column=1, row=1, sticky=E)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   select_folder(self.path_dir_roms, "Select ROMs folder")
                   ).grid(column=3, row=1, sticky=W)

        # Pack file
        textbox_pack_file = Entry(self, width=50,
                                  textvariable=self.path_pack_file)
        textbox_pack_file.grid(column=2, row=2, sticky=E)
        # textbox_roms.pack(pady=10, padx=10)
        ttk.Label(self, text="SMDB/pack file: ").grid(column=1, row=2,
                                                      sticky=E)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   select_file_save(self.path_pack_file,
                                    "Select SMDB/pack file")
                   ).grid(column=3, row=2, sticky=W)

        textbox_roms.focus_set()


# Step 2: Creating The App
class App(Tk):
    def __init__(self, *args, **kwargs):
        # call the parent constructor
        Tk.__init__(self, *args, **kwargs)

        # show app frame
        self.appFrame = ParseFrame(self, padding="3 3 12 12")
        self.appFrame.pack(side="top", fill="both", expand=True)


# *********************************************************************#
#                                                                      #
#                            Functions                                 #
#                                                                      #
# *********************************************************************#

def select_folder(self, directory, tb, title):
    path = fd.askdirectory(initialdir=os.getcwd(), title=title)
    if path:
        directory.set(path)


def select_file_open(self, filename, title):
    path = fd.askopenfilename(initialdir=os.getcwd(), title=title)
    if path:
        filename.set(path)


def select_file_save(self, filename, title):
    path = fd.asksaveasfilename(initialdir=os.getcwd(), title=title)
    if path:
        filename.set(path)


# Step 3: Bootstrap the app
def main():
    app = App()
    app.title("EverDrive-Packs-Lists-Database")
    app.mainloop()

# *********************************************************************#
#                                                                      #
#                              Body                                    #
#                                                                      #
# *********************************************************************#


if __name__ == '__main__':
    main()
