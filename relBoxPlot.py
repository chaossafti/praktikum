import math
from tkinter import *

_VERTICAL_NODES = 11


def count_match(l: list, f):
    count: int = 0
    for e in l:
        if f(e) is True:
            count += 1
    return count


class Boxplot(Canvas):

    def assign_vars(self):
        self.highest_value = 0
        self.lowest_value = 0

        for l in self.data.values():
            self.highest_value = max(l) if max(l) > self.highest_value else self.highest_value

        for l in self.data.values():
            self.lowest_value = min(l) if min(l) > self.lowest_value else self.lowest_value

        self.sorted_data = sorted(self.data, key=lambda k: float(k))
        self.steps = len(self.data)

    def __init__(self, root, data: dict[int, list[float]]):
        super().__init__(root, width=600)
        self.data = data


        self.highest_value = -1
        self.lowest_value = -1
        self.sorted_data = None
        self.steps = -1

        self.assign_vars()

        self.root = root
        self.distance = self.winfo_reqwidth() * 0.9

        self.configure(height=300)
        self.abs_x_start = 30
        self.abs_y_start = (self.winfo_reqheight() - 40)

        self.draw()

    def redraw(self, data: dict[int, list[float]]):
        self.data = data
        self.assign_vars()
        self.delete("all")
        self.draw()

    def draw(self):
        horizontal_distance_step_size = self.distance / self.steps

        # horizontal line
        for i in range(self.steps):
            start_x: int = int(self.abs_x_start + horizontal_distance_step_size * i)
            end_x: int = int(self.abs_x_start + horizontal_distance_step_size * (i + 1))

            # lines
            self.create_line(start_x, self.abs_y_start, end_x, self.abs_y_start, width=2)
            self.create_line(start_x, self.abs_y_start, start_x, self.abs_y_start + 10, width=2)
            self.create_line(end_x, self.abs_y_start, end_x, self.abs_y_start + 10, width=2)

            # text
            self.create_text((start_x + end_x) / 2, self.abs_y_start + 10, text=str(self.sorted_data[i]))

        vertical_value_step_size: int = math.ceil(self.highest_value / (_VERTICAL_NODES-1))
        vertical_distance_step_size: int = int((self.winfo_reqheight() - 40) / (_VERTICAL_NODES-1))
        # vertical line
        for n in range(_VERTICAL_NODES):
            start_x: int = self.abs_x_start
            end_x: int = int(self.abs_x_start + self.distance)
            start_y: int = (n-1) * vertical_distance_step_size
            end_y: int = n * vertical_distance_step_size

            # lines
            self.create_line(start_x, start_y, start_x, end_y, width=2)  # straight vertical
            self.create_line(start_x - 10, start_y, end_x, start_y, width=1, fill="gray")  # horizontal

            # text
            self.create_text(start_x - 14, (start_y + end_y) / 2,
                             text=str((_VERTICAL_NODES - n) * 10) + "%",
                             font=("Arial", 9, "bold"))

        # draw boxplots
        vertical_distance_per_value: float = vertical_distance_step_size / vertical_value_step_size
        i: int = -1
        for k in self.sorted_data:
            i += 1
            l = self.data[k]
            highest_value: float = max(l)
            lowest_value: float = min(l)

            x = self.abs_x_start + i * horizontal_distance_step_size + (horizontal_distance_step_size / 2) + 5
            start_y: float = self.abs_y_start - highest_value * vertical_distance_per_value
            y_lowest_value = self.abs_y_start - (lowest_value * vertical_distance_per_value)

            # boxplots
            def calculate_quartil(p: float, sorted_data: list) -> float:
                index = p * (len(sorted_data) + 1)
                if index.is_integer():
                    return sorted_data[int(index) - 1]
                else:
                    lower = sorted_data[int(math.floor(index)) - 1]
                    upper = sorted_data[int(math.ceil(index)) - 1]
                    return (lower + upper) / 2

            l_sorted = sorted(l)
            q1 = calculate_quartil(0.25, l_sorted)
            q2 = calculate_quartil(0.5, l_sorted)
            q3 = calculate_quartil(0.75, l_sorted)

            q1_y = self.abs_y_start - (q1 * vertical_distance_per_value)
            q2_y = self.abs_y_start - (q2 * vertical_distance_per_value)
            q3_y = self.abs_y_start - (q3 * vertical_distance_per_value)

            # draw
            self.create_rectangle(x - 15, q3_y, x + 15, q1_y, fill="gray", outline="black")  # box
            self.create_line(x - 15, q2_y, x + 15, q2_y, fill="red")  # median
            self.create_line(x, q1_y, x, y_lowest_value, fill="black", width=2)  # lowest 25%
            self.create_line(x, q3_y, x, start_y, fill="black", width=2)  # highest 25%


if __name__ == '__main__':
    w = Tk()
    d: dict = {"1": [22, 31, 33, 3], "2": [1, 2, 3, 4, 5, 6, 7, 8]}

    Boxplot(w, d).grid(row=0, column=0)
    w.mainloop()
