grade_at_scale: dict[int, float] = {
    0: 5,
    1: 4,
    2: 3.7,
    3: 3.3,
    4: 3.0,
    5: 2.7,
    6: 2.3,
    7: 2.0,
    8: 1.7,
    9: 1.3,
    10: 1
}

grading: list[dict] | None = None
def set_grading(g: list[dict]):
    global grading
    grading = g


total_points: int | None = None
def set_total_points(tp: int):
    global total_points
    total_points = tp


points_needed_for_success: int | None = None
def set_required_points(n: int):
    global points_needed_for_success
    points_needed_for_success = n



def create_grade_table() -> list[dict[str, float]]:
    global points_needed_for_success
    global total_points

    def calculate_needed_points(scale: int) -> float:
        return points_needed_for_success+(scale - 1)*(total_points - points_needed_for_success)/10

    result: list[dict[str, float]] = []
    for i in range(1, 11):
        # [{note: 1, punkte: 30}]
        result.append({"note": grade_at_scale[i], "punkte": calculate_needed_points(i)})

    return result


def get_grade(points: float):
    global grading

    i: int = -1
    for d in grading:
        i += 1
        required_points = d["punkte"]

        if points >= required_points:
            continue

        return min(grading[max(i - 1, 0)]["note"], 5) if i != 0 else 5

    # more points than a 1
    return 1

def grade_all(students: list[dict]) -> list[dict]:
    for student in students:
        student["note"] = get_grade(student["insgt. punkte"] if "insgt. punkte" in student else 0)

    return students

def create_notenspiegel(students) -> dict[str, int]:
    notenspiegel: dict[float, int] = {}
    for student in students:
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
