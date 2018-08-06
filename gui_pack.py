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
from platform import system
# import subprocess
import parse_pack
import threading


__author__ = "aleyr"
__date__ = "2018/08/03"
__version__ = "$Revision: 0.1"


# *********************************************************************#
#                                                                      #
#                             Classes                                  #
#                                                                      #
# *********************************************************************#

# Class for popup messages
class TextMessage(object):
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

    def about(self, fontz):
        top = tk.Toplevel()
        top.title("About")
        top.lift()
        tk.Label(top,
                 text="""Smoke Monster Packs UI
       by Aleyr""",
                 justify=CENTER,
                 font=fontz["bold"]).grid(row=0, column=0, columnspan=2,
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
                              TextMessage().about(fontz))
        self.add_cascade(label="Help", menu=help_menu)


class ParseFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.path_dir_roms = StringVar()
        self.path_pack_file = StringVar()

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
        # ttk.Button(button_frame, text="Parse", underline=0,
        #            command=lambda:
        #            self.click_parse()
        #            ).grid(column=3, row=1, sticky=W)
        # self.parent.bind("<Alt_L><p>", lambda e: self.click_parse())
        # button_frame.grid(column=2, row=8, columnspan=3, sticky=E)

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
            # cmd = create_command_array(folder=self.path_dir_roms.get(),
            #                            output=self.path_pack_file.get())
            # print(str(cmd))
            # subprocess.call(cmd, shell=True)
            t = threading.Thread(target=parse_pack.parse_folder,
                                 name="parsing",
                                 args=[self.path_dir_roms.get(),
                                       self.path_pack_file.get()])
            t.daemon = True
            t.start()


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
        self.file_strategy = IntVar()
        self.overwrite = IntVar()

        # self.file_strategy.set(0)
        # self.overwrite.set(1)

        # ROMs directory
        textbox_roms = Entry(self, width=50, textvariable=self.path_dir_roms)
        textbox_roms.grid(column=2, row=1, sticky=E)
        ttk.Label(self, text="ROMs folder: "
                  ).grid(column=1, row=1, sticky=W)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   select_folder(self.path_dir_roms, "Select ROMs folder")
                   ).grid(column=3, row=1, sticky=W)

        # SMDB file
        textbox_pack_file = Entry(self, width=50,
                                  textvariable=self.path_pack_file)
        textbox_pack_file.grid(column=2, row=2, sticky=E)
        ttk.Label(self, text="SMDB/pack file: "
                  ).grid(column=1, row=2, sticky=W)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   select_file_open(self.path_pack_file,
                                    "Select SMDB/pack file")
                   ).grid(column=3, row=2, sticky=W)

        # Pack directory
        textbox_pack = Entry(self, width=50, textvariable=self.path_dir_pack)
        textbox_pack.grid(column=2, row=3, sticky=E)
        ttk.Label(self, text="Pack folder: "
                  ).grid(column=1, row=3, sticky=W)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   select_folder(self.path_dir_pack, "Select Pack folder")
                   ).grid(column=3, row=3, sticky=W)

        # Missing file
        textbox_missing_file = Entry(self, width=50,
                                     textvariable=self.path_missing_file)
        textbox_missing_file.grid(column=2, row=4, sticky=E)
        ttk.Label(self, text="Missing file: "
                  ).grid(column=1, row=4, sticky=W)
        ttk.Button(self, text="Browse",
                   command=lambda:
                   select_file_save(self.path_missing_file,
                                    "Save missing file")
                   ).grid(column=3, row=4, sticky=W)

        ttk.Label(self, text="File strategy: "
                  ).grid(column=1, row=5, sticky=W)
        Radiobutton(self, text="Copy", variable=self.file_strategy, value=0
                    ).grid(column=2, row=5, sticky=W)
        Radiobutton(self, text="HardLink", variable=self.file_strategy, value=1
                    ).grid(column=2, row=6, sticky=W)

        ttk.Label(self, text="Skip existing: "
                  ).grid(column=1, row=7, sticky=W)
        Checkbutton(self, text="", variable=self.overwrite
                    ).grid(column=2, row=7, sticky=W)
        self.overwrite.set(1)

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
        # ttk.Button(button_frame, text="Build", underline=0,
        #            command=lambda:
        #            self.click_build()
        #            ).grid(column=3, row=1, sticky=W)
        # self.parent.bind("<Alt_L><b>", lambda e: self.click_build())
        # button_frame.grid(column=2, row=8, columnspan=3, sticky=E)

        textbox_roms.focus_set()

    def click_clear(self):
        self.path_dir_roms.set('')
        self.path_pack_file.set('')
        self.path_dir_pack.set('')
        self.path_missing_file.set('')
        self.file_strategy.set(0)
        self.overwrite.set(1)

    def click_command(self):
        if self.validate_info():
            cmd = create_command(input_folder=self.path_dir_roms.get(),
                                 database=self.path_pack_file.get(),
                                 output_folder=self.path_dir_pack.get(),
                                 missing=self.path_missing_file.get(),
                                 file_strategy=self.file_strategy.get(),
                                 skip_eisting=self.overwrite.get())
            TextMessage().popup("Python command", cmd)

    def validate_info(self):
        out = False
        if (not self.path_dir_roms.get() == "" and
                os.path.lexists(self.path_dir_roms.get()) and
                not self.path_pack_file.get() == "" and
                not self.path_dir_pack.get() == ""):
            out = True
        else:
            error_msg = ""
            if self.path_dir_roms.get() == "":
                error_msg += "ROMs folder is a required field.\n"
            if not os.path.lexists(self.path_dir_roms.get()):
                error_msg += "ROMs folder does not exist, "
                error_msg += "please select a valid folder.\n"
            if self.path_pack_file.get() == "":
                error_msg += "SMDB/pack file is a required field.\n"
            if self.path_dir_pack.get() == "":
                error_msg += "Pack folder is a required field.\n"
            TextMessage().popup("Error", error_msg)

        return out

    def click_build(self):
        if self.validate_info():
            print("Build")


class App(Tk):
    def __init__(self, *args, **kwargs):
        # call the parent constructor
        Tk.__init__(self, *args, **kwargs)

        tab_control = ttk.Notebook(self)

        build_frame = BuildFrame(self, padding="3 3 12 12")
        build_frame.pack(side="top", fill="both", expand=True)
        tab_control.add(build_frame, text="Build Pack", sticky=N)

        parse_frame = ParseFrame(self, padding="3 3 12 12")
        parse_frame.pack(side="top", fill="both", expand=True)
        tab_control.add(parse_frame, text="Parse ROMs Folder", sticky=N)

        tab_control.pack(expand=1, fill="both")

        menu_bar = MenuBar(self)

        self.config(menu=menu_bar)


# *********************************************************************#
#                                                                      #
#                            Functions                                 #
#                                                                      #
# *********************************************************************#

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
    cmd = sys.executable
    if folder:
        cmd += " " + os.path.join(os.getcwd(), "parse_pack.py")
        cmd += " -f " + folder
        cmd += " -o " + output
    else:
        cmd += " " + os.path.join(os.getcwd(), "build_pack.py")
        cmd += " -i " + input_folder
        cmd += " -d " + database
        cmd += (" -o " + output_folder) if output_folder else ""
        cmd += (" -m " + missing) if missing else ""
        if file_strategy == 0:
            cmd += " --file_strategy copy"
        else:
            cmd += " --file_strategy hardlink"
        cmd += " --skip_existing" if skip_eisting else ""

    # cmd += "\n\n\nExecute above command on the folder where the script "
    # cmd += "is located."

    return cmd


def create_command_array(folder=None, output=None, input_folder=None,
                         database=None, output_folder=None, missing=None,
                         file_strategy=None, skip_eisting=None):
    # cmd = ["cmd", "/k", sys.executable]
    cmd = [sys.executable]
    if folder:
        cmd.append(os.path.join(os.getcwd(), "parse_pack.py"))
        cmd.append("-f")
        cmd.append(folder)
        cmd.append("-o")
        cmd.append(output)
    else:
        cmd.append(os.path.join(os.getcwd(), "build_pack.py"))
        cmd.append("-i")
        cmd.append(input_folder)
        cmd.append("-d")
        cmd.append(database)
        cmd.append("-o")
        cmd.append(output_folder)
        cmd.append("-m")
        cmd.append(missing)
        if file_strategy == 0:
            cmd.append("--file_strategy")
            cmd.append("copy")
        else:
            cmd.append("--file_strategy")
            cmd.append("hardlink")
        if skip_eisting:
            cmd.append("--skip_existing")

    return cmd


def main():
    app = App()
    app.title("EverDrive-Packs-Lists-Database")
    app.mainloop()

# *********************************************************************#
#                                                                      #
#                              Body                                    #
#                                                                      #
# *********************************************************************#


# Fonts
if "Darwin" in system():
    #    print("\nOS X detected")
    fontsize = 12
    pad_radio = 3
    but_size = -2
    res_size = -1
else:
    #    print("\nWindows detected")
    fontsize = 10
    pad_radio = 0
    but_size = -2
    res_size = -2

window_font = "TkDefaultFont %s" % fontsize
fontz = {"bold": ("TkDefaultFont", fontsize, "bold"),
         "normal_small": ("TkDefaultFont", fontsize + but_size, "normal"),
         "italic_small": ("TkDefaultFont", fontsize + but_size, "italic")}


if __name__ == '__main__':
    main()
