#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graphical User Iterface for build_pack and parse_pack scripts.
"""

from tkinter import *
from tkinter import ttk

from utils import *
from buildframe import *
from parseframe import *
from menubar import *
from textmessage import *
from autoresized_notebook import Autoresized_Notebook


__author__ = "aleyr"
__date__ = "2018/08/03"
__version__ = "$Revision: 0.8"


# *********************************************************************#
#                                                                      #
#                             Classes                                  #
#                                                                      #
# *********************************************************************#


class App(Tk):
    def __init__(self, *args, **kwargs):
        # call the parent constructor
        Tk.__init__(self, *args, **kwargs)

        self.text_label = StringVar()
        # self.text_label.set("123456790")

        tab_control = Autoresized_Notebook(self)

        build_frame = BuildFrame(self, padding="3 3 12 12")
        build_frame.pack(side="top", fill="both", expand=True)
        tab_control.add(build_frame, text="Build Pack", sticky=N)

        parse_frame = ParseFrame(self, padding="3 3 12 12")
        parse_frame.pack(side="top", fill="both", expand=True)
        tab_control.add(parse_frame, text="Parse ROMs Folder", sticky=N)

        tab_control.pack(side="top", fill="both", expand=True)

        # status_frame = ttk.Frame(self, padding="3 3 3 3")
        status_label = ttk.Label(self, borderwidth=2, relief="ridge",
                                 textvariable=self.text_label)
        status_label.pack(fill="both", expand=True)
        # status_frame.pack(fill="both", expand=True)

        self.progress = ttk.Progressbar(self, orient="horizontal",
                                        mode="determinate")
        self.progress.pack(fill="both", expand=True)

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
