"""
Database Schemas for Hostel Management App

Each Pydantic model represents a MongoDB collection.
Collection name = lowercase of the class name.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
import datetime as dt

class Student(BaseModel):
    name: str = Field(..., description="Full name of the student")
    email: str = Field(..., description="Email address")
    roll: str = Field(..., description="Roll number / student ID")
    room: str = Field(..., description="Room number")
    course: str = Field(..., description="Course / program")
    year: int = Field(..., ge=1, le=6, description="Year of study")

class Laundryrequest(BaseModel):
    student_id: str = Field(..., description="Reference to Student document _id (string)")
    items: List[str] = Field(..., description="List of items to be laundered")
    preferred_date: dt.date = Field(..., description="Preferred date for laundry pickup")
    status: str = Field("pending", description="Status of the request: pending, in_progress, done")

class Attendancerecord(BaseModel):
    student_id: str = Field(..., description="Reference to Student document _id (string)")
    day: dt.date = Field(..., description="Attendance date")
    present: bool = Field(True, description="Whether the student is present")

class Menu(BaseModel):
    day: dt.date = Field(..., description="Menu date")
    breakfast: str = Field(..., description="Breakfast items")
    lunch: str = Field(..., description="Lunch items")
    dinner: str = Field(..., description="Dinner items")

class Issue(BaseModel):
    student_id: str = Field(..., description="Reference to Student document _id (string)")
    title: str = Field(..., description="Issue title")
    description: str = Field(..., description="Detailed description of the issue")
    status: str = Field("open", description="Status: open, in_progress, resolved")
