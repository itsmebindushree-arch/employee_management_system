from contextlib import asynccontextmanager

from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models  # Ensures Employee metadata is registered before table creation.
from .schemas import EmployeeCreate, EmployeeListResponse, EmployeeResponse, EmployeeUpdate
from .services import (
    create_employee,
    delete_employee,
    get_all_employees,
    get_employee_by_id,
    update_employee,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Employee Management API",
    description="Beginner FastAPI project for managing employee records",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Employee Management API is running"
    }


@app.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=201
)
def add_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    return create_employee(db, employee)


@app.get(
    "/employees",
    response_model=EmployeeListResponse,
    summary="Search, filter, and browse employees",
)
def list_employees(
    db: Session = Depends(get_db),
    search: Annotated[
        str | None, Query(description="Case-insensitive partial employee-name search")
    ] = None,
    department: Annotated[
        str | None, Query(description="Case-insensitive exact department filter")
    ] = None,
    work_mode: Annotated[
        Literal["WFH", "WFO"] | None, Query(description="Work location mode")
    ] = None,
    is_active: Annotated[
        bool | None, Query(description="Filter active (true) or inactive (false) employees")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum records to return")] = 10,
    offset: Annotated[int, Query(ge=0, description="Number of matching records to skip")] = 0,
):
    total, employees = get_all_employees(
        db,
        search=search,
        department=department,
        work_mode=work_mode,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    return {"total": total, "limit": limit, "offset": offset, "items": employees}


@app.get(
    "/employees/{employee_id}",
    response_model=EmployeeResponse
)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    return get_employee_by_id(db, employee_id)


@app.put(
    "/employees/{employee_id}",
    response_model=EmployeeResponse
)
def update_employee_details(
    employee_id: int,
    employee: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    return update_employee(db, employee_id, employee)


@app.delete("/employees/{employee_id}")
def remove_employee(employee_id: int, db: Session = Depends(get_db)):
    return delete_employee(db, employee_id)
