#!/usr/bin/env python3

import sys
import random
from uuid import uuid4
from datetime import datetime, timedelta
from database import MongoDBConnection


def generate_id():
    return str(uuid4())


def seed_database():
    connection = MongoDBConnection.get_instance()
    db = connection.get_db()

    print("Clearing existing data...")
    collections = [
        "students", "teachers", "classes",
        "attendance", "assignments", "submissions", "exams"
    ]
    for col in collections:
        db[col].delete_many({})

    # ==================== TEACHERS ====================
    print("Seeding teachers...")
    teachers = []
    for i in range(15):
        teacher = {
            "_id": generate_id(),
            "name": f"Teacher {i}",
            "email": f"teacher{i}@school.com",
            "phone": f"9876543{i:03}",
            "designation": "Teacher",
            "department": random.choice(["Math", "Science", "English"]),
            "qualification": "B.Ed",
            "hire_date": datetime(2020, 1, 1)
        }
        teachers.append(teacher)

    db.teachers.insert_many(teachers)
    teacher_ids = [t["_id"] for t in teachers]

    # ==================== CLASSES ====================
    print("Seeding classes...")
    classes = []

    for grade in range(6, 9):  # Class 6–8
        for section in ["A", "B"]:
            cls = {
                "_id": generate_id(),
                "class_name": f"Class {grade}",
                "section": section,
                "teacher_id": random.choice(teacher_ids),
                "grade": grade,
                "student_count": 0,
                "room_number": str(100 + grade)
            }
            classes.append(cls)

    # ensure at least 15 classes
    while len(classes) < 15:
        classes.append({
            "_id": generate_id(),
            "class_name": f"Class {random.randint(6, 10)}",
            "section": random.choice(["A", "B"]),
            "teacher_id": random.choice(teacher_ids),
            "grade": random.randint(6, 10),
            "student_count": 0,
            "room_number": str(random.randint(100, 300))
        })

    db.classes.insert_many(classes)
    class_ids = [c["_id"] for c in classes]

    # ==================== STUDENTS ====================
    print("Seeding students...")
    students = []

    for i in range(150):  # lots of students
        cls = random.choice(classes)

        student = {
            "_id": generate_id(),
            "name": f"Student {i}",
            "email": f"student{i}@school.com",
            "phone": f"988000{i:04}",
            "class_id": cls["_id"],   # ✅ correct mapping
            "section": cls["section"],
            "roll_number": random.randint(1, 50),
            "enrollment_date": datetime(2023, 6, 1)
        }
        students.append(student)

    db.students.insert_many(students)
    student_ids = [s["_id"] for s in students]

    # ==================== ATTENDANCE ====================
    print("Seeding attendance...")
    attendance_records = []

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for student in students:
        for d in range(10):  # 10 days per student
            status = "Present" if random.random() > 0.2 else "Absent"

            attendance_records.append({
                "_id": generate_id(),
                "student_id": student["_id"],   # ✅ correct
                "class_id": student["class_id"], # ✅ correct
                "date": today - timedelta(days=d),
                "status": status,
                "remarks": None
            })

    db.attendance.insert_many(attendance_records)

    # ==================== ASSIGNMENTS ====================
    print("Seeding assignments...")
    assignments = []

    for cls in classes:
        for i in range(2):  # 2 per class → ensures >15 total
            assignment = {
                "_id": generate_id(),
                "title": f"Assignment {i}",
                "description": "Complete tasks",
                "class_id": cls["_id"],  # ✅ correct
                "teacher_id": cls["teacher_id"],
                "created_date": today - timedelta(days=2),
                "due_date": today + timedelta(days=random.randint(1, 7)),
                "total_marks": 100
            }
            assignments.append(assignment)

    db.assignments.insert_many(assignments)
    assignment_ids = [a["_id"] for a in assignments]

    # ==================== SUBMISSIONS ====================
    print("Seeding submissions...")
    submissions = []

    for assignment in assignments:
        class_students = [s for s in students if s["class_id"] == assignment["class_id"]]

        for student in random.sample(class_students, min(10, len(class_students))):
            submitted = random.random() > 0.3

            submissions.append({
                "_id": generate_id(),
                "assignment_id": assignment["_id"],  # ✅ correct
                "student_id": student["_id"],        # ✅ correct
                "submission_date": today if submitted else None,
                "marks_obtained": random.randint(40, 100) if submitted else None,
                "status": "Submitted" if submitted else "Pending"
            })

    db.submissions.insert_many(submissions)

    # ==================== EXAMS ====================
    print("Seeding exams...")
    exams = []

    subjects = ["Math", "Science", "English", "History"]

    for cls in classes:
        for subject in subjects[:2]:  # ensures >15 total
            exams.append({
                "_id": generate_id(),
                "exam_name": f"{subject} Exam",
                "class_id": cls["_id"],  # ✅ correct
                "date": today + timedelta(days=random.randint(5, 20)),
                "time": "10:00",
                "duration": 120,
                "total_marks": 100,
                "subject": subject
            })

    db.exams.insert_many(exams)

    # ==================== SUMMARY ====================
    print("\n✅ Database seeded successfully!")
    print(f"Teachers: {len(teachers)}")
    print(f"Classes: {len(classes)}")
    print(f"Students: {len(students)}")
    print(f"Attendance: {len(attendance_records)}")
    print(f"Assignments: {len(assignments)}")
    print(f"Submissions: {len(submissions)}")
    print(f"Exams: {len(exams)}")


if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)