from tkinter import *
import tkinter


class Tabelle:

    def __init__(self, root):
        self._TEXT_VARIABLES = {}
        self._ENTRYS = {}
        self.root = root

    def place_entry(self, row: int, column: int, text: str, master = None, width: int = 15, editable: bool = False) -> tuple[Entry, StringVar]:
        var: tkinter.StringVar = tkinter.StringVar()
        if master is None:
            master = self.root


        e = Entry(master, width=width, fg='black',
                  font=('Arial', 11, 'bold'), textvariable=var)
        e.insert(END, text)
        e.grid(row=row, column=column)
        e.grid_columnconfigure(0, weight=0)
        e.grid_columnconfigure(1, weight=0)

        if not editable:
            e.config(state="readonly")

        self._ENTRYS[(row, column)] = e
        self._TEXT_VARIABLES[(row, column)] = var

        return e, var
