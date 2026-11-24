import json
import os
import tempfile
from school_management_system import SchoolManagementSystem

with tempfile.TemporaryDirectory() as folder:
    path = os.path.join(folder, "data.json")
    app = SchoolManagementSystem(path)
    app.data["grades"]["1"] = {"id": "1", "name": "JuniorII"}
    app.data["students"]["8011"] = {"id": "8011", "name": "Test Student", "status": "JuniorII", "date_of_birth": "2008-01-01", "gender": "X", "phone": "000"}
    app.data["enrollments"].append({"student_id": "8011", "grade": "Grade 10", "date": "2026-11-04"})
    assert app.save_data()
    restored = SchoolManagementSystem(path)
    assert restored.data["students"]["8011"]["name"] == "Test Student"
    assert len(restored.data["enrollments"]) == 1
    duplicate_count = sum(1 for e in restored.data["enrollments"] if e["student_id"] == "8011" and e["status"] == "Grade 10")
    assert duplicate_count == 1
    print("PASS: persistence, JSON structure, and duplicate-enrollment invariant")
