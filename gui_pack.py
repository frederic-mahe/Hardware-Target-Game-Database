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

class AppFrame(ttk.Frame):
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
        textbox_roms = Entry(self, textvariable=self.path_dir_roms)
        textbox_roms.grid(column=2, row=1, sticky=E)
        # textbox_roms.pack(pady=10, padx=10)
        ttk.Label(self, text="ROMs folder: ").grid(column=1, row=1, sticky=E)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   self.select_folder(self.path_dir_roms,
                                      "Select ROMs folder")
                   ).grid(column=3, row=1, sticky=W)

        # Pack file
        textbox_pack_file = Entry(self, textvariable=self.path_pack_file)
        textbox_pack_file.grid(column=2, row=2, sticky=E)
        # textbox_roms.pack(pady=10, padx=10)
        ttk.Label(self, text="SMDB/pack file: ").grid(column=1, row=2, 
                                                      sticky=E)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   self.select_file_open(self.path_pack_file,
                                         "Select SMDB/pack file")
                   ).grid(column=3, row=2, sticky=W)

        textbox_roms.focus_set()

        # feet = StringVar()
        # meters = StringVar()

        # feet_entry = ttk.Entry(self, width=7, textvariable=feet)
        # feet_entry.grid(column=2, row=1, sticky=(W, E))

        # ttk.Label(self, textvariable=meters).grid(column=2, row=2,
        #                                                sticky=(W, E))

        # ttk.Label(self, text="feet").grid(column=3, row=1, sticky=W)
        # ttk.Label(self, text="is equivalent to").grid(column=1, row=2,
        #                                                    sticky=E)
        # ttk.Label(self, text="meters").grid(column=3, row=2, sticky=W)
        # ttk.Button(self, text="Calculate", command=calculate).grid(column=3,
        #                                                            row=3,
        #                                                            sticky=W)

        # for child in self.winfo_children():
        #     child.grid_configure(padx=5, pady=5)

        # feet_entry.focus()
        # slef.parent.bind('<Return>', calculate)

    def select_folder(self, directory, title):
        directory = fd.askdirectory(initialdir=os.getcwd(), title=title)
        # directory_wrp[0] = fd.askdirectory(initialdir=os.getcwd(),
        #                                            title=title)
        print(directory)
        # return directory

    def select_file_open(self, filename, title):
        filename = fd.askopenfilename(initialdir=os.getcwd(), title=title)
        # filename_wrp[0] = fd.askopenfilename(initialdir=os.getcwd(),
        #                                              title=title)
        print(filename)
        # return filename

    def select_file_save(self, filename, title):
        filename = fd.asksaveasfilename(initialdir=os.getcwd(), title=title)
        print(filename)
        return filename


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


# *********************************************************************#
#                                                                      #
#                              Body                                    #
#                                                                      #
# *********************************************************************#

if __name__ == '__main__':
    root = Tk()
    root.title("EverDrive-Packs-Lists-Database")

    mainframe = AppFrame(root, padding="3 3 12 12")

    root.mainloop()
