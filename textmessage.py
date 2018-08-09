#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graphical User Iterface for build_pack and parse_pack scripts.
"""


import tkinter as tk
from tkinter import *
from platform import system


__author__ = "aleyr"
__date__ = "2018/08/09"
__version__ = "$Revision: 0.3"


class TextMessage(object):

    def __init__(self):
        # Fonts
        if "Darwin" in system():
            #    print("\nOS X detected")
            self.fontsize = 12
            self.pad_radio = 3
            self.but_size = -2
            self.res_size = -1
        else:
            #    print("\nWindows detected")
            self.fontsize = 10
            self.pad_radio = 0
            self.but_size = -2
            self.res_size = -2

        self.fontz = {
             "bold": ("TkDefaultFont", self.fontsize, "bold"),
             "normal_small": ("TkDefaultFont",
                              self.fontsize + self.but_size, "normal"),
             "italic_small": ("TkDefaultFont",
                              self.fontsize + self.but_size, "italic")}

    def popup(self, title, message, size=10):
        top = tk.Toplevel()
        top.title(title)
        about_message = (message)
        top.lift()
        msg = tk.Text(top, width=90, font=('courier', size, 'normal'))
        msg.grid(stick=tk.N, padx=(10, 10), pady=(10, 10))
        msg.insert("1.0", about_message)
        button = tk.Button(top, height=1, width=20, text="OK", underline=0,
                           command=top.destroy, bg='gray97', relief=tk.GROOVE)
        button.grid(sticky=tk.S, pady=(0, 10))
        s = tk.Scrollbar(top, width=20)
        s.grid(row=0, column=0, sticky=E + N + S, padx=(0, 10), pady=(10, 10))
        s['command'] = msg.yview
        msg['yscrollcommand'] = s.set
        top.resizable(width=tk.FALSE, height=tk.FALSE)
        button.focus_set()
        top.bind("<Alt_L><o>", lambda e: top.destroy())
        top.bind('<Escape>', lambda e: top.destroy())

    def about(self):
        top = tk.Toplevel()
        top.title("About")
        top.lift()
        tk.Label(top,
                 text="""Smoke Monster Packs UI
       by Aleyr""",
                 justify=CENTER,
                 font=self.fontz["bold"]).grid(row=0, column=0, columnspan=2,
                                               pady=(10, 10), padx=(10, 10))
        tk.Label(top,
                 text="""2018""",
                 justify=CENTER).grid(row=1, column=0, columnspan=2,
                                      pady=(10, 10), padx=(10, 10))
        tk.Label(top,
                 text="""Contact:""",
                 justify=CENTER).grid(row=2, column=0, columnspan=1,
                                      pady=(10, 10), padx=(10, 10))
        about_message = """aleyr@walla.com"""
        msg = tk.Text(top, height=1, width=27)
        msg.grid(row=2, column=1, padx=(10, 10), pady=(10, 10))
        msg.insert("1.0", about_message)
        button = tk.Button(top, height=1, width=20, text="OK", underline=0,
                           command=top.destroy, bg='gray97', relief=tk.GROOVE)
        button.grid(row=3, column=0, columnspan=2, sticky=S, pady=(0, 10))
        top.resizable(width=FALSE, height=FALSE)
        button.focus_set()
        top.bind('<Alt_L><o>', lambda e: top.destroy())
        top.bind('<Escape>', lambda e: top.destroy())
