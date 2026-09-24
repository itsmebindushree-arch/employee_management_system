"""Insert fictional data for manually exercising Task 3 in Swagger UI.

Run from the repository root after configuring .env:
    python -m scripts.seed_sample_employees
"""

from app.database import Base, SessionLocal, engine
from app.schemas import EmployeeCreate
from app.services import create_employee


SAMPLE_EMPLOYEES = [
    {"name": "Aarav Mehta", "email": "aarav.mehta@example.com", "department": "Engineering", "primary_skill": "Python", "location": "Pune", "work_mode": "WFH"},
    {"name": "Aarohi Singh", "email": "aarohi.singh@example.com", "department": "Engineering", "primary_skill": "React", "location": "Bengaluru", "work_mode": "WFH"},
    {"name": "Dev Patel", "email": "dev.patel@example.com", "department": "Engineering", "primary_skill": "Java", "location": "Mumbai", "work_mode": "WFO"},
    {"name": "Nina Das", "email": "nina.das@example.com", "department": "Engineering", "primary_skill": "SQL", "location": "Hyderabad", "work_mode": "WFH"},
    {"name": "Maya Rao", "email": "maya.rao@example.com", "department": "Human Resources", "primary_skill": "Recruiting", "location": "Pune", "work_mode": "WFO"},
    {"name": "Rohan Shah", "email": "rohan.shah@example.com", "department": "Sales", "primary_skill": "Negotiation", "location": "Delhi", "work_mode": "WFO"},
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        inserted = 0
        for payload in SAMPLE_EMPLOYEES:
            try:
                create_employee(db, EmployeeCreate(**payload))
                inserted += 1
            except Exception as exc:
                if getattr(exc, "status_code", None) != 409:
                    raise
        print(f"Inserted {inserted} sample employee(s); existing emails were skipped.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
