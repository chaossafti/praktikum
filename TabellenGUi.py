import os.path
import time
import tkinter
from tkinter import *
import re
import pyautogui
from AuswertungWindow import Window
import absBoxPlot
import grading
import relBoxPlot
import tabellenGenerator
from CSVIO import write_csv, read_csv
from Tabelle import Tabelle

_COLUMN_TO_KEY: dict[int, str] = {
    0: "Vorname",
    1: "Nachname",
    2: "Matrikelnummer",
    3: "Schein?"
}

_KEY_TO_COLUMN: dict[str, int] = {
    "Vorname": 0,
    "Nachname": 1,
    "Matrikelnummer": 2,
    "Schein?": 3
}

_TASK_START_INDEX = len(_COLUMN_TO_KEY)
_POST_TASK_OFFSET = 3
_POINTS_ENTRY_PATTERN = r"\d+[,.]?\d*"
_POINTS_ENTRY_WIDTH = 5
_GRADE_ENTRY_WIDTH = 5


class PunkteTabelle(Tabelle):

    def __init__(self, root: Tk, students: list[dict], output_paths: tuple[str, str, str],task_count: int):
        super().__init__(root)
        self.auswertung_window = None
        self.box_plot_window = None
        self.box_plot = None
        self.notendiagramm = None
        self.notendiagramm_window: Tk | None = None
        self.students = students
        self.notentabelle_file_path: str = output_paths[0]
        self.bestandentabelle_file_path: str = output_paths[1]
        self.save_file: str = output_paths[2]
        self.last_save: list[dict] = read_csv(self.save_file)
        self.task_count = task_count

        # write the headers for the table
        self.place_entry(0, _KEY_TO_COLUMN["Vorname"], "Vorname")
        self.place_entry(0, _KEY_TO_COLUMN["Nachname"], "Nachname")
        self.place_entry(0, _KEY_TO_COLUMN["Matrikelnummer"], "Matrikelnummer")
        self.place_entry(0, _KEY_TO_COLUMN["Schein?"], "Schein?")

        # write the task headers (Aufgabe N)
        for column in range(self.task_count):
            self.place_entry(0, column + _TASK_START_INDEX, "A" + str(column + 1), width=_POINTS_ENTRY_WIDTH)

        trailig_headers_start: int = self.task_count + _TASK_START_INDEX
        self.place_entry(0, trailig_headers_start, "insgt. punkte")
        self.place_entry(0, trailig_headers_start + 1, "note", width=_GRADE_ENTRY_WIDTH)
        self.place_entry(0, trailig_headers_start + 2, "Bestanden?")

        # fill in the table with data from the last save
        for row in range(len(students)):
            student: dict = students[row]
            for column in range(_TASK_START_INDEX + self.task_count - 1 + _POST_TASK_OFFSET):

                matrikelnummer: int = int(student["Matrikelnummer"])
                key: str
                if column in _COLUMN_TO_KEY:
                    # constant value
                    key = _COLUMN_TO_KEY[column]
                    self.place_entry(row + 1, column, student[key])

                else:
                    # points
                    task_index: str = "Aufgabe " + str(column - _TASK_START_INDEX + 1)
                    student_from_save: dict = {}

                    for saved_student in self.last_save:
                        if saved_student["Matrikelnummer"] == matrikelnummer:
                            student_from_save = saved_student

                    if student_from_save is not None and task_index in student_from_save:
                        # the student already has points assigned in the last save
                        self.place_entry(row + 1, column, str(student_from_save[task_index]), editable=True, width=_POINTS_ENTRY_WIDTH)

                    else:
                        # no points assigned yet
                        self.place_entry(row + 1, column, "0", editable=True, width=_POINTS_ENTRY_WIDTH)


        # "note", "insgt. punkte" and "Bestanden?" column
        sum_grades: int = 0
        for row in range(len(students)):
            sum_points: float = 0
            for task in range(self.task_count):
                text: str = self._ENTRYS[(row + 1, task + _TASK_START_INDEX)].get()
                points: float = self.get_points_on_task_from_row(row+1, task)
                if points == -1:
                    self.notify_invalid_points_entered_at(row+1, task)
                    continue
                sum_points += points

            grade: int = grading.get_grade(sum_points)
            sum_grades += grade
            self.place_entry(row + 1, _TASK_START_INDEX + self.task_count, str(sum_points), editable=False) # insgt. punkte
            self.place_entry(row + 1, _TASK_START_INDEX + self.task_count + 1, str(grade), editable=False, # grade
                             width=_GRADE_ENTRY_WIDTH)
            self.place_entry(row + 1, _TASK_START_INDEX + self.task_count + 2,
                             str("Bestanden" if grade < 5 else "Nicht Bestanden"), editable=False) # bestanden



        # average grade entry
        self.place_entry(len(students) + 1, self.task_count + _TASK_START_INDEX + 1, str(sum_grades / len(students)),
                         width=_GRADE_ENTRY_WIDTH)

        # "Speichern" button
        self.save = Button(self.root, command=self.on_save)
        self.save.config(text="Speichern")

        button_start_column: int = self.task_count + _TASK_START_INDEX + _POST_TASK_OFFSET
        self.save.grid(row=len(students), column=button_start_column)

        # "Noten berechnen" button
        self.calculate_grades_button = Button(self.root, command=self.reload)
        self.calculate_grades_button.config(text="Noten berechnen")

        self.calculate_grades_button.grid(row=len(students) + 1, column=button_start_column)

        # "Tabellen Erstellen" button
        def generate_tables():
            self.on_save(alert=False)
            tabellenGenerator.generate_tables(students, self.notentabelle_file_path, self.bestandentabelle_file_path)

        self.create_tables = Button(self.root, command=generate_tables)
        self.create_tables.config(text="Tabellen Erstellen")

        self.create_tables.grid(row=len(students) - 1, column=button_start_column)

        # "Auswertung." button
        self.calculate_grades_button = Button(self.root, command=self.show_auswertung)
        self.calculate_grades_button.config(text="Auswertung")

        self.calculate_grades_button.grid(row=len(students) - 2, column=button_start_column)


        # confirm close
        root.protocol("WM_DELETE_WINDOW", self.on_close)


    def show_auswertung(self):
        self.auswertung_window = Window(self)
        self.auswertung_window.mainloop()


    def on_close(self):
        _SAVE_CLOSE = "Speichern und Schließen"
        _CLOSE = "Schließen ohne zu Speichern"
        _CANCEL = "Abbrechen"

        # confirm does exist
        # noinspection PyUnresolvedReferences
        clicked: str | None = pyautogui.confirm(text="Schließen ohne zu speichern?",
                                                buttons=[_SAVE_CLOSE, _CLOSE, _CANCEL])

        if clicked is None or clicked == _CANCEL:
            return
        elif clicked == _SAVE_CLOSE:
            self.on_save()
            time.sleep(0.1)
            self.root.quit()
        elif clicked == _CLOSE:
            time.sleep(0.1)
            self.root.quit()

    def on_save(self, alert: bool = True):
        # run when button is pressed
        # read the points of the students

        for row in range(1, len(self.students) + 1):
            student: dict = self.student_from_row(row)

            sum_points: float = 0
            for task in range(self.task_count):
                points = self.get_points_on_task_from_row(row, task)
                if points == -1:
                    self.notify_invalid_points_entered_at(row, task)
                    continue
                sum_points += points

                student["Aufgabe " + str(task + 1)] = points

            student["insgt. punkte"] = sum_points
            student["note"] = grading.get_grade(sum_points)

        save_data: list[dict] = []
        for s in self.students:
            save_data.append(s)

        # save the points into the csv
        write_csv(self.save_file, save_data)
        if alert:
            pyautogui.alert("Noten Gespeichert!")

    def reload(self):
        self.on_save(alert=False)
        # "note" and "bestanden" column
        sum_grades: int = 0
        for row in range(len(self.students)):
            sum_points: float = 0
            # add points
            for task in range(self.task_count):
                points: float = self.get_points_on_task_from_row(row+1, task)
                if points == -1:
                    self.notify_invalid_points_entered_at(row+1, task)
                    continue

                sum_points += points

            grade: int = grading.get_grade(sum_points)
            sum_grades += grade

            entries_start_index: int = self.task_count + _TASK_START_INDEX
            # "insgt. punkte"
            sum_points_var = self._TEXT_VARIABLES[(row + 1, entries_start_index)]
            sum_points_var.set(str(sum_points))

            # "note"
            grade_var = self._TEXT_VARIABLES[(row + 1, entries_start_index + 1)]
            grade_var.set(str(grade))

            # "Bestanden?"
            bestanden_var = self._TEXT_VARIABLES[(row + 1, entries_start_index + 2)]
            bestanden_var.set(str("Bestanden" if grade < 5 else "Nicht Bestanden"))

        # average grade entry

        var: tkinter.StringVar = self._TEXT_VARIABLES[len(self.students) + 1, self.task_count + _TASK_START_INDEX + 1]
        var.set(str(sum_grades / len(self.students)))

    def vorname_from_row(self, row: int) -> str:
        return self._TEXT_VARIABLES[(row, _KEY_TO_COLUMN["Vorname"])].get()

    def nachname_from_row(self, row: int) -> str:
        return self._TEXT_VARIABLES[(row, _KEY_TO_COLUMN["Nachname"])].get()

    def matrikelnummer_from_row(self, row: int) -> int:
        return int(self._TEXT_VARIABLES[(row, _KEY_TO_COLUMN["Matrikelnummer"])].get())

    def student_from_row(self, row: int) -> dict:
        return self.students[row - 1]

    def get_points_on_task_from_row(self, row: int, task: int) -> float:
        text: str = self._ENTRYS[(row, _TASK_START_INDEX + task)].get()
        if len(text) < 1:
            return 0

        if re.fullmatch(_POINTS_ENTRY_PATTERN, text):
            return float(text.replace(',', '.'))
        else:
            return -1.0

    def notify_invalid_points_entered_at(self, row: int, task: int):
        pyautogui.alert("Aufgabe " + str(
            task + 1) + " bei " + self.nachname_from_row(row) + ", " + self.vorname_from_row(
            row) + " enthät einen falschen Wert!")


def start(students: list[dict], output_paths: tuple[str, str, str]) -> None:
    root: Tk = Tk(className="Noten Tabelle - " + os.path.basename(output_paths[2]))

    def get_valid_input(var: StringVar, error: str) -> int | None:
        try:
            return int(var.get())
        except ValueError:
            pyautogui.alert(error)
            return None

    def start_gui():
        task_count = get_valid_input(question_task_count_input_var, "Falsche eingabe bei Aufgaben Anzahl")
        total_points = get_valid_input(question_total_points_input_var, "Falsche eingabe bei Insgt. Punkten")
        required_points = get_valid_input(question_required_points_input_var, "Falsche eingabe bei Bestanden ab")

        if task_count is None or total_points is None or required_points is None:
            return

        grading.set_total_points(total_points)
        grading.set_required_points(required_points)

        for widget in root.winfo_children():
            widget.destroy()
        grading.set_grading(grading.create_grade_table())
        PunkteTabelle(root, students, output_paths, task_count)



    question_task_count = Entry(root)
    question_total_points = Entry(root)
    question_required_points = Entry(root)

    question_task_count.insert(END, "Aufgaben Anzahl")
    question_total_points.insert(END, "Insgt. Punkte")
    question_required_points.insert(END, "Bestanden ab")

    question_task_count.config(state="readonly")
    question_total_points.config(state="readonly")
    question_required_points.config(state="readonly")


    question_task_count_input_var = tkinter.StringVar()
    question_total_points_input_var = tkinter.StringVar()
    question_required_points_input_var = tkinter.StringVar()

    question_task_count_input = Entry(root, textvariable=question_task_count_input_var)
    question_total_points_input = Entry(root, textvariable=question_total_points_input_var)
    question_required_points_input = Entry(root, textvariable=question_required_points_input_var)


    question_task_count.grid(row=0, column=0)
    question_total_points.grid(row=1, column=0)
    question_required_points.grid(row=2, column=0)

    question_task_count_input.grid(row=0, column=1)
    question_total_points_input.grid(row=1, column=1)
    question_required_points_input.grid(row=2, column=1)



    done_button = Button(text="Fertig", command=start_gui)
    done_button.grid(row=3, column=0)

    root.mainloop()

