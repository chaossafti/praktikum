from tkinter import Canvas, Tk


class BarChart(Canvas):

    def __init__(self, root, data: dict[str, int], width: int, dx: int, x: int, y: int):
        super().__init__(master=root, width=min(500, x+(dx*(len(data)))+(len(data)*width)))
        self.x = x
        self.y = y
        self.dx = dx
        self.width = width
        self.data = data

        self.draw()

    def draw(self):
        # title
        self.create_text(250, 20, text="Noten")

        x: int = self.x
        y: int = self.y

        available_height: float = self.winfo_reqheight()*0.85
        scale: float = available_height / max(self.data.values())

        # draw each data point
        for name in self.data:
            height: float = self.data[name] * scale
            self.create_rectangle(x + self.width, y - height, x, y, fill="orange")
            self.create_text(x + (self.width / 2), y + 10, text=name, font=('Arial', 11, 'bold'))
            self.create_text(x + (self.width / 2), y + 10 - max(height, 40) / 2,
                             text=self.data[name], font=('Arial', 11, 'bold'), angle=90)

            x += self.dx + self.width


    def redraw(self, data: dict[str, int]):
        self.data = data
        self.delete("all")
        self.draw()


if __name__ == '__main__':
    w: Tk = Tk()

    d: dict = {}
    for i in range(15):
        d[str(i)] = i

    BarChart(w, d, 30, 5, 5, 250).grid(row=0, column=0)
    w.mainloop()