#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graphical User Iterface for build_pack and parse_pack scripts.
"""


import tkinter as tk
from tkinter import *


__author__ = "aleyr"
__date__ = "2018/08/09"
__version__ = "$Revision: 0.3"


class MenuBar(tk.Menu):
    def __init__(self, parent, *args, **kwargs):
        tk.Menu.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        file_menu = tk.Menu(self, tearoff=0)
        help_menu = tk.Menu(self, tearoff=0)

        file_menu.add_command(label="Exit",
                              command=self.parent.destroy)
        self.add_cascade(label="File", menu=file_menu)

        help_menu.add_command(label="About",
                              command=lambda:
                              TextMessage().about())
        self.add_cascade(label="Help", menu=help_menu)
