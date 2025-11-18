from typing import Dict

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from app import models
from app.database import engine, SessionLocal
from app.operations import add as op_add, subtract as op_subtract, multiply as op_multiply, divide as op_divide
from app.schemas import UserCreate, UserRead
from app.security import hash_password

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Calculator API")


# --- Database Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- User Endpoints ---

@app.post("/users/", response_model=UserRead, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Hash the password
    hashed_pw = hash_password(user_in.password)

    user = models.User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed_pw,
    )
    db.add(user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        # Most likely uniqueness violation on username or email
        raise HTTPException(status_code=400, detail="Username or email already exists")

    db.refresh(user)
    return user


# --- Calculator Endpoints ---

@app.post("/add")
def add_numbers(payload: Dict[str, float], db: Session = Depends(get_db)):
    x = payload["x"]
    y = payload["y"]
    result = op_add(x, y)

    calc = models.Calculation(operation="add", operand_a=x, operand_b=y, result=result, user_id=1)
    db.add(calc)
    db.commit()
    db.refresh(calc)

    return {"result": result, "calculation_id": calc.id}


@app.post("/subtract")
def subtract_numbers(payload: Dict[str, float], db: Session = Depends(get_db)):
    x = payload["x"]
    y = payload["y"]
    result = op_subtract(x, y)

    calc = models.Calculation(operation="subtract", operand_a=x, operand_b=y, result=result, user_id=1)
    db.add(calc)
    db.commit()
    db.refresh(calc)

    return {"result": result, "calculation_id": calc.id}


@app.post("/multiply")
def multiply_numbers(payload: Dict[str, float], db: Session = Depends(get_db)):
    x = payload["x"]
    y = payload["y"]
    result = op_multiply(x, y)

    calc = models.Calculation(operation="multiply", operand_a=x, operand_b=y, result=result, user_id=1)
    db.add(calc)
    db.commit()
    db.refresh(calc)

    return {"result": result, "calculation_id": calc.id}


@app.post("/divide")
def divide_numbers(payload: Dict[str, float], db: Session = Depends(get_db)):
    x = payload["x"]
    y = payload["y"]

    try:
        result = op_divide(x, y)
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Cannot divide by zero")

    calc = models.Calculation(operation="divide", operand_a=x, operand_b=y, result=result, user_id=1)
    db.add(calc)
    db.commit()
    db.refresh(calc)

    return {"result": result, "calculation_id": calc.id}
