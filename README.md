# Employee Management API

A FastAPI application that stores employee records in a persistent MySQL `employees` table. It uses SQLAlchemy ORM, Pydantic validation, and Swagger UI.

## Features

- Database-generated employee IDs and persistent records
- Create, search, filter, paginate, retrieve, update, and delete employee APIs, plus `/health`
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

## Search, filtering, and pagination

`GET /employees` accepts optional query parameters. SQLAlchemy performs filtering,
counting, ordering, and pagination in the database.

| Parameter | Rules | Behavior |
| --- | --- | --- |
| `search` | string | Case-insensitive partial match against `name` |
| `department` | string | Case-insensitive exact department match |
| `work_mode` | `WFH` or `WFO` | Matches work mode |
| `is_active` | `true` or `false` | Matches employment status |
| `limit` | integer, 1–100; default `10` | Maximum matching records returned |
| `offset` | integer, minimum `0`; default `0` | Matching records to skip |

Employees are always in ascending employee-ID order. With no query parameters, the
endpoint returns the first 10 employees. Each successful response includes:

```json
{
  "total": 3,
  "limit": 2,
  "offset": 0,
  "items": [{ "id": 1, "name": "Aarav Mehta" }]
}
```

`total` is the number of matching records before pagination. No results returns
`200` with `"total": 0` and `"items": []`; an offset beyond the final matching
record likewise has empty `items` but retains the correct total.

Example requests:

```text
GET /employees?search=aar
GET /employees?department=Engineering&work_mode=WFH&limit=2&offset=0
GET /employees?department=Engineering&work_mode=WFH&limit=2&offset=2
GET /employees?is_active=false
```

Invalid values return FastAPI's `422` validation response, for example
`work_mode=HYBRID`, `limit=0`, or `offset=-1`.

### Sample data for Swagger

After configuring MySQL, add six fictional employees spanning Engineering, Human
Resources, and Sales with both WFH and WFO modes:

```powershell
python -m scripts.seed_sample_employees
```

The script is safe to run repeatedly: existing emails are skipped. Start the API
and open `/docs` to exercise the requests above.

## Expected error behavior

- Invalid request fields, including blank required text, return FastAPI validation errors (`422`).
- A duplicate email (including a different letter case) returns `409` with `Email already exists`.
- A missing employee returns `404` with `Employee not found`.
- Non-positive employee IDs return `400`.

## Verification checklist

Use Swagger UI to capture the required screenshots after configuring MySQL:

1. Run `python -m unittest discover -s tests -v`.
2. Seed the sample data and capture actual responses for partial-name search, combined filters, page 1/page 2, no matches, and invalid inputs.
3. Exercise create, get-by-ID, update, and delete to confirm Task 2 behavior remains intact.
4. Create the same email again with different capitalization and capture the `409` error.
5. Create an employee, stop Uvicorn, start it again, and retrieve it with `GET /employees/{employee_id}`. The retained record demonstrates persistence.

Task 2 Swagger screenshots are available in the `screenshots/` folder. They include the current MySQL-backed API responses for employee creation, CRUD operations, validation errors, and the persistence test showing the same employee before and after restarting the FastAPI application.

## Task 3 learning note

I learned how to build one composable SQLAlchemy statement for optional filters,
calculate a matching total before applying `offset` and `limit`, and let FastAPI
describe and validate query parameters in Swagger UI. The main difficulty was
ensuring that the count and page use exactly the same filters; deriving the count
from the filtered statement avoids discrepancies. Authentication, Docker,
relationships, migrations, frontend work, and new database tables remain out of
scope.

## Task 3 – Employee Search, Filtering and Pagination

The GET /employees endpoint supports:

- search – partial, case-insensitive employee-name search
- department – filter by department
- work_mode – WFH or WFO
- is_active – filter active/inactive employees
- limit – maximum records, 1–100, default 10
- offset – number of records to skip, default 0

Example requests:

GET /employees?search=Aarav

GET /employees?department=Engineering

GET /employees?work_mode=WFH

GET /employees?department=Engineering&work_mode=WFH&limit=5&offset=0

GET /employees?department=Engineering&work_mode=WFH&limit=2&offset=2


### What I Learned

I learned how to implement search, filtering and pagination using
FastAPI query parameters and SQLAlchemy database queries.

### Difficulties Faced

I had to understand how multiple filters work together and how
limit and offset are applied after filtering.