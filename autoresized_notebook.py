from tkinter.ttk import Notebook


__author__ = "Miguel Martínez López"
__date__ = "2016/12/06"
__contact__ = "https://github.com/ActiveState/code"


class Autoresized_Notebook(Notebook):
    def __init__(self, master=None, **kw):
        Notebook.__init__(self, master, **kw)
        self.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event):
        event.widget.update_idletasks()

        tab = event.widget.nametowidget(event.widget.select())
        event.widget.configure(height=tab.winfo_reqheight())
