from tkinter import *
import TabellenGUi
import notenDiagramm


class Window(Tk):

    def __init__(self, table: TabellenGUi):
        super().__init__(className="Auswertung")
        table.on_save(alert=False)
        self.notendiagram = notenDiagramm.NotenDiagram(self, table.students, table)



