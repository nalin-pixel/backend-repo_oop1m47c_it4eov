import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import db, create_document, get_documents
from schemas import Student, Laundryrequest, Attendancerecord, Menu, Issue

app = FastAPI(title="Hostel Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hostel Management Backend Running"}


@app.get("/schema")
def get_schema():
    return {
        "student": Student.model_json_schema(),
        "laundryrequest": Laundryrequest.model_json_schema(),
        "attendancerecord": Attendancerecord.model_json_schema(),
        "menu": Menu.model_json_schema(),
        "issue": Issue.model_json_schema(),
    }


# Students
@app.post("/students")
def create_student(student: Student):
    inserted_id = create_document("student", student)
    return {"id": inserted_id}

@app.get("/students")
def list_students():
    docs = get_documents("student")
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


# Laundry Requests
@app.post("/laundry")
def create_laundry(req: Laundryrequest):
    # Soft validation: if database unavailable, still accept; if available, optionally check student exists
    if db is not None:
        try:
            # Try to find a student document with matching _id string
            # Convert ObjectId string if possible
            from bson import ObjectId  # imported here to avoid startup failure if unavailable
            student_obj = db["student"].find_one({"_id": ObjectId(req.student_id)})
            if not student_obj:
                raise HTTPException(status_code=404, detail="Student not found")
        except Exception:
            # If conversion or lookup fails, continue without hard failure
            pass
    inserted_id = create_document("laundryrequest", req)
    return {"id": inserted_id}

@app.get("/laundry")
def list_laundry(student_id: Optional[str] = None):
    filt = {}
    if student_id:
        filt = {"student_id": student_id}
    docs = get_documents("laundryrequest", filt)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


# Attendance
@app.post("/attendance")
def mark_attendance(rec: Attendancerecord):
    if db is not None:
        try:
            from bson import ObjectId
            student_obj = db["student"].find_one({"_id": ObjectId(rec.student_id)})
            if not student_obj:
                raise HTTPException(status_code=404, detail="Student not found")
        except Exception:
            pass
    inserted_id = create_document("attendancerecord", rec)
    return {"id": inserted_id}

@app.get("/attendance")
def get_attendance(student_id: Optional[str] = None):
    filt = {}
    if student_id:
        filt = {"student_id": student_id}
    docs = get_documents("attendancerecord", filt)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


# Menu
@app.post("/menu")
def create_menu(menu: Menu):
    inserted_id = create_document("menu", menu)
    return {"id": inserted_id}

@app.get("/menu")
def list_menu():
    docs = get_documents("menu")
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


# Issues
@app.post("/issues")
def create_issue(issue: Issue):
    if db is not None:
        try:
            from bson import ObjectId
            student_obj = db["student"].find_one({"_id": ObjectId(issue.student_id)})
            if not student_obj:
                raise HTTPException(status_code=404, detail="Student not found")
        except Exception:
            pass
    inserted_id = create_document("issue", issue)
    return {"id": inserted_id}

@app.get("/issues")
def list_issues(student_id: Optional[str] = None, status: Optional[str] = None):
    filt = {}
    if student_id:
        filt["student_id"] = student_id
    if status:
        filt["status"] = status
    docs = get_documents("issue", filt)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
