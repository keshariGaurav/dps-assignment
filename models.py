from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")
        return schema

# ==================== Student Models ====================
class Student(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: str
    phone: str
    class_id: str
    section: str  # A, B, C etc
    roll_number: int
    enrollment_date: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class StudentResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: str
    class_id: str
    section: str
    roll_number: int
    
    class Config:
        populate_by_name = True

# ==================== Teacher Models ====================
class Teacher(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: str
    phone: str
    designation: str
    department: str
    qualification: str
    hire_date: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class TeacherResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: str
    designation: str
    department: str

    class Config:
        populate_by_name = True

# ==================== Class Models ====================
class Class(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    class_name: str
    section: str
    teacher_id: str
    grade: int
    student_count: int
    room_number: str
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

# ==================== Attendance Models ====================
class Attendance(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    student_id: str
    class_id: str
    date: datetime
    status: str  # Present, Absent, Leave
    remarks: Optional[str]
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class AttendanceResponse(BaseModel):
    student_id: str
    date: str
    status: str
    remarks: Optional[str]

# ==================== Assignment Models ====================
class Assignment(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: str
    class_id: str
    teacher_id: str
    created_date: datetime
    due_date: datetime
    total_marks: int
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class AssignmentResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    class_id: str
    created_date: str
    due_date: str
    total_marks: int
    
    class Config:
        populate_by_name = True

# ==================== Submission Models ====================
class AssignmentSubmission(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    assignment_id: str
    student_id: str
    submission_date: datetime
    marks_obtained: Optional[int]
    status: str  # Submitted, Pending
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

# ==================== Exam Models ====================
class Exam(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    exam_name: str
    class_id: str
    date: datetime
    time: str
    duration: int  # in minutes
    total_marks: int
    subject: str
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class ExamResponse(BaseModel):
    id: str = Field(alias="_id")
    exam_name: str
    class_id: str
    date: str
    subject: str
    total_marks: int
    
    class Config:
        populate_by_name = True

# ==================== Query Response Models ====================
class QueryResponse(BaseModel):
    success: bool
    query: str
    result_count: int
    data: List[dict]
    generated_query: Optional[str] = None
    response_text: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None
