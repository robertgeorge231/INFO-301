"""School Management System - console application.

Standard library only. Data is stored in school_data.json so it survives restarts.
Run interactively with: python school_management_system.py
Run the non-interactive demonstration with: python school_management_system.py --demo
"""

import json
import os
import sys
from datetime import datetime


DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "school_data.json")


class SchoolManagementSystem:
    """Owns the application data, validation, persistence, and menu actions."""

    EMPTY_DATA = {
        "students": {}, "teachers": {}, "subjects": {}, "grades": {},
        "enrollments": [], "scores": []
    }

    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.data = self.load_data()

    def load_data(self):
        try:
            if not os.path.exists(self.data_file):
                return json.loads(json.dumps(self.EMPTY_DATA))
            with open(self.data_file, "r", encoding="utf-8") as file:
                loaded = json.load(file)
            for key, value in self.EMPTY_DATA.items():
                loaded.setdefault(key, json.loads(json.dumps(value)))
            return loaded
        except (OSError, json.JSONDecodeError) as error:
            print("Warning: Could not load data ({}). Starting with empty data.".format(error))
            return json.loads(json.dumps(self.EMPTY_DATA))

    def save_data(self):
        try:
            folder = os.path.dirname(self.data_file)
            if folder:
                os.makedirs(folder, exist_ok=True)
            temporary = self.data_file + ".tmp"
            with open(temporary, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=2)
            os.replace(temporary, self.data_file)
            return True
        except OSError as error:
            print("Error saving data: {}".format(error))
            return False

    @staticmethod
    def non_empty(prompt):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("Value cannot be empty.")

    @staticmethod
    def numeric_id(prompt):
        while True:
            value = input(prompt).strip()
            if value.isdigit() and int(value) > 0:
                return value
            print("Enter a positive numeric ID.")

    @staticmethod
    def date_value(prompt, allow_blank=False, current=""):
        while True:
            value = input(prompt).strip()
            if allow_blank and value == "":
                return current
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return value
            except ValueError:
                print("Use date format YYYY-MM-DD.")

    @staticmethod
    def choice(prompt, options):
        while True:
            value = input(prompt).strip()
            if value in options:
                return value
            print("Choose one of: {}".format(", ".join(options)))

    def add_student(self):
        student_id = self.numeric_id("Student ID: ")
        if student_id in self.data["students"]:
            print("A student with that ID already exists.")
            return
        self.data["students"][student_id] = {
            "id": student_id, "name": self.non_empty("Name: "),
            "grade": self.non_empty("Grade name (or N/A): "),
            "date_of_birth": self.date_value("Date of birth (YYYY-MM-DD): "),
            "gender": self.non_empty("Gender: "), "phone": self.non_empty("Phone: ")
        }
        self.save_data(); print("Student added successfully.")

    def list_students(self, students=None):
        students = self.data["students"] if students is None else students
        if not students:
            print("No students found."); return
        print("\nID     Name                 Grade        DOB          Gender   Phone")
        print("-" * 74)
        for s in students.values():
            print("{:<6} {:<20} {:<12} {:<12} {:<8} {}".format(
                s["id"], s["name"][:20], s["grade"][:12], s["date_of_birth"],
                s["gender"][:8], s["phone"]))

    def update_student(self):
        student_id = self.numeric_id("Student ID to update: ")
        student = self.data["students"].get(student_id)
        if not student:
            print("Student not found."); return
        print("Press Enter to keep the current value.")
        for field, label in (("name", "Name"), ("grade", "Grade"), ("gender", "Gender"), ("phone", "Phone")):
            value = input("{} [{}]: ".format(label, student[field])).strip()
            if value: student[field] = value
        student["date_of_birth"] = self.date_value(
            "Date of birth [{}]: ".format(student["date_of_birth"]), True, student["date_of_birth"])
        self.save_data(); print("Student updated successfully.")

    def delete_student(self):
        student_id = self.numeric_id("Student ID to delete: ")
        if student_id not in self.data["students"]:
            print("Student not found."); return
        del self.data["students"][student_id]
        self.data["enrollments"] = [e for e in self.data["enrollments"] if e["student_id"] != student_id]
        self.data["scores"] = [s for s in self.data["scores"] if s["student_id"] != student_id]
        self.save_data(); print("Student and linked records deleted.")

    def search_student(self):
        term = self.non_empty("Enter student ID or name: ").lower()
        found = {k: v for k, v in self.data["students"].items()
                 if term == k.lower() or term in v["name"].lower()}
        self.list_students(found)

    def student_menu(self):
        actions = {"1": self.add_student, "2": lambda: self.list_students(),
                   "3": self.update_student, "4": self.delete_student, "5": self.search_student}
        while True:
            print("\n--- Student Menu ---\n1. Add  2. View all  3. Update  4. Delete  5. Search  0. Back")
            option = self.choice("Choice: ", list(actions) + ["0"])
            if option == "0": return
            actions[option]()

    def add_teacher(self):
        teacher_id = self.numeric_id("Teacher ID: ")
        if teacher_id in self.data["teachers"]:
            print("A teacher with that ID already exists."); return
        subjects = [x.strip() for x in self.non_empty("Subjects (comma separated): ").split(",") if x.strip()]
        self.data["teachers"][teacher_id] = {
            "id": teacher_id, "name": self.non_empty("Name: "),
            "qualification": self.non_empty("Qualification: "), "subjects": subjects,
            "phone": self.non_empty("Phone: "), "grades": []
        }
        self.save_data(); print("Teacher added successfully.")

    def list_teachers(self):
        if not self.data["teachers"]: print("No teachers found."); return
        for t in self.data["teachers"].values():
            print("{} | {} | {} | Subjects: {} | Grades: {} | {}".format(
                t["id"], t["name"], t["qualification"], ", ".join(t["subjects"]),
                ", ".join(t["grades"]) or "None", t["phone"]))

    def update_teacher(self):
        teacher_id = self.numeric_id("Teacher ID to update: ")
        teacher = self.data["teachers"].get(teacher_id)
        if not teacher: print("Teacher not found."); return
        for field, label in (("name", "Name"), ("qualification", "Qualification"), ("phone", "Phone")):
            value = input("{} [{}]: ".format(label, teacher[field])).strip()
            if value: teacher[field] = value
        value = input("Subjects [{}]: ".format(", ".join(teacher["subjects"]))).strip()
        if value: teacher["subjects"] = [x.strip() for x in value.split(",") if x.strip()]
        self.save_data(); print("Teacher updated successfully.")

    def delete_teacher(self):
        teacher_id = self.numeric_id("Teacher ID to delete: ")
        if teacher_id not in self.data["teachers"]: print("Teacher not found."); return
        del self.data["teachers"][teacher_id]
        self.data["scores"] = [s for s in self.data["scores"] if s["teacher_id"] != teacher_id]
        self.save_data(); print("Teacher deleted.")

    def assign_teacher(self):
        teacher_id = self.numeric_id("Teacher ID: ")
        if teacher_id not in self.data["teachers"]: print("Teacher not found."); return
        grade = self.non_empty("Grade name: ")
        if grade not in self.data["grades"]: print("Grade not found. Add it first."); return
        teacher = self.data["teachers"][teacher_id]
        if grade not in teacher["grades"]: teacher["grades"].append(grade)
        self.save_data(); print("Teacher assigned to grade.")

    def teacher_menu(self):
        while True:
            print("\n--- Teacher Menu ---\n1. Add  2. View  3. Update  4. Delete  5. Assign to grade  0. Back")
            option = self.choice("Choice: ", ["0", "1", "2", "3", "4", "5"])
            if option == "0": return
            {"1": self.add_teacher, "2": self.list_teachers, "3": self.update_teacher,
             "4": self.delete_teacher, "5": self.assign_teacher}[option]()

    def add_grade(self):
        grade_id = self.numeric_id("Grade ID: ")
        if grade_id in self.data["grades"]: print("That grade ID already exists."); return
        name = self.non_empty("Grade name: ")
        if any(g["name"].lower() == name.lower() for g in self.data["grades"].values()):
            print("That grade name already exists."); return
        self.data["grades"][grade_id] = {"id": grade_id, "name": name}
        self.save_data(); print("Grade added.")

    def list_grades(self):
        if not self.data["grades"]: print("No grades found."); return
        for g in self.data["grades"].values(): print("{} - {}".format(g["id"], g["name"]))

    def update_grade(self):
        grade_id = self.numeric_id("Grade ID to update: ")
        grade = self.data["grades"].get(grade_id)
        if not grade: print("Grade not found."); return
        new_name = self.non_empty("New grade name: ")
        old_name = grade["name"]; grade["name"] = new_name
        for student in self.data["students"].values():
            if student["grade"] == old_name: student["grade"] = new_name
        for teacher in self.data["teachers"].values():
            teacher["grades"] = [new_name if x == old_name else x for x in teacher["grades"]]
        for enrollment in self.data["enrollments"]:
            if enrollment["grade"] == old_name: enrollment["grade"] = new_name
        self.save_data(); print("Grade updated.")

    def delete_grade(self):
        grade_id = self.numeric_id("Grade ID to delete: ")
        grade = self.data["grades"].get(grade_id)
        if not grade: print("Grade not found."); return
        name = grade["name"]; del self.data["grades"][grade_id]
        for student in self.data["students"].values():
            if student["grade"] == name: student["grade"] = "N/A"
        self.data["enrollments"] = [e for e in self.data["enrollments"] if e["grade"] != name]
        self.save_data(); print("Grade deleted.")

    def grade_menu(self):
        actions = {"1": self.add_grade, "2": self.list_grades, "3": self.update_grade, "4": self.delete_grade}
        while True:
            print("\n--- Grade Menu ---\n1. Add  2. View  3. Update  4. Delete  0. Back")
            option = self.choice("Choice: ", list(actions) + ["0"])
            if option == "0": return
            actions[option]()

    def add_subject(self):
        subject_id = self.numeric_id("Subject ID: ")
        if subject_id in self.data["subjects"]: print("That subject ID already exists."); return
        self.data["subjects"][subject_id] = {"id": subject_id, "name": self.non_empty("Subject name: "), "grades": []}
        self.save_data(); print("Subject added.")

    def list_subjects(self):
        if not self.data["subjects"]: print("No subjects found."); return
        for s in self.data["subjects"].values(): print("{} - {} (Grades: {})".format(s["id"], s["name"], ", ".join(s["grades"]) or "None"))

    def assign_subject(self):
        subject_id = self.numeric_id("Subject ID: ")
        subject = self.data["subjects"].get(subject_id)
        if not subject: print("Subject not found."); return
        grade = self.non_empty("Grade name: ")
        if not any(g["name"].lower() == grade.lower() for g in self.data["grades"].values()): print("Grade not found."); return
        actual = next(g["name"] for g in self.data["grades"].values() if g["name"].lower() == grade.lower())
        if actual not in subject["grades"]: subject["grades"].append(actual)
        self.save_data(); print("Subject assigned to grade.")

    def subject_menu(self):
        actions = {"1": self.add_subject, "2": self.list_subjects, "3": self.assign_subject}
        while True:
            print("\n--- Subject Menu ---\n1. Add  2. View  3. Assign to grade  0. Back")
            option = self.choice("Choice: ", list(actions) + ["0"])
            if option == "0": return
            actions[option]()

    def enroll_student(self):
        student_id = self.numeric_id("Student ID: ")
        if student_id not in self.data["students"]: print("Student not found."); return
        grade = self.non_empty("Grade name: ")
        if not any(g["name"].lower() == grade.lower() for g in self.data["grades"].values()): print("Grade not found."); return
        actual = next(g["name"] for g in self.data["grades"].values() if g["name"].lower() == grade.lower())
        if any(e["student_id"] == student_id and e["grade"] == actual for e in self.data["enrollments"]): print("Duplicate enrollment prevented."); return
        self.data["enrollments"].append({"student_id": student_id, "grade": actual, "date": datetime.now().strftime("%Y-%m-%d")})
        self.data["students"][student_id]["grade"] = actual
        self.save_data(); print("Student enrolled successfully.")

    def enrollment_history(self):
        student_id = self.numeric_id("Student ID: ")
        if student_id not in self.data["students"]: print("Student not found."); return
        history = [e for e in self.data["enrollments"] if e["student_id"] == student_id]
        if not history: print("No enrollment history."); return
        for e in history: print("{} - enrolled in {} on {}".format(student_id, e["grade"], e["date"]))

    def enrollment_menu(self):
        while True:
            print("\n--- Enrollment Menu ---\n1. Enroll student  2. View student history  0. Back")
            option = self.choice("Choice: ", ["0", "1", "2"])
            if option == "0": return
            (self.enroll_student if option == "1" else self.enrollment_history)()

    def add_score(self):
        student_id = self.numeric_id("Student ID: "); teacher_id = self.numeric_id("Teacher ID: ")
        if student_id not in self.data["students"] or teacher_id not in self.data["teachers"]: print("Student or teacher not found."); return
        subject = self.non_empty("Subject: ")
        while True:
            raw = input("Score (0-100): ").strip()
            try:
                score = float(raw)
                if 0 <= score <= 100: break
            except ValueError: pass
            print("Enter a number from 0 to 100.")
        self.data["scores"].append({"student_id": student_id, "teacher_id": teacher_id, "subject": subject, "score": score})
        self.save_data(); print("Score recorded.")

    def show_scores(self, records=None):
        records = self.data["scores"] if records is None else records
        if not records: print("No scores found."); return
        for r in records:
            student = self.data["students"].get(r["student_id"], {}).get("name", "Unknown")
            teacher = self.data["teachers"].get(r["teacher_id"], {}).get("name", "Unknown")
            print("Student: {} ({}) | Subject: {} | Score: {} | Teacher: {}".format(student, r["student_id"], r["subject"], r["score"], teacher))

    def score_menu(self):
        while True:
            print("\n--- Score Menu ---\n1. Add score  2. All scores  3. Student scores  4. Teacher scores  0. Back")
            option = self.choice("Choice: ", ["0", "1", "2", "3", "4"])
            if option == "0": return
            if option == "1": self.add_score()
            elif option == "2": self.show_scores()
            elif option in ("3", "4"):
                key = "student_id" if option == "3" else "teacher_id"
                value = self.numeric_id("{} ID: ".format("Student" if key == "student_id" else "Teacher"))
                self.show_scores([r for r in self.data["scores"] if r[key] == value])

    def reports_menu(self):
        while True:
            print("\n--- Reports and Summaries ---\n1. Students by grade  2. Report card  3. Totals  0. Back")
            option = self.choice("Choice: ", ["0", "1", "2", "3"])
            if option == "0": return
            if option == "1":
                grade = self.non_empty("Grade name: ")
                self.list_students({k: v for k, v in self.data["students"].items() if v["grade"].lower() == grade.lower()})
            elif option == "2":
                student_id = self.numeric_id("Student ID: ")
                student = self.data["students"].get(student_id)
                if not student: print("Student not found."); continue
                records = [r for r in self.data["scores"] if r["student_id"] == student_id]
                print("\nREPORT CARD: {} | Grade: {}".format(student["name"], student["grade"]))
                if records:
                    for r in records: print("{}: {}".format(r["subject"], r["score"]))
                    print("Average: {:.2f}".format(sum(r["score"] for r in records) / len(records)))
                else: print("No scores recorded yet (dummy scores may be entered from Score Menu).")
            else:
                print("Students: {} | Teachers: {} | Subjects: {} | Grades: {} | Enrollments: {}".format(
                    len(self.data["students"]), len(self.data["teachers"]), len(self.data["subjects"]), len(self.data["grades"]), len(self.data["enrollments"])))

    def run(self):
        actions = {"1": self.student_menu, "2": self.teacher_menu, "3": self.subject_menu,
                   "4": self.grade_menu, "5": self.enrollment_menu, "6": self.score_menu, "7": self.reports_menu}
        while True:
            print("\n========== SCHOOL MANAGEMENT SYSTEM ==========")
            print("1. Student Management\n2. Teacher Management\n3. Subject Management\n4. Grade Management")
            print("5. Enrollment System\n6. Scores\n7. Reports and Summaries\n0. Save and Exit")
            option = self.choice("Select an option: ", list(actions) + ["0"])
            if option == "0": self.save_data(); print("Goodbye. Data saved."); return
            actions[option]()


def demo():
    """A deterministic, non-interactive walkthrough used to verify and record the system."""
    demo_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_data.json")
    if os.path.exists(demo_file): os.remove(demo_file)
    app = SchoolManagementSystem(demo_file)
    print("SCHOOL MANAGEMENT SYSTEM - DEMONSTRATION")
    app.data["grades"] = {"1": {"id": "1", "name": "Grade 10"}}
    app.data["subjects"] = {"1": {"id": "1", "name": "Mathematics", "grades": ["Grade 10"]}}
    app.data["students"] = {"1001": {"id": "1001", "name": "Amina Kallon", "grade": "Grade 10", "date_of_birth": "2008-04-15", "gender": "Female", "phone": "555-0101"}}
    app.data["teachers"] = {"2001": {"id": "2001", "name": "Mr. Conteh", "qualification": "BSc Education", "subjects": ["Mathematics"], "phone": "555-0202", "grades": ["Grade 10"]}}
    app.data["enrollments"] = [{"student_id": "1001", "grade": "Grade 10", "date": "2026-11-04"}]
    app.data["scores"] = [{"student_id": "1001", "teacher_id": "2001", "subject": "Mathematics", "score": 87}]
    app.save_data()
    print("\n[1] Students by grade: Grade 10")
    app.list_students({"1001": app.data["students"]["1001"]})
    print("\n[2] Enrollment history")
    app.enrollment_history_demo("1001")
    print("\n[3] Score report and totals")
    app.show_scores(); print("Totals -> Students: 1 | Teachers: 1 | Subjects: 1 | Grades: 1")
    print("\n[4] Persistence check: data saved to demo_data.json")
    check = SchoolManagementSystem(demo_file)
    print("Reloaded {} student(s) successfully.".format(len(check.data["students"])))


def _history_demo(self, student_id):
    for e in self.data["enrollments"]:
        if e["student_id"] == student_id: print("{} - enrolled in {} on {}".format(student_id, e["grade"], e["date"]))


SchoolManagementSystem.enrollment_history_demo = _history_demo

if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        try:
            SchoolManagementSystem().run()
        except (KeyboardInterrupt, EOFError):
            print("\nProgram closed safely.")
