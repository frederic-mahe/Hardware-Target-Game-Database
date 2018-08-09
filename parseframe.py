#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graphical User Iterface for build_pack and parse_pack scripts.
"""


import tkinter as tk
from tkinter import *
from tkinter import ttk
import os
from subprocess import Popen, PIPE
from threading import Thread
from queue import Queue, Empty
from textmessage import *
from utils import *

__author__ = "aleyr"
__date__ = "2018/08/09"
__version__ = "$Revision: 0.3"


class ParseFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.path_dir_roms = StringVar()
        self.path_pack_file = StringVar()
        self.text_label = StringVar()

        # ROMs directory
        textbox_roms = Entry(self, width=50, textvariable=self.path_dir_roms)
        textbox_roms.grid(column=2, row=1, sticky=E)
        # textbox_roms.pack(pady=10, padx=10)
        ttk.Label(self, text="ROMs folder: "
                  ).grid(column=1, row=1, sticky=W)
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
        ttk.Label(self, text="New pack file: "
                  ).grid(column=1, row=2, sticky=W)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   select_file_save(self.path_pack_file,
                                    "Save SMDB/pack file")
                   ).grid(column=3, row=2, sticky=W)

        button_frame = ttk.Frame(self)
        ttk.Button(button_frame, text="Clear", underline=0,
                   command=lambda:
                   self.click_clear()
                   ).grid(column=1, row=1, sticky=E)
        self.parent.bind("<Alt_L><c>", lambda e: self.click_clear())
        ttk.Button(button_frame, text="Command", underline=2,
                   command=lambda:
                   self.click_command()
                   ).grid(column=2, row=1, sticky=E)
        self.parent.bind("<Alt_L><m>", lambda e: self.click_command())
        ttk.Button(button_frame, text="Parse", underline=0,
                   command=lambda:
                   self.click_parse()
                   ).grid(column=3, row=1, sticky=W)
        self.parent.bind("<Alt_L><p>", lambda e: self.click_parse())
        button_frame.grid(column=2, row=8, columnspan=3, sticky=E)

        self.label = ttk.Label(self,
                               textvariable=self.text_label,
                               font=(None, 50)
                               ).grid(column=1, row=9,
                                      columnspan=5, sticky=W)

        textbox_roms.focus_set()

    def click_clear(self):
        self.path_dir_roms.set("")
        self.path_pack_file.set("")

    def click_command(self):
        if self.validate_info():
            cmd = create_command(folder=self.path_dir_roms.get(),
                                 output=self.path_pack_file.get())
            TextMessage().popup("Python command", cmd)

    def validate_info(self):
        out = False
        if (not self.path_dir_roms.get() == "" and
                os.path.lexists(self.path_dir_roms.get()) and
                not self.path_pack_file.get() == ""):
            out = True
        else:
            error_msg = ""
            if self.path_dir_roms.get() == "":
                error_msg += "ROMs folder is a required field.\n"
            if not os.path.lexists(self.path_dir_roms.get()):
                error_msg += "ROMs folder does not exist, "
                error_msg += "please select a valid folder.\n"
            if self.path_pack_file.get() == "":
                error_msg += "New pack file is a required field.\n"
            TextMessage().popup("Error", error_msg)

        return out

    def click_parse(self):
        if self.validate_info():
            cmd = create_command_array(folder=self.path_dir_roms.get(),
                                       output=self.path_pack_file.get())
            print(str(cmd))
            # subprocess.call(cmd, shell=True)
            # t = threading.Thread(target=parse_pack.parse_folder,
            #                      name="parsing",
            #                      args=[self.path_dir_roms.get(),
            #                            self.path_pack_file.get()])
            # t.daemon = True
            # t.start()
        self.process = Popen(cmd, stdout=PIPE)

        q = Queue(maxsize=1024)
        t = Thread(target=self.reader_thread, args=[q])
        t.daemon = True  # close pipe if GUI process exits
        t.start()

        self.update(q)
        # self.parent.after(40, self.update, q)  # start update loop

    def reader_thread(self, q):
        """Read subprocess output and put it into the queue."""
        try:
            with self.process.stdout as pipe:
                for line in iter(pipe.readline, b''):
                    q.put(line)
        finally:
            q.put(None)

    def update(self, q):
        """Update GUI with items from the queue."""
        # display all content
        for line in iter_except(q.get_nowait, Empty):
            if line is None:
                # print("Work is done!!!!")
                self.quit()
                return
            else:
                # if self.parent.progress["maximum"] < 0:
                #     self.parent.progress["maximum"] = float(line[29:38])
                # print("line " + str(line))
                # print("progress number " + str(float(line[18:27])))
                self.parent.progress["value"] = float(line[18:27])
                self.text_label.set(line[18:27])
                break  # display no more than one line per 40 milliseconds
        self.parent.after(40, self.update, q)  # schedule next update

    def quit(self):
        self.parent.progress["value"] = 0
        self.process.kill()  # exit subprocess if GUI is closed (zombie!)
        # self.parent.destroy()
