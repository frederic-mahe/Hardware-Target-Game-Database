#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graphical User Iterface for build_pack and parse_pack scripts.
"""
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import os
from subprocess import Popen, PIPE
from threading import Thread
from queue import Queue, Empty

from utils import *
from buildframe import *
from parseframe import *
from menubar import *
from textmessage import *
from autoresized_notebook import Autoresized_Notebook


__author__ = "aleyr"
__date__ = "2018/08/03"
__version__ = "$Revision: 0.3"


# *********************************************************************#
#                                                                      #
#                             Classes                                  #
#                                                                      #
# *********************************************************************#


class App(Tk):
    def __init__(self, *args, **kwargs):
        # call the parent constructor
        Tk.__init__(self, *args, **kwargs)

        tab_control = Autoresized_Notebook(self)

        build_frame = BuildFrame(self, padding="3 3 12 12")
        build_frame.pack(side="top", fill="both", expand=True)
        tab_control.add(build_frame, text="Build Pack", sticky=N)

        parse_frame = ParseFrame(self, padding="3 3 12 12")
        parse_frame.pack(side="top", fill="both", expand=True)
        tab_control.add(parse_frame, text="Parse ROMs Folder", sticky=N)

        tab_control.pack(side="top", fill="both", expand=True)

        self.progress = ttk.Progressbar(self, orient="horizontal", 
                                        mode="indeterminate")
        self.progress.pack(fill="both", expand=True)
        # self.progress["maximum"] = -1

        menu_bar = MenuBar(self)

        self.config(menu=menu_bar)


# *********************************************************************#
#                                                                      #
#                            Functions                                 #
#                                                                      #
# *********************************************************************#


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
