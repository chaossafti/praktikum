from tkinter import *
import tkinter


class Tabelle(Canvas):

    def __init__(self, root):
        super().__init__(root)
        self._TEXT_VARIABLES: dict[tuple, StringVar] = {}
        self._ENTRYS = {}
        self.root = root

    def place_entry(self, row: int, column: int, text: str, master = None, width: int = 15, editable: bool = False) -> tuple[Entry, StringVar]:
        if master is None:
            master = self.root
        var: tkinter.StringVar = tkinter.StringVar(master)


        e = Entry(master, width=width, fg='black',
                  font=('Arial', 11, 'bold'), textvariable=var)

        e.insert(END,text)
        var.set(text)

        e.grid(row=row, column=column)
        e.grid_columnconfigure(0, weight=0)
        e.grid_columnconfigure(1, weight=0)

        if not editable:
            e.config(state="readonly")

        self._ENTRYS[(row, column)] = e
        self._TEXT_VARIABLES[(row, column)] = var

        return e, var
