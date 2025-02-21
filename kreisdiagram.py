from tkinter import *


class Kreisdiagram(Canvas):

    def __init__(self, root, data: list[tuple[int, str]], chartname):
        super().__init__(master=root, height=160, width=160)
        self.data = data
        self.sum_data = 0
        self.chartname = chartname
        for t in data:
            self.sum_data += t[0]

        normalized = []
        for t in data:
            normalized.append((t[0] / self.sum_data * 100, t[1]))

        self.data = normalized
        self.draw()


    def redraw(self, data: list[tuple[int, str]]):
        self.data = data
        self.sum_data = 0
        for t in data:
            self.sum_data += t[0]

        normalized = []
        for t in data:
            normalized.append((t[0] / self.sum_data * 100, t[1]))

        self.data = normalized

        self.delete("all")
        self.draw()


    def draw(self):
        self.create_text(100, 8, text=self.chartname)

        start = 0
        start_x = 20
        end_x = 160
        start_y = 20
        end_y = 160
        for v, c in self.data:
            self.create_arc(start_x, start_y, end_x, end_y, start=start, extent=v * 3.6, fill=c, outline="black", width=2)
            start = start + v * 3.6

