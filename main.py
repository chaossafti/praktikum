from tabellenGenerator import generate_output
from CSVIO import read_csv
from sys import argv

if __name__ == '__main__':
    if len(argv) < 5:
        print("<studenten.csv> <schein_studenten.csv> <notentabelle.csv> <bestandentabelle.csv> <punktetabelle.csv>")
        exit(1)

    students: list[dict] = read_csv(argv[1])
    schein_students: list[dict] = read_csv(argv[2])
    for schein_student in schein_students:
        schein_student["Schein?"] = "Schein"

    # merge both input files into a single list
    for student in students:
        student["Schein?"] = "Kein Schein"
        schein_students.append(student)

    generate_output((argv[3], argv[4], argv[5]), schein_students)
