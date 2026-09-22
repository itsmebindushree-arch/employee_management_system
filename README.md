# Employee Management API

A FastAPI application that stores employee records in a persistent MySQL `employees` table. It uses SQLAlchemy ORM, Pydantic validation, and Swagger UI.

## Features

- Database-generated employee IDs and persistent records
- Create, list, retrieve, update, and delete employee APIs, plus `/health`
- Case-insensitive email uniqueness, enforced in application logic and by a database unique constraint
- Required text fields reject empty and whitespace-only values
- `is_active` defaults to `true`; `created_at` is set once on creation and never changed by updates
- One SQLAlchemy session per request, always closed; failed writes are rolled back

## Prerequisites

- Python 3.12
- MySQL Server 8.0+ (or a compatible MySQL server)

## Database setup

Log in to MySQL and create the database:

```sql
CREATE DATABASE employee_management
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

The application creates the `employees` table automatically when it starts. SQLAlchemy defines an auto-incrementing primary key and a unique `email` column. Email input is normalized to lowercase before storage, making uniqueness case-insensitive even if the server uses a case-sensitive collation.

## Configuration and installation

1. Create and activate a virtual environment.

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies.

   ```powershell
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`, then set local MySQL credentials. `.env` is ignored by Git; never commit it.

   ```powershell
   Copy-Item .env.example .env
   ```

4. Start the API.

   ```powershell
   uvicorn app.main:app --reload
   ```

Open Swagger UI at <http://127.0.0.1:8000/docs>.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Health check |
| POST | `/employees` | Create an employee (`201`) |
| GET | `/employees` | List employees |
| GET | `/employees/{employee_id}` | Get one employee |
| PUT | `/employees/{employee_id}` | Replace an employee |
| DELETE | `/employees/{employee_id}` | Delete an employee |

Example create payload (fictional data):

```json
{
  "name": "Aarav Mehta",
  "email": "aarav.mehta@example.com",
  "department": "Engineering",
  "primary_skill": "Python",
  "location": "Pune",
  "work_mode": "WFH"
}
```

For an update, send the same fields plus `"is_active": true` or `false`.

## Expected error behavior

- Invalid request fields, including blank required text, return FastAPI validation errors (`422`).
- A duplicate email (including a different letter case) returns `409` with `Email already exists`.
- A missing employee returns `404` with `Employee not found`.
- Non-positive employee IDs return `400`.

## Verification checklist

Use Swagger UI to capture the required screenshots after configuring MySQL:

1. Create an employee and capture the `201` response.
2. Exercise list, get, update, and delete operations.
3. Create the same email again with different capitalization and capture the `409` error.
4. Request a nonexistent employee ID and capture the `404` error.
5. Create an employee, stop Uvicorn, start it again, and retrieve it with `GET /employees/{id}`. The retained record demonstrates persistence.

Task 2 Swagger screenshots are available in the `screenshots/` folder. They include the current MySQL-backed API responses for employee creation, CRUD operations, validation errors, and the persistence test showing the same employee before and after restarting the FastAPI application.

## Notes

I learned how FastAPI dependencies manage a short-lived database session per request, how SQLAlchemy maps a Python model to a MySQL table, and why application-level duplicate checks must be backed by a database constraint. The main assumption is that a local MySQL server and database can be created with the supplied credentials. Authentication, Docker, relationships, and migrations are intentionally out of scope for this task.
