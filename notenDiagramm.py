from tkinter import Canvas, Button
import pyautogui
import TabellenGUi
import grading
from BarChart import BarChart
from grading import grade_at_scale
from Tabelle import Tabelle


_GRADE_ENTRY_WIDTH = 7
_POINTS_ENTRY_WIDTH = 13

class NotenDiagram(Tabelle):

    def create_notenspiegel(self) -> dict[str, int]:
        notenspiegel: dict[float, int] = {}
        for student in self.students:
            if student["note"] in notenspiegel:
                notenspiegel[student["note"]] += 1
            else:
                notenspiegel[student["note"]] = 1

        sorted_grades = sorted(grade_at_scale)
        result: dict[str, int] = {}
        for n in sorted_grades:
            grade: float = grade_at_scale[n]
            if grade in notenspiegel:
                result[str(grade)] = notenspiegel[grade]
            else:
                result[str(grade)] = 0

        return result

    def __init__(self, root, students: list[dict], table: TabellenGUi):
        super().__init__(root)
        self.students = students
        self.tabelle_canvas = Canvas(self.root)
        self.bar_chart_canvas = Canvas(self.root)
        self.notenspiegel = self.create_notenspiegel()
        self.bar_chart = BarChart(self.bar_chart_canvas, self.notenspiegel, 30, 5, 5, 250)
        self.bar_chart.grid(row=2, column=0)
        self.points_table: TabellenGUi = table

        # place headers
        for n in grade_at_scale:
            self.place_entry(0, n, str(grade_at_scale[n]), width=_GRADE_ENTRY_WIDTH, master=self.tabelle_canvas)


        # place the values
        for n in grade_at_scale:
            grade: float = grade_at_scale[n]
            grade_count: int = self.notenspiegel[str(grade)] if grade in self.notenspiegel else 0
            self.place_entry(1, n, str(grade_count), width=_GRADE_ENTRY_WIDTH, master=self.tabelle_canvas)

        self.tabelle_canvas.pack(side="top", expand=False, anchor="nw")

        # create a bar chart
        self.bar_chart_canvas.location(0, 100)
        self.bar_chart_canvas.pack(side="left", expand=False, anchor="nw")

        # place the editable Entries

        self.place_entry(0, 11, str("insgt. punkte"), editable=False, width=_POINTS_ENTRY_WIDTH, master=self.tabelle_canvas)
        self.total_points_entry = self.place_entry(0, 12, str(grading.total_points), editable=True, width=_POINTS_ENTRY_WIDTH, master=self.tabelle_canvas)

        self.place_entry(1, 11, str("Bestanden ab"), editable=False, width=_POINTS_ENTRY_WIDTH, master=self.tabelle_canvas)
        self.points_needed_entry = self.place_entry(1, 12, str(grading.points_needed_for_success), editable=True, width=_POINTS_ENTRY_WIDTH, master=self.tabelle_canvas)

        # "Neu laden" button
        self.calculate_grades_button = Button(self.tabelle_canvas, command=self.reload)
        self.calculate_grades_button.config(text="Neu laden")

        self.calculate_grades_button.grid(row=2, column=12)

    def reload(self):

        # update the total points and required points to succeed values
        try:
            tp = int(self.total_points_entry[0].get())
            grading.set_total_points(tp)
        except ValueError as e:
            pyautogui.alert("Das ingst. punkte feld enthält eine falsche punkt anzahl!")
            raise e

        try:
            tp = int(self.points_needed_entry[0].get())
            grading.set_required_points(tp)
        except ValueError:
            pyautogui.alert("Das Bestanden ab feld enthält eine falsche punkt anzahl!")

        # update grades inside the points table
        self.points_table.reload()

