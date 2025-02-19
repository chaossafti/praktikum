import TabellenGUi
from CSVIO import write_csv


def generate_output(output_paths: tuple[str, str, str], students: list[dict]) -> None:
    # sort the students alphabetically
    students = sorted(students, key=lambda d: d['Nachname'], reverse=False)
    TabellenGUi.start(students, output_paths)


def generate_tables(students: list[dict], notentabelle_file: str, bestandentabelle_file: str):
    def build(fields_to_copy: list[str]) -> list[dict]:
        result: list[dict] = []
        for s in students:
            s_copy: dict = {}
            for field in fields_to_copy:
                try:
                    s_copy[field] = s[field]
                except KeyError as e:
                    print(s)
                    raise e

            result.append(s_copy)
        return result

    # grade table: vorname/nachname/matrikelnummer/insgt. punkte/noten
    # succeed table: vorname/nachname/matrikelnummer/insgt. punkte/bestanden

    # create grade table:
    grade_table: list[dict] = build(['Vorname', "Nachname", "Matrikelnummer", "insgt. punkte", "note"])

    # create succeed_table
    succeed_table: list[dict] = []
    for student in students:
        student_copy: dict = {"Vorname": student["Vorname"], "Nachname": student["Nachname"],
                              "Matrikelnummer": student["Matrikelnummer"], "insgt. punkte": student["insgt. punkte"]}
        if student["note"] < 5:
            student_copy["bestanden"] = "Bestanden"
        else:
            student_copy["bestanden"] = "Nicht Bestanden"

        succeed_table.append(student_copy)

    # store both tables
    write_csv(notentabelle_file, grade_table)
    write_csv(bestandentabelle_file, succeed_table)
