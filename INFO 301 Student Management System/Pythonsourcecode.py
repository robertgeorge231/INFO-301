"""
School Management System

A console-based school management application using JSON files for persistence.
Only Python's standard library is used.

Run:
    python school_management_system.py

The program automatically creates data.json in the same directory on first run.
"""

import json
import os
import random
from datetime import datetime


DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

DEFAULT_DATA = {
    "students": [],
    "teachers": [],
    "subjects": [],
    "grades": [],
    "enrollments": [],
    "scores": []
}


class SchoolManagementSystem:
    """Main application class responsible for data, persistence, and menus."""

    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.data = self.load_data()

    # ---------------------------- Persistence ----------------------------

    def load_data(self):
        """Load application data from JSON, creating a clean structure if needed."""
        if not os.path.exists(self.data_file):
            return {key: list(value) for key, value in DEFAULT_DATA.items()}

        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                loaded = json.load(file)
            data = {key: loaded.get(key, []) for key in DEFAULT_DATA}
            return data
        except (json.JSONDecodeError, OSError) as error:
            print(f"Warning: Could not load data ({error}). Starting with empty data.")
            return {key: list(value) for key, value in DEFAULT_DATA.items()}

    def save_data(self):
        """Save all application data to JSON."""
        try:
            folder = os.path.dirname(self.data_file)
            if folder:
                os.makedirs(folder, exist_ok=True)
            temporary_file = self.data_file + ".tmp"
            with open(temporary_file, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4)
            os.replace(temporary_file, self.data_file)
        except OSError as error:
            print(f"Error: Could not save data: {error}")

    # ---------------------------- Input helpers --------------------------

    @staticmethod
    def pause():
        input("\nPress Enter to continue...")

    @staticmethod
    def get_non_empty(prompt):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("This field cannot be empty.")

    @staticmethod
    def get_id(prompt="Enter numeric ID: "):
        while True:
            value = input(prompt).strip()
            if value.isdigit() and int(value) > 0:
                return value
            print("ID must be a positive whole number.")

    @staticmethod
    def get_optional_id(prompt):
        while True:
            value = input(prompt).strip()
            if value == "":
                return None
            if value.isdigit() and int(value) > 0:
                return value
            print("Enter a positive whole number, or press Enter to keep the current value.")

    @staticmethod
    def get_date(prompt="Date of birth (YYYY-MM-DD): "):
        while True:
            value = input(prompt).strip()
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return value
            except ValueError:
                print("Invalid date. Use the format YYYY-MM-DD.")

    @staticmethod
    def get_optional_date(prompt):
        while True:
            value = input(prompt).strip()
            if value == "":
                return None
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return value
            except ValueError:
                print("Invalid date. Use YYYY-MM-DD, or press Enter to keep the current value.")

    @staticmethod
    def get_phone(prompt="Phone: "):
        while True:
            value = input(prompt).strip()
            cleaned = value.replace("+", "", 1).replace(" ", "").replace("-", "")
            if cleaned.isdigit() and len(cleaned) >= 7:
                return value
            print("Enter a valid phone number containing at least 7 digits.")

    @staticmethod
    def get_optional_phone(prompt):
        while True:
            value = input(prompt).strip()
            if value == "":
                return None
            cleaned = value.replace("+", "", 1).replace(" ", "").replace("-", "")
            if cleaned.isdigit() and len(cleaned) >= 7:
                return value
            print("Enter a valid phone number, or press Enter to keep the current value.")

    @staticmethod
    def get_gender(prompt="Gender: "):
        while True:
            value = input(prompt).strip().title()
            if value in {"Male", "Female", "Other"}:
                return value
            print("Choose Male, Female, or Other.")

    @staticmethod
    def get_score(prompt="Score (0-100): "):
        while True:
            try:
                value = float(input(prompt).strip())
                if 0 <= value <= 100:
                    return round(value, 2)
            except ValueError:
                pass
            print("Enter a number from 0 to 100.")

    @staticmethod
    def choose_from_list(items, label, display_key="name"):
        if not items:
            print(f"No {label} found.")
            return None
        for index, item in enumerate(items, start=1):
            print(f"{index}. {item.get(display_key, item)}")
        while True:
            choice = input(f"Select {label} number (0 to cancel): ").strip()
            if choice == "0":
                return None
            if choice.isdigit() and 1 <= int(choice) <= len(items):
                return items[int(choice) - 1]
            print("Invalid selection.")

    def find_by_id(self, collection, item_id):
        return next((item for item in self.data[collection] if item["id"] == item_id), None)

    def unique_id(self, collection, item_id):
        return self.find_by_id(collection, item_id) is None

    # ---------------------------- Display helpers ------------------------

    @staticmethod
    def print_table(rows, columns):
        if not rows:
            print("No records found.")
            return
        widths = {key: len(title) for key, title in columns}
        for row in rows:
            for key, _ in columns:
                widths[key] = max(widths[key], len(str(row.get(key, ""))))
        header = " | ".join(title.ljust(widths[key]) for key, title in columns)
        print(header)
        print("-" * len(header))
        for row in rows:
            print(" | ".join(str(row.get(key, "")).ljust(widths[key]) for key, _ in columns))

    def student_name(self, student_id):
        student = self.find_by_id("students", student_id)
        return student["name"] if student else f"Unknown student ({student_id})"

    def teacher_name(self, teacher_id):
        teacher = self.find_by_id("teachers", teacher_id)
        return teacher["name"] if teacher else f"Unknown teacher ({teacher_id})"

    def subject_name(self, subject_id):
        subject = self.find_by_id("subjects", subject_id)
        return subject["name"] if subject else f"Unknown subject ({subject_id})"

    def grade_name(self, grade_id):
        grade = self.find_by_id("grades", grade_id)
        return grade["name"] if grade else f"Unknown grade ({grade_id})"

    # ---------------------------- Student management ---------------------

    def add_student(self):
        print("\n--- Add Student ---")
        student_id = self.get_id("Student ID: ")
        if not self.unique_id("students", student_id):
            print("A student with that ID already exists.")
            return
        student = {
            "id": student_id,
            "name": self.get_non_empty("Name: "),
            "grade": self.get_non_empty("Current grade (optional text): "),
            "date_of_birth": self.get_date(),
            "gender": self.get_gender(),
            "phone": self.get_phone()
        }
        self.data["students"].append(student)
        self.save_data()
        print("Student added successfully.")

    def list_students(self, students=None):
        students = self.data["students"] if students is None else students
        rows = []
        for student in students:
            enrolled = [self.grade_name(e["grade_id"]) for e in self.data["enrollments"] if e["student_id"] == student["id"]]
            rows.append({
                "id": student["id"], "name": student["name"],
                "grade": ", ".join(enrolled) or student.get("grade", ""),
                "date_of_birth": student["date_of_birth"],
                "gender": student["gender"], "phone": student["phone"]
            })
        self.print_table(rows, [("id", "ID"), ("name", "Name"), ("grade", "Grade"),
                                ("date_of_birth", "Date of Birth"), ("gender", "Gender"), ("phone", "Phone")])

    def update_student(self):
        print("\n--- Update Student ---")
        student = self.find_by_id("students", self.get_id("Student ID: "))
        if not student:
            print("Student not found.")
            return
        print("Press Enter to keep the current value.")
        name = input(f"Name [{student['name']}]: ").strip()
        grade = input(f"Grade text [{student.get('grade', '')}]: ").strip()
        dob = self.get_optional_date(f"Date of birth [{student['date_of_birth']}]: ")
        gender = input(f"Gender [{student['gender']}] (Male/Female/Other): ").strip().title()
        phone = self.get_optional_phone(f"Phone [{student['phone']}]: ")
        if name:
            student["name"] = name
        if grade:
            student["grade"] = grade
        if dob:
            student["date_of_birth"] = dob
        if gender:
            if gender in {"Male", "Female", "Other"}:
                student["gender"] = gender
            else:
                print("Invalid gender; previous value retained.")
        if phone:
            student["phone"] = phone
        self.save_data()
        print("Student updated successfully.")

    def delete_student(self):
        student_id = self.get_id("Student ID to delete: ")
        student = self.find_by_id("students", student_id)
        if not student:
            print("Student not found.")
            return
        self.data["students"].remove(student)
        self.data["enrollments"] = [e for e in self.data["enrollments"] if e["student_id"] != student_id]
        self.data["scores"] = [s for s in self.data["scores"] if s["student_id"] != student_id]
        self.save_data()
        print("Student and related enrollment/score records deleted.")

    def search_student(self):
        term = self.get_non_empty("Enter student ID or name: ").lower()
        matches = [s for s in self.data["students"] if term in s["id"].lower() or term in s["name"].lower()]
        self.list_students(matches)

    # ---------------------------- Teacher management ---------------------

    def add_teacher(self):
        print("\n--- Add Teacher ---")
        teacher_id = self.get_id("Teacher ID: ")
        if not self.unique_id("teachers", teacher_id):
            print("A teacher with that ID already exists.")
            return
        subjects = self.get_non_empty("Subjects taught (comma-separated): ")
        teacher = {
            "id": teacher_id,
            "name": self.get_non_empty("Name: "),
            "qualification": self.get_non_empty("Qualification: "),
            "subjects": [s.strip() for s in subjects.split(",") if s.strip()],
            "phone": self.get_phone()
        }
        self.data["teachers"].append(teacher)
        self.save_data()
        print("Teacher added successfully.")

    def list_teachers(self):
        rows = [{"id": t["id"], "name": t["name"], "qualification": t["qualification"],
                 "subjects": ", ".join(t["subjects"]), "phone": t["phone"]}
                for t in self.data["teachers"]]
        self.print_table(rows, [("id", "ID"), ("name", "Name"), ("qualification", "Qualification"),
                                ("subjects", "Subjects"), ("phone", "Phone")])
        if self.data["teachers"]:
            print("\nTeacher-to-grade assignments:")
            for teacher in self.data["teachers"]:
                grades = [self.grade_name(g) for g in teacher.get("grade_ids", [])]
                print(f"- {teacher['name']}: {', '.join(grades) or 'None'}")

    def update_teacher(self):
        teacher = self.find_by_id("teachers", self.get_id("Teacher ID: "))
        if not teacher:
            print("Teacher not found.")
            return
        print("Press Enter to keep the current value.")
        name = input(f"Name [{teacher['name']}]: ").strip()
        qualification = input(f"Qualification [{teacher['qualification']}]: ").strip()
        subjects = input(f"Subjects comma-separated [{', '.join(teacher['subjects'])}]: ").strip()
        phone = self.get_optional_phone(f"Phone [{teacher['phone']}]: ")
        if name:
            teacher["name"] = name
        if qualification:
            teacher["qualification"] = qualification
        if subjects:
            teacher["subjects"] = [s.strip() for s in subjects.split(",") if s.strip()]
        if phone:
            teacher["phone"] = phone
        self.save_data()
        print("Teacher updated successfully.")

    def delete_teacher(self):
        teacher_id = self.get_id("Teacher ID to delete: ")
        teacher = self.find_by_id("teachers", teacher_id)
        if not teacher:
            print("Teacher not found.")
            return
        self.data["teachers"].remove(teacher)
        self.data["scores"] = [s for s in self.data["scores"] if s.get("teacher_id") != teacher_id]
        self.save_data()
        print("Teacher deleted successfully.")

    def assign_teacher_to_grade(self):
        teacher = self.choose_from_list(self.data["teachers"], "teacher")
        grade = self.choose_from_list(self.data["grades"], "grade")
        if not teacher or not grade:
            return
        teacher.setdefault("grade_ids", [])
        if grade["id"] not in teacher["grade_ids"]:
            teacher["grade_ids"].append(grade["id"])
            self.save_data()
            print("Teacher assigned to grade.")
        else:
            print("Teacher is already assigned to that grade.")

    # ---------------------------- Subjects and grades --------------------

    def add_subject(self):
        subject_id = self.get_id("Subject ID: ")
        if not self.unique_id("subjects", subject_id):
            print("A subject with that ID already exists.")
            return
        subject = {"id": subject_id, "name": self.get_non_empty("Subject name: "), "grade_ids": []}
        self.data["subjects"].append(subject)
        self.save_data()
        print("Subject added successfully.")

    def list_subjects(self):
        rows = [{"id": s["id"], "name": s["name"],
                 "grades": ", ".join(self.grade_name(g) for g in s.get("grade_ids", [])) or "None"}
                for s in self.data["subjects"]]
        self.print_table(rows, [("id", "ID"), ("name", "Subject"), ("grades", "Assigned Grades")])

    def assign_subject_to_grade(self):
        subject = self.choose_from_list(self.data["subjects"], "subject")
        grade = self.choose_from_list(self.data["grades"], "grade")
        if not subject or not grade:
            return
        subject.setdefault("grade_ids", [])
        if grade["id"] not in subject["grade_ids"]:
            subject["grade_ids"].append(grade["id"])
            self.save_data()
            print("Subject assigned to grade.")
        else:
            print("Subject is already assigned to that grade.")

    def add_grade(self):
        grade_id = self.get_id("Grade ID: ")
        if not self.unique_id("grades", grade_id):
            print("A grade with that ID already exists.")
            return
        grade = {"id": grade_id, "name": self.get_non_empty("Grade name: "),
                 "description": input("Description (optional): ").strip()}
        self.data["grades"].append(grade)
        self.save_data()
        print("Grade added successfully.")

    def list_grades(self):
        self.print_table(self.data["grades"], [("id", "ID"), ("name", "Grade"), ("description", "Description")])

    def update_grade(self):
        grade = self.find_by_id("grades", self.get_id("Grade ID: "))
        if not grade:
            print("Grade not found.")
            return
        name = input(f"Grade name [{grade['name']}]: ").strip()
        description = input(f"Description [{grade.get('description', '')}]: ").strip()
        if name:
            grade["name"] = name
        if description:
            grade["description"] = description
        self.save_data()
        print("Grade updated successfully.")

    def delete_grade(self):
        grade_id = self.get_id("Grade ID to delete: ")
        grade = self.find_by_id("grades", grade_id)
        if not grade:
            print("Grade not found.")
            return
        self.data["grades"].remove(grade)
        self.data["enrollments"] = [e for e in self.data["enrollments"] if e["grade_id"] != grade_id]
        for subject in self.data["subjects"]:
            subject["grade_ids"] = [g for g in subject.get("grade_ids", []) if g != grade_id]
        for teacher in self.data["teachers"]:
            teacher["grade_ids"] = [g for g in teacher.get("grade_ids", []) if g != grade_id]
        self.save_data()
        print("Grade and related assignments deleted.")

    # ---------------------------- Enrollment -----------------------------

    def enroll_student(self):
        student = self.choose_from_list(self.data["students"], "student")
        grade = self.choose_from_list(self.data["grades"], "grade")
        if not student or not grade:
            return
        duplicate = any(e["student_id"] == student["id"] and e["grade_id"] == grade["id"]
                        for e in self.data["enrollments"])
        if duplicate:
            print("Duplicate enrollment prevented: student is already in that grade.")
            return
        enrollment = {
            "student_id": student["id"], "grade_id": grade["id"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data["enrollments"].append(enrollment)
        self.save_data()
        print("Student enrolled successfully.")

    def view_enrollments(self):
        rows = [{"student": self.student_name(e["student_id"]), "grade": self.grade_name(e["grade_id"]),
                 "date": e["date"]} for e in self.data["enrollments"]]
        self.print_table(rows, [("student", "Student"), ("grade", "Grade"), ("date", "Enrollment Date")])

    def enrollment_history(self):
        student_id = self.get_id("Student ID: ")
        if not self.find_by_id("students", student_id):
            print("Student not found.")
            return
        rows = [{"grade": self.grade_name(e["grade_id"]), "date": e["date"]}
                for e in self.data["enrollments"] if e["student_id"] == student_id]
        print(f"Enrollment history for {self.student_name(student_id)}:")
        self.print_table(rows, [("grade", "Grade"), ("date", "Enrollment Date")])

    # ---------------------------- Scores ---------------------------------

    def record_score(self):
        student = self.choose_from_list(self.data["students"], "student")
        subject = self.choose_from_list(self.data["subjects"], "subject")
        teacher = self.choose_from_list(self.data["teachers"], "teacher")
        if not student or not subject or not teacher:
            return
        score_value = self.get_score()
        existing = next((s for s in self.data["scores"] if s["student_id"] == student["id"]
                         and s["subject_id"] == subject["id"] and s["teacher_id"] == teacher["id"]), None)
        if existing:
            existing["score"] = score_value
            existing["date"] = datetime.now().strftime("%Y-%m-%d")
            print("Existing score updated.")
        else:
            self.data["scores"].append({
                "student_id": student["id"], "subject_id": subject["id"],
                "teacher_id": teacher["id"], "score": score_value,
                "date": datetime.now().strftime("%Y-%m-%d")
            })
            print("Score recorded successfully.")
        self.save_data()

    def score_rows(self, scores):
        return [{"student": self.student_name(s["student_id"]), "subject": self.subject_name(s["subject_id"]),
                 "teacher": self.teacher_name(s["teacher_id"]), "score": s["score"], "date": s["date"]}
                for s in scores]

    def view_all_scores(self):
        rows = self.score_rows(self.data["scores"])
        self.print_table(rows, [("student", "Student"), ("subject", "Subject"),
                                ("teacher", "Teacher"), ("score", "Score"), ("date", "Date")])

    def view_student_scores(self):
        student_id = self.get_id("Student ID: ")
        if not self.find_by_id("students", student_id):
            print("Student not found.")
            return
        rows = self.score_rows([s for s in self.data["scores"] if s["student_id"] == student_id])
        self.print_table(rows, [("student", "Student"), ("subject", "Subject"),
                                ("teacher", "Teacher"), ("score", "Score"), ("date", "Date")])

    def view_teacher_scores(self):
        teacher_id = self.get_id("Teacher ID: ")
        if not self.find_by_id("teachers", teacher_id):
            print("Teacher not found.")
            return
        rows = self.score_rows([s for s in self.data["scores"] if s["teacher_id"] == teacher_id])
        self.print_table(rows, [("student", "Student"), ("subject", "Subject"),
                                ("teacher", "Teacher"), ("score", "Score"), ("date", "Date")])

    # ---------------------------- Reports --------------------------------

    def students_by_grade(self):
        grade = self.choose_from_list(self.data["grades"], "grade")
        if not grade:
            return
        student_ids = {e["student_id"] for e in self.data["enrollments"] if e["grade_id"] == grade["id"]}
        self.list_students([s for s in self.data["students"] if s["id"] in student_ids])

    def report_card(self):
        student = self.choose_from_list(self.data["students"], "student")
        if not student:
            return
        scores = [s for s in self.data["scores"] if s["student_id"] == student["id"]]
        if not scores:
            print("No recorded scores. Dummy scores will be generated for the report card.")
            enrolled_grade_ids = [e["grade_id"] for e in self.data["enrollments"] if e["student_id"] == student["id"]]
            subject_ids = [subject["id"] for subject in self.data["subjects"]
                           if set(subject.get("grade_ids", [])) & set(enrolled_grade_ids)]
            if not subject_ids:
                subject_ids = [subject["id"] for subject in self.data["subjects"]]
            scores = [{"student_id": student["id"], "subject_id": subject_id,
                       "teacher_id": "N/A", "score": random.randint(50, 95), "date": "Dummy"}
                      for subject_id in subject_ids]
        print(f"\nREPORT CARD: {student['name']} (ID: {student['id']})")
        print("=" * 55)
        total = sum(float(s["score"]) for s in scores)
        for score in scores:
            mark = float(score["score"])
            if mark >= 80:
                remark = "Excellent"
            elif mark >= 70:
                remark = "Very Good"
            elif mark >= 60:
                remark = "Good"
            elif mark >= 50:
                remark = "Pass"
            else:
                remark = "Needs Improvement"
            print(f"{self.subject_name(score['subject_id']):25} {mark:6.2f}  {remark}")
        average = total / len(scores) if scores else 0
        print("-" * 55)
        print(f"Average: {average:.2f}")
        print("Note: Scores marked Dummy are sample scores for demonstration.")

    def summary(self):
        print("\n--- School Summary ---")
        print(f"Total students: {len(self.data['students'])}")
        print(f"Total teachers: {len(self.data['teachers'])}")
        print(f"Total subjects: {len(self.data['subjects'])}")
        print(f"Total grades: {len(self.data['grades'])}")
        print(f"Total enrollments: {len(self.data['enrollments'])}")
        print(f"Total scores: {len(self.data['scores'])}")

    # ---------------------------- Menus ----------------------------------

    def student_menu(self):
        while True:
            print("\n===== STUDENT MENU =====")
            print("1. Add student\n2. View all students\n3. Update student")
            print("4. Delete student\n5. Search student\n0. Back")
            choice = input("Choose an option: ").strip()
            actions = {"1": self.add_student, "2": self.list_students, "3": self.update_student,
                       "4": self.delete_student, "5": self.search_student}
            if choice == "0":
                return
            action = actions.get(choice)
            if action:
                action()
                self.pause()
            else:
                print("Invalid option.")

    def teacher_menu(self):
        while True:
            print("\n===== TEACHER MENU =====")
            print("1. Add teacher\n2. View teachers\n3. Update teacher")
            print("4. Delete teacher\n5. Assign teacher to grade\n0. Back")
            choice = input("Choose an option: ").strip()
            actions = {"1": self.add_teacher, "2": self.list_teachers, "3": self.update_teacher,
                       "4": self.delete_teacher, "5": self.assign_teacher_to_grade}
            if choice == "0":
                return
            action = actions.get(choice)
            if action:
                action()
                self.pause()
            else:
                print("Invalid option.")

    def subject_menu(self):
        while True:
            print("\n===== SUBJECT MENU =====")
            print("1. Add subject\n2. View subjects\n3. Assign subject to grade\n0. Back")
            choice = input("Choose an option: ").strip()
            actions = {"1": self.add_subject, "2": self.list_subjects, "3": self.assign_subject_to_grade}
            if choice == "0":
                return
            action = actions.get(choice)
            if action:
                action()
                self.pause()
            else:
                print("Invalid option.")

    def grade_menu(self):
        while True:
            print("\n===== GRADE MENU =====")
            print("1. Add grade\n2. View grades\n3. Update grade\n4. Delete grade\n0. Back")
            choice = input("Choose an option: ").strip()
            actions = {"1": self.add_grade, "2": self.list_grades, "3": self.update_grade, "4": self.delete_grade}
            if choice == "0":
                return
            action = actions.get(choice)
            if action:
                action()
                self.pause()
            else:
                print("Invalid option.")

    def enrollment_menu(self):
        while True:
            print("\n===== ENROLLMENT MENU =====")
            print("1. Enroll student into grade\n2. View all enrollments\n3. Student enrollment history\n0. Back")
            choice = input("Choose an option: ").strip()
            actions = {"1": self.enroll_student, "2": self.view_enrollments, "3": self.enrollment_history}
            if choice == "0":
                return
            action = actions.get(choice)
            if action:
                action()
                self.pause()
            else:
                print("Invalid option.")

    def score_menu(self):
        while True:
            print("\n===== SCORE MENU =====")
            print("1. Record/update score\n2. View all scores")
            print("3. View scores for a student\n4. View scores for a teacher\n0. Back")
            choice = input("Choose an option: ").strip()
            actions = {"1": self.record_score, "2": self.view_all_scores,
                       "3": self.view_student_scores, "4": self.view_teacher_scores}
            if choice == "0":
                return
            action = actions.get(choice)
            if action:
                action()
                self.pause()
            else:
                print("Invalid option.")

    def reports_menu(self):
        while True:
            print("\n===== REPORTS AND SUMMARIES =====")
            print("1. List students by grade\n2. Generate student report card")
            print("3. View school totals\n0. Back")
            choice = input("Choose an option: ").strip()
            actions = {"1": self.students_by_grade, "2": self.report_card, "3": self.summary}
            if choice == "0":
                return
            action = actions.get(choice)
            if action:
                action()
                self.pause()
            else:
                print("Invalid option.")

    def run(self):
        print("=" * 60)
        print("       SCHOOL MANAGEMENT SYSTEM")
        print("=" * 60)
        while True:
            print("\n========== MAIN MENU ==========")
            print("1. Student Management")
            print("2. Teacher Management")
            print("3. Subject Management")
            print("4. Grade Management")
            print("5. Enrollment System")
            print("6. Score Management")
            print("7. Reports and Summaries")
            print("0. Save and Exit")
            choice = input("Choose an option: ").strip()
            actions = {"1": self.student_menu, "2": self.teacher_menu, "3": self.subject_menu,
                       "4": self.grade_menu, "5": self.enrollment_menu, "6": self.score_menu,
                       "7": self.reports_menu}
            if choice == "0":
                self.save_data()
                print("Data saved. Goodbye!")
                break
            action = actions.get(choice)
            if action:
                try:
                    action()
                except (EOFError, KeyboardInterrupt):
                    print("\nInput interrupted. Returning to the main menu.")
                except Exception as error:
                    print(f"An unexpected error occurred: {error}")
            else:
                print("Invalid option. Please choose a number from the menu.")


def main():
    try:
        SchoolManagementSystem().run()
    except (EOFError, KeyboardInterrupt):
        print("\nProgram closed. Existing saved data has not been lost.")


if __name__ == "__main__":
    main()
