#!/usr/bin/env python3
"""
Database seeding script to populate MongoDB with sample data for ERP system
"""

import sys
from datetime import datetime, timedelta
from database import MongoDBConnection
from bson import ObjectId
import random

def seed_database():
    """Seed database with sample data"""
    
    connection = MongoDBConnection.get_instance()
    db = connection.get_db()
    
    # Clear existing data
    print("Clearing existing data...")
    for collection_name in ["students", "teachers", "classes", "attendance", "assignments", "submissions", "exams"]:
        db[collection_name].delete_many({})
    
    # ==================== Seed Teachers ====================
    print("Seeding teachers...")
    teachers_data = [
        {
            "name": "Mr. Sharma",
            "email": "sharma@school.com",
            "phone": "9876543210",
            "designation": "Senior Teacher",
            "department": "Mathematics",
            "qualification": "B.Sc, B.Ed",
            "hire_date": datetime(2020, 1, 15)
        },
        {
            "name": "Ms. Patel",
            "email": "patel@school.com",
            "phone": "9876543211",
            "designation": "Teacher",
            "department": "English",
            "qualification": "B.A, B.Ed",
            "hire_date": datetime(2021, 6, 10)
        },
        {
            "name": "Mr. Gupta",
            "email": "gupta@school.com",
            "phone": "9876543212",
            "designation": "Teacher",
            "department": "Science",
            "qualification": "B.Sc, B.Ed",
            "hire_date": datetime(2019, 7, 20)
        },
        {
            "name": "Ms. Singh",
            "email": "singh@school.com",
            "phone": "9876543213",
            "designation": "Teacher",
            "department": "History",
            "qualification": "B.A, B.Ed",
            "hire_date": datetime(2022, 3, 1)
        }
    ]
    
    teacher_ids = []
    for teacher in teachers_data:
        result = db.teachers.insert_one(teacher)
        teacher_ids.append(str(result.inserted_id))
    print(f"✓ Inserted {len(teacher_ids)} teachers")
    
    # ==================== Seed Classes ====================
    print("Seeding classes...")
    classes_data = [
        {
            "class_name": "Class 6",
            "section": "A",
            "teacher_id": teacher_ids[0],
            "grade": 6,
            "student_count": 30,
            "room_number": "101"
        },
        {
            "class_name": "Class 6",
            "section": "B",
            "teacher_id": teacher_ids[1],
            "grade": 6,
            "student_count": 28,
            "room_number": "102"
        },
        {
            "class_name": "Class 7",
            "section": "A",
            "teacher_id": teacher_ids[2],
            "grade": 7,
            "student_count": 32,
            "room_number": "201"
        },
        {
            "class_name": "Class 7",
            "section": "B",
            "teacher_id": teacher_ids[3],
            "grade": 7,
            "student_count": 29,
            "room_number": "202"
        }
    ]
    
    class_ids = []
    for cls in classes_data:
        result = db.classes.insert_one(cls)
        class_ids.append(str(result.inserted_id))
    print(f"✓ Inserted {len(class_ids)} classes")
    
    # ==================== Seed Students ====================
    print("Seeding students...")
    student_names = [
        "Aarav Kumar", "Ananya Sharma", "Arjun Patel", "Aisha Roy",
        "Bhavesh Singh", "Beatrice Gupta", "Chahat Verma", "Chirag Desai",
        "Deepika Joshi", "Dhruv Reddy", "Esha Kapoor", "Ethan Malhotra",
        "Fatima Khan", "Faisal Ahmed", "Gasha Nair", "Gautam Bhat",
        "Harini Menon", "Harsh Mishra", "Isha Chattopadhyay", "Ivan Pereira",
        "Jaya Subramanian", "Jai Bakshi", "Kavya Iyer", "Kevin Tiwari",
        "Laila Hassan", "Liam Chopra", "Meera Saxena", "Mayank Rao",
        "Navya Kulkarni", "Neil Sharma"
    ]
    
    student_ids = []
    roll_num = 1
    for i, name in enumerate(student_names):
        class_idx = i % len(class_ids)
        student = {
            "name": name,
            "email": f"{name.lower().replace(' ', '.')}@school.com",
            "phone": f"988000{1000+i}",
            "class_id": class_ids[class_idx],
            "section": classes_data[class_idx]["section"],
            "roll_number": (i % 15) + 1,
            "enrollment_date": datetime(2023, 6, 1)
        }
        result = db.students.insert_one(student)
        student_ids.append(str(result.inserted_id))
    print(f"✓ Inserted {len(student_ids)} students")
    
    # ==================== Seed Attendance ====================
    print("Seeding attendance records...")
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    attendance_records = []
    
    for student_id in student_ids:
        student = db.students.find_one({"_id": ObjectId(student_id)})
        class_id = student["class_id"]
        
        # Last 10 days of attendance
        for days_ago in range(10):
            date = today - timedelta(days=days_ago)
            # 85% present, 15% absent
            status = "Present" if random.random() > 0.15 else "Absent"
            
            attendance_records.append({
                "student_id": student_id,
                "class_id": class_id,
                "date": date,
                "status": status,
                "remarks": None if status == "Present" else "Not marked"
            })
    
    db.attendance.insert_many(attendance_records)
    print(f"✓ Inserted {len(attendance_records)} attendance records")
    
    # ==================== Seed Assignments ====================
    print("Seeding assignments...")
    assignment_titles = [
        "Chapter 1-3 Exercises",
        "Essay on Climate Change",
        "Math Problem Set",
        "Science Project"
    ]
    
    assignments_data = []
    for class_id in class_ids:
        for i, title in enumerate(assignment_titles):
            due_date = today + timedelta(days=7+i*2)
            
            assignment = {
                "title": title,
                "description": f"Complete all problems in {title}",
                "class_id": class_id,
                "teacher_id": random.choice(teacher_ids),
                "created_date": today - timedelta(days=2),
                "due_date": due_date,
                "total_marks": 10
            }
            assignments_data.append(assignment)
    
    assignment_results = db.assignments.insert_many(assignments_data)
    assignment_ids = [str(id) for id in assignment_results.inserted_ids]
    print(f"✓ Inserted {len(assignment_ids)} assignments")
    
    # ==================== Seed Submissions ====================
    print("Seeding submissions...")
    submissions_data = []
    
    for assignment_id in assignment_ids[:10]:
        for student_id in student_ids[:20]:
            # 70% submitted, 30% pending
            if random.random() > 0.3:
                submission = {
                    "assignment_id": assignment_id,
                    "student_id": student_id,
                    "submission_date": today - timedelta(days=1),
                    "marks_obtained": random.randint(6, 10),
                    "status": "Submitted"
                }
            else:
                submission = {
                    "assignment_id": assignment_id,
                    "student_id": student_id,
                    "submission_date": None,
                    "marks_obtained": None,
                    "status": "Pending"
                }
            submissions_data.append(submission)
    
    db.submissions.insert_many(submissions_data)
    print(f"✓ Inserted {len(submissions_data)} submissions")
    
    # ==================== Seed Exams ====================
    print("Seeding exams...")
    exam_subjects = ["Mathematics", "English", "Science", "History", "Geography"]
    exams_data = []
    
    base_date = today.replace(day=1) + timedelta(days=20)
    
    for idx, class_id in enumerate(class_ids):
        for exam_idx, subject in enumerate(exam_subjects):
            exam_date = base_date + timedelta(days=exam_idx)
            
            exam = {
                "exam_name": f"{subject} Exam",
                "class_id": class_id,
                "date": exam_date,
                "time": f"{9+exam_idx}:00",
                "duration": 120,
                "total_marks": 100,
                "subject": subject
            }
            exams_data.append(exam)
    
    db.exams.insert_many(exams_data)
    print(f"✓ Inserted {len(exams_data)} exams")
    
    # Print summary
    print("\n" + "="*50)
    print("Database Seeding Complete!")
    print("="*50)
    print(f"Teachers: {len(teacher_ids)}")
    print(f"Classes: {len(class_ids)}")
    print(f"Students: {len(student_ids)}")
    print(f"Attendance Records: {len(attendance_records)}")
    print(f"Assignments: {len(assignment_ids)}")
    print(f"Submissions: {len(submissions_data)}")
    print(f"Exams: {len(exams_data)}")
    print("="*50)

if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"Error seeding database: {e}")
        sys.exit(1)
