from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from .models import Employee
from .schemas import EmployeeCreate, EmployeeUpdate


def _validate_employee_id(employee_id: int) -> None:
    if employee_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Employee ID must be greater than 0"
        )


def _get_employee_or_404(db: Session, employee_id: int) -> Employee:
    _validate_employee_id(employee_id)
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


def _email_exists(db: Session, email: str, exclude_id: int | None = None) -> bool:
    statement = select(Employee.id).where(func.lower(Employee.email) == email.lower())
    if exclude_id is not None:
        statement = statement.where(Employee.id != exclude_id)
    return db.scalar(statement) is not None


def _duplicate_email_error() -> HTTPException:
    return HTTPException(status_code=409, detail="Email already exists")


def create_employee(db: Session, employee_data: EmployeeCreate) -> Employee:
    if _email_exists(db, employee_data.email):
        raise _duplicate_email_error()

    employee = Employee(**employee_data.model_dump(), is_active=True)
    db.add(employee)
    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise _duplicate_email_error() from None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to create employee") from None
    return employee


def get_all_employees(
    db: Session,
    search: str | None = None,
    department: str | None = None,
    work_mode: str | None = None,
    is_active: bool | None = None,
    limit: int = 10,
    offset: int = 0,
) -> tuple[int, list[Employee]]:
    """Fetch one ordered page after applying all requested SQL filters."""
    statement = select(Employee)

    if search:
        statement = statement.where(
            func.lower(Employee.name).like(f"%{search.lower()}%")
        )
    if department:
        statement = statement.where(
            func.lower(Employee.department) == department.lower()
        )
    if work_mode is not None:
        statement = statement.where(Employee.work_mode == work_mode)
    if is_active is not None:
        statement = statement.where(Employee.is_active == is_active)

    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    employees = list(
        db.scalars(statement.order_by(Employee.id).offset(offset).limit(limit))
    )
    return total, employees


def get_employee_by_id(db: Session, employee_id: int) -> Employee:
    return _get_employee_or_404(db, employee_id)


def update_employee(db: Session, employee_id: int, employee_data: EmployeeUpdate) -> Employee:
    employee = _get_employee_or_404(db, employee_id)
    if _email_exists(db, employee_data.email, exclude_id=employee_id):
        raise _duplicate_email_error()

    # created_at is deliberately not included in the update payload.
    for field, value in employee_data.model_dump().items():
        setattr(employee, field, value)

    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise _duplicate_email_error() from None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to update employee") from None
    return employee


def delete_employee(db: Session, employee_id: int) -> dict[str, str]:
    employee = _get_employee_or_404(db, employee_id)
    db.delete(employee)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to delete employee") from None

    return {"message": "Employee deleted successfully"}
