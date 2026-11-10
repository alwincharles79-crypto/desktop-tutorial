from contextlib import asynccontextmanager
from pathlib import Path
import csv
import io
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .database import create_table, get_connection
from .validation import validate_student

ROOT = Path(__file__).resolve().parent.parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_table()
    yield

app = FastAPI(
    title="Student Registration System",
    description="A student registration and records management application.",
    version="1.0.0",
    lifespan=lifespan,
)

class StudentInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    student_name: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=254)
    phone: str = Field(min_length=10, max_length=10)
    course: str = Field(min_length=1, max_length=100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return value.lower().strip()

    @field_validator("student_name", "course")
    @classmethod
    def non_blank(cls, value):
        if not value.strip():
            raise ValueError("This field cannot be blank.")
        return value.strip()

    def validate_business_rules(self):
        errors = validate_student(self.student_name, self.email, self.phone, self.course)
        if errors:
            raise HTTPException(status_code=422, detail=errors)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Student Registration System"}

@app.get("/api/stats")
def stats():
    with get_connection() as conn:
        row = conn.execute("""SELECT COUNT(*) AS total,
            COUNT(DISTINCT course) AS courses,
            SUM(CASE WHEN date(registration_date)=date('now','localtime') THEN 1 ELSE 0 END) AS today
            FROM students""").fetchone()
        recent = conn.execute("SELECT id, student_name, course, registration_date FROM students ORDER BY id DESC LIMIT 5").fetchall()
    return {"total_students": row["total"] or 0, "total_courses": row["courses"] or 0,
            "today_registrations": row["today"] or 0, "recent": [dict(x) for x in recent]}

@app.get("/api/students")
def list_students(search: str = Query(default="", max_length=120)):
    with get_connection() as conn:
        if search.strip():
            term = f"%{search.strip()}%"
            rows = conn.execute("""SELECT * FROM students WHERE student_name LIKE ? OR email LIKE ?
                OR phone LIKE ? OR course LIKE ? ORDER BY id DESC""", (term, term, term, term)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]

@app.post("/api/students", status_code=201)
def create_student(student: StudentInput):
    student.validate_business_rules()
    try:
        with get_connection() as conn:
            cur = conn.execute("INSERT INTO students (student_name,email,phone,course) VALUES (?,?,?,?)",
                (student.student_name, student.email, student.phone, student.course))
            row = conn.execute("SELECT * FROM students WHERE id=?", (cur.lastrowid,)).fetchone()
            return dict(row)
    except sqlite3.IntegrityError as exc:
        message = "Email address is already registered." if "email" in str(exc).lower() else "Phone number is already registered."
        raise HTTPException(status_code=409, detail=message)

@app.put("/api/students/{student_id}")
def update_student(student_id: int, student: StudentInput):
    student.validate_business_rules()
    try:
        with get_connection() as conn:
            cur = conn.execute("UPDATE students SET student_name=?,email=?,phone=?,course=? WHERE id=?",
                (student.student_name, student.email, student.phone, student.course, student_id))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Student record not found.")
            return dict(conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone())
    except sqlite3.IntegrityError as exc:
        message = "Email address is already registered." if "email" in str(exc).lower() else "Phone number is already registered."
        raise HTTPException(status_code=409, detail=message)

@app.delete("/api/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM students WHERE id=?", (student_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student record not found.")

@app.get("/api/export")
def export_students():
    with get_connection() as conn:
        rows = conn.execute("SELECT id,student_name,email,phone,course,registration_date FROM students ORDER BY id").fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student ID", "Student Name", "Email", "Phone", "Course", "Registration Date"])
    writer.writerows([tuple(row) for row in rows])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=students_export.csv"})

app.mount("/static", StaticFiles(directory=ROOT / "frontend"), name="static")

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(ROOT / "frontend" / "index.html")
