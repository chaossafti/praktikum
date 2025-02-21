from sys import argv

import pyautogui

from Tabelle import Tabelle
from tkinter import *
from CSVIO import write_csv

_TASK_ENTRY_WIDTH = 3


class SmileyTabelle(Tabelle):
    def __init__(self, root, task_count: int, auswertung):
        super().__init__(root)
        self.global_smiley_data: list[dict] = []
        self.smiley_data = {}

        self.auswertung_window = auswertung
        self.done = None
        self.none_button = None
        self.unhappy_button = None
        self.straight_button = None
        self.happy_button = None
        self.root = root
        self.task_count = task_count
        self.current_task = 0
        self.total = 0

        self.draw()


    def draw(self):
        # headers
        for task in range(self.task_count):
            self.place_entry(0, task, "A"+str(task+1))

        # text boxes
        for task in range(self.task_count):
            self.place_entry(1, task, "")

        # smiley commands
        def on_press(sm: str):
            if self.current_task >= self.task_count:
                return

            e = self._ENTRYS[1, self.current_task]
            e.config(state="normal")
            e.insert(END, sm)

            e.config(state="readonly")

            index = (sm, self.current_task)
            if index in self.smiley_data:
                self.smiley_data[index] += 1
            else:
                self.smiley_data[index] = 1

            self.current_task += 1

        def on_press_happy():
            on_press(":)")

        def on_press_straight():
            on_press(":|")

        def on_press_unhappy():
            on_press(":(")

        def on_press_none():
            on_press("X")

        # button placing
        self.happy_button = Button(self.root, text=":)", command=on_press_happy)
        self.happy_button.grid(row=2, column=0)

        self.straight_button = Button(self.root, text=":|", command=on_press_straight)
        self.straight_button.grid(row=2, column=1)

        self.unhappy_button = Button(self.root, text=":(", command=on_press_unhappy)
        self.unhappy_button.grid(row=2, column=2)

        self.none_button = Button(self.root, text="X", command=on_press_none)
        self.none_button.grid(row=2, column=3)

        # next_evaluation button
        def next_evaluation():
            def find_inside_global_smiley_data(task):
                for d in self.global_smiley_data:
                    if d["task"] == task:
                        return d

                return None

            for index in self.smiley_data:
                sm = index[0]
                task = index[1]
                d = find_inside_global_smiley_data(task)
                if d is None:
                    d = {"task": task, ":)": 0, ":|": 0, ":(": 0, "X": 0}
                    self.global_smiley_data.append(d)

                d[sm] += 1


            self.smiley_data = {}
            self.current_task = 0
            self.total += 1
            self.delete("all")
            self.draw()

        self.done = Button(self.root, text="Weiter", command=next_evaluation)
        self.done.grid(row=3, column=0)

        # done button
        def done():
            is_actually_done = pyautogui.confirm("Sicher das du Fertig bist?\nDu hast " + str(self.total) + " Klausuren ausgewertet.")
            if is_actually_done is None or not is_actually_done:
                return

            # save and update diagram
            write_csv(argv[6], self.global_smiley_data)

            self.auswertung_window.set_smiley_data(self.global_smiley_data)


        self.done = Button(self.root, text="Fertig", command=done)
        self.done.grid(row=3, column=1)

if __name__ == '__main__':
    w = Tk()
    s = SmileyTabelle(w,3, None)
    w.mainloop()

