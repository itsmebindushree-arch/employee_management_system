"""Service-level verification using SQLite without requiring a MySQL server."""

import os
import unittest

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from fastapi import HTTPException
from pydantic import ValidationError

from app.database import Base, SessionLocal, engine
from app.schemas import EmployeeCreate, EmployeeUpdate
from app.services import (
    create_employee,
    delete_employee,
    get_all_employees,
    get_employee_by_id,
    update_employee,
)


class EmployeeServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        Base.metadata.create_all(engine)
        self.db = SessionLocal()
        self.payload = {
            "name": "Aarav Mehta",
            "email": "aarav.mehta@example.com",
            "department": "Engineering",
            "primary_skill": "Python",
            "location": "Pune",
            "work_mode": "WFH",
        }

    def tearDown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(engine)

    def test_crud_duplicate_check_and_timestamp_preservation(self) -> None:
        employee = create_employee(self.db, EmployeeCreate(**self.payload))
        self.assertEqual(employee.id, 1)
        self.assertTrue(employee.is_active)
        self.assertEqual(employee.email, "aarav.mehta@example.com")
        created_at = employee.created_at

        total, employees = get_all_employees(self.db)
        self.assertEqual(total, 1)
        self.assertEqual(len(employees), 1)
        self.assertEqual(get_employee_by_id(self.db, employee.id).id, employee.id)

        with self.assertRaises(HTTPException) as duplicate_error:
            create_employee(
                self.db,
                EmployeeCreate(**{**self.payload, "email": "AARAV.MEHTA@EXAMPLE.COM"}),
            )
        self.assertEqual(duplicate_error.exception.status_code, 409)

        updated = update_employee(
            self.db,
            employee.id,
            EmployeeUpdate(**{**self.payload, "name": "Aarav Kumar", "is_active": False}),
        )
        self.assertFalse(updated.is_active)
        self.assertEqual(updated.created_at, created_at)

        delete_employee(self.db, employee.id)
        self.assertEqual(get_all_employees(self.db), (0, []))

        with self.assertRaises(HTTPException) as missing_error:
            get_employee_by_id(self.db, employee.id)
        self.assertEqual(missing_error.exception.status_code, 404)

    def test_blank_required_text_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            EmployeeCreate(**{**self.payload, "name": "   "})

    def test_search_filters_pagination_and_total(self) -> None:
        records = [
            ("Aarav Mehta", "aarav@example.com", "Engineering", "WFH", True),
            ("Aarohi Singh", "aarohi@example.com", "Engineering", "WFH", True),
            ("Dev Patel", "dev@example.com", "Engineering", "WFO", False),
            ("Maya Rao", "maya@example.com", "Human Resources", "WFO", True),
            ("Nina Das", "nina@example.com", "Engineering", "WFH", True),
        ]
        for name, email, department, work_mode, is_active in records:
            employee = create_employee(
                self.db,
                EmployeeCreate(**{
                    **self.payload,
                    "name": name,
                    "email": email,
                    "department": department,
                    "work_mode": work_mode,
                }),
            )
            if not is_active:
                update_employee(
                    self.db,
                    employee.id,
                    EmployeeUpdate(**{
                        **self.payload,
                        "name": name,
                        "email": email,
                        "department": department,
                        "work_mode": work_mode,
                        "is_active": False,
                    }),
                )

        total, items = get_all_employees(
            self.db, department="engineering", work_mode="WFH", limit=2, offset=0
        )
        self.assertEqual(total, 3)
        self.assertEqual([employee.name for employee in items], ["Aarav Mehta", "Aarohi Singh"])

        total, items = get_all_employees(self.db, search="AAR", limit=10)
        self.assertEqual(total, 2)
        self.assertEqual([employee.name for employee in items], ["Aarav Mehta", "Aarohi Singh"])

        total, items = get_all_employees(
            self.db, department="Engineering", work_mode="WFH", limit=2, offset=2
        )
        self.assertEqual(total, 3)
        self.assertEqual([employee.name for employee in items], ["Nina Das"])

        total, items = get_all_employees(self.db, is_active=False, limit=10)
        self.assertEqual(total, 1)
        self.assertEqual(items[0].name, "Dev Patel")

        total, items = get_all_employees(self.db, search="nobody", limit=10, offset=99)
        self.assertEqual((total, items), (0, []))


if __name__ == "__main__":
    unittest.main()
