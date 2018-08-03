#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graphical User Iterface for build_pack and parse_pack scripts.
"""

__author__ = "aleyr"
__date__ = "2018/08/03"
__version__ = "$Revision: 0.1"


from tkinter import *
from tkinter import ttk


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

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    feet = StringVar()
    meters = StringVar()

    feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
    feet_entry.grid(column=2, row=1, sticky=(W, E))

    ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2,
                                                   sticky=(W, E))
    ttk.Button(mainframe, text="Calculate", command=calculate
               ).grid(column=3, row=3, sticky=W)

    ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
    ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2,
                                                       sticky=E)
    ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)

    feet_entry.focus()
    root.bind('<Return>', calculate)

    root.mainloop()
