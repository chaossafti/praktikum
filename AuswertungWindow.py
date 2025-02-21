import math
from sys import argv
from tkinter import *

import TabellenGUi
import absBoxPlot
import notenTabelle
import relBoxPlot
from BarChart import BarChart
import grading
from CSVIO import read_csv
from kreisdiagram import Kreisdiagram


_SMILEY_TO_COLOR = {
    ":)": "green",
    ":|": "yellow",
    ":(": "red",
    "X": "gray"
}

class Window(Tk):

    def get_rel_boxplot_data(self) -> dict[int, list[float]]:
        min_points_per_task: dict[int, float] = {}
        for task in range(self.table.task_count):
            min_points_per_task[task] = -1
            for row in range(len(self.table.students)):
                if min_points_per_task[task] < self.table.get_points_on_task_from_row(row + 1, task):
                    min_points_per_task[task] = self.table.get_points_on_task_from_row(row + 1, task)

        result: dict[int, list[float]] = {}
        for task in range(self.table.task_count):
            result[task] = []
            min_points = min_points_per_task[task]
            for row in range(len(self.table.students)):
                result[task].append(min_points / max(1, self.table.get_points_on_task_from_row(row + 1, task)))

        return result

    def get_abs_boxplot_data(self) -> dict[int, list[float]]:
        result: dict[int, list[float]] = {}
        for task in range(self.table.task_count):
            result[task] = []
            for row in range(len(self.table.students)):
                result[task].append(self.table.get_points_on_task_from_row(row + 1, task))

        return result


    def __init__(self, table: TabellenGUi):
        super().__init__(className="Auswertung")
        self.pie_chart_select_task_entry = None
        self.emoji_window = None
        self.smiley_table = None

        self.table = table
        table.on_save(alert=False)
        self.table_canvas = Canvas(self, height=24*4)
        self.diagram_canvas = Canvas(self, height=700)
        self.button_canvas = Canvas(self, width=self.winfo_reqwidth())
        self.pie_chart_canvas = Canvas(self, width=self.winfo_reqwidth())

        self.table_canvas.pack(side="top", anchor="w")
        self.button_canvas.pack(side="bottom", anchor="w")
        self.pie_chart_canvas.pack(side="bottom", anchor="w")
        self.diagram_canvas.pack(side="bottom", anchor="w")

        self.order = ["barchart", "rel", "abs"]

        self.notenspiegel = grading.create_notenspiegel(table.students)
        self.notentabelle = notenTabelle.NotenTabelle(self.table_canvas, table.students, table)
        self.notentabelle.calculate_grades_button.config(command=self.reload)
        self.notentabelle.emoji_button.config(command=self.show_emoji_table)

        self.smiley_data: list[dict] = read_csv(argv[6])
        self.pie_chart_data = {}

        self.pie_charts: dict = {}

        self.bar_chart = BarChart(self.diagram_canvas, self.notenspiegel, 40, 5, 0, 250)
        self.rel_boxplot = relBoxPlot.Boxplot(self.diagram_canvas, self.get_rel_boxplot_data())
        self.abs_boxplot = absBoxPlot.Boxplot(self.diagram_canvas, self.get_abs_boxplot_data())
        self.total_len = self.rel_boxplot.winfo_reqwidth() + self.abs_boxplot.winfo_reqwidth() + self.bar_chart.winfo_reqwidth()
        self.name_to_diagram = {"barchart": self.bar_chart, "rel": self.rel_boxplot, "abs": self.abs_boxplot}

        self.draw()


    def set_smiley_data(self, smiley_data: list[dict]):
        self.smiley_data = smiley_data
        self.redraw_all_pie_charts()

    def redraw_all_pie_charts(self):
        for task in range(self.table.task_count):
            chart = self.pie_charts[task]
            chart.redraw(self.gather_piechart_data(task))

    def show_emoji_table(self):
        import smileyTabelle
        self.emoji_window = Tk()
        self.smiley_table = smileyTabelle.SmileyTabelle(self.emoji_window, self.table.task_count, self)
        self.emoji_window.mainloop()

    def gather_piechart_data(self, task) -> list[tuple[int, str]]:
        ratings = {}
        for rating in self.smiley_data:
            if rating["task"] == task:
                ratings = rating
                break

        data = []
        for sm in _SMILEY_TO_COLOR.keys():
            c = _SMILEY_TO_COLOR[sm]
            data.append((ratings[sm], c))

        return data


    def reload(self):
        self.notentabelle.reload()
        self.abs_boxplot.redraw(self.get_abs_boxplot_data())
        self.rel_boxplot.redraw(self.get_rel_boxplot_data())

        # redraw the bar chart
        grading.grading = sorted(grading.create_grade_table(), key=lambda d: d['note'], reverse=True)
        grading.grade_all(self.table.students)
        self.notentabelle.notenspiegel = grading.create_notenspiegel(self.table.students)
        self.bar_chart.redraw(self.notentabelle.notenspiegel)



    def redraw(self):
        self.draw()

    def draw(self):
        self.bar_chart.grid(row=2, column=0)
        self.rel_boxplot.grid(row=2, column=1)
        self.abs_boxplot.grid(row=2, column=2)

        for task in range(self.table.task_count):
            chart = Kreisdiagram(self.pie_chart_canvas, self.gather_piechart_data(task), "Evaluation A" + str(task+1))
            chart.grid(row=math.floor(task / 10), column=task % 10)
            self.pie_charts[task] = chart





