from tkinter import *
import TabellenGUi
import absBoxPlot
import notenTabelle
import relBoxPlot
from BarChart import BarChart
import grading


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
        self.table = table
        table.on_save(alert=False)
        self.table_canvas = Canvas(self, height=24*4)
        self.diagram_canvas = Canvas(self)
        self.button_canvas = Canvas(self, width=self.winfo_reqwidth())

        self.table_canvas.pack(side="top", anchor="w")
        self.button_canvas.pack(side="bottom", anchor="w")
        self.diagram_canvas.pack(side="bottom", anchor="w")

        self.order = ["barchart", "rel", "abs"]

        self.notenspiegel = grading.create_notenspiegel(table.students)
        self.notentabelle = notenTabelle.NotenTabelle(self.table_canvas, table.students, table)
        self.notentabelle.calculate_grades_button.config(command=self.reload)


        self.bar_chart = BarChart(self.diagram_canvas, self.notenspiegel, 40, 5, 0, 250)
        self.rel_boxplot = relBoxPlot.Boxplot(self.diagram_canvas, self.get_rel_boxplot_data())
        self.abs_boxplot = absBoxPlot.Boxplot(self.diagram_canvas, self.get_abs_boxplot_data())
        self.total_len = self.rel_boxplot.winfo_reqwidth() + self.abs_boxplot.winfo_reqwidth() + self.bar_chart.winfo_reqwidth()
        self.name_to_diagram = {"barchart": self.bar_chart, "rel": self.rel_boxplot, "abs": self.abs_boxplot}

        def move_left(index: int):
            to_move = self.order[index]
            left_index = index - 1 if index > 0 else 2
            left = self.order[left_index]
            self.order[left_index] = to_move
            self.order[index] = left

            self.redraw()

        def move_right(index: int):
            to_move = self.order[index]
            right_index = index + 1 if index < 2 else 0
            right = self.order[right_index]
            self.order[right_index] = to_move
            self.order[index] = right

            self.redraw()


        def move_first_left():
            move_left(0)
        def move_second_left():
            move_left(1)
        def move_third_left():
            move_left(2)

        def move_first_right():
            move_right(0)
        def move_second_right():
            move_right(1)
        def move_third_right():
            move_right(2)

        # first diagram
        b = Button(self.button_canvas, text=str("<"), command=move_first_left)
        b.grid(row=0, column=0, padx=500*0.32)

        b = Button(self.button_canvas, text=str(">"), command=move_first_right)
        b.grid(row=0, column=1)


        # second diagram
        b = Button(self.button_canvas, text=str("<"), command=move_second_left)
        b.grid(row=0, column=2, padx=500*0.5)

        b = Button(self.button_canvas, text=str(">"), command=move_second_right)
        b.grid(row=0, column=3)


        # third diagram
        b = Button(self.button_canvas, text=str("<"), command=move_third_left)
        b.grid(row=0, column=4, padx=500*0.5)

        b = Button(self.button_canvas, text=str(">"), command=move_third_right)
        b.grid(row=0, column=5)

        self.draw()

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
        i: int = -1
        for d in self.order:
            i += 1
            self.name_to_diagram[d].grid(row=2, column=i)



