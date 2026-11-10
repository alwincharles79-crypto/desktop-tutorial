# Student Registration System

A responsive student registration and records-management web application built with **Python, FastAPI, SQLite, HTML, CSS and JavaScript**.

## Features

- Dashboard with total students, registrations today and course count
- Register students with input validation
- View, search, edit and delete student records
- Duplicate email and phone prevention
- Export student records to CSV
- SQLite persistence (records remain after restarting the server)
- Responsive interface for desktop, tablet and mobile
- Interactive API documentation at `/docs`

## Requirements

- Python 3.10 or newer
- pip

## Run locally

```bash
# 1. Create and activate a virtual environment
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the application
uvicorn backend.app:app --reload
```

Open **http://127.0.0.1:8000** in your browser. API documentation is available at **http://127.0.0.1:8000/docs**.

## Validation rules

- Student name must contain at least two characters.
- Email address must have a valid format.
- Phone number must be a 10-digit Indian mobile number starting with 6, 7, 8 or 9.
- Course is required.
- Email addresses and phone numbers must be unique.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Service health check |
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/students` | List students; optional `?search=` filter |
| POST | `/api/students` | Register a student |
| PUT | `/api/students/{id}` | Update a student |
| DELETE | `/api/students/{id}` | Delete a student |
| GET | `/api/export` | Download student records as CSV |

## Project structure

```text
student-registration-system/
├── backend/
│   ├── __init__.py
│   ├── app.py
│   ├── database.py
│   └── validation.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── tests/
│   └── test_validation.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Privacy and deployment note

The database is created locally on first run and is excluded from Git. Do not commit real student contact information or credentials. This project is intended as a learning/demo application; add authentication, role-based access, HTTPS and appropriate privacy controls before using it with real student data or deploying it publicly.

## License

For educational use. Add a license file if you intend to distribute the project under a specific open-source license.
