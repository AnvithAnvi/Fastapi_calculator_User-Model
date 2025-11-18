from typing import Dict

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Calculation, User
from app.operations import add, subtract, multiply, divide
from app.schemas import UserCreate, UserRead
from app.security import hash_password

# Make sure tables are created
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Calculator with Users")


# ---------- Helper: default user for calculations ----------

def get_or_create_default_user(db: Session) -> User:
    """
    Ensure there is at least one user in the DB that we can attach
    calculations to when the tests call /add,/subtract,/multiply,/divide
    without specifying a user.
    """
    user = db.query(User).filter(User.username == "default_user").first()
    if user:
        return user

    hashed = hash_password("defaultpassword")
    user = User(
        username="default_user",
        email="default@example.com",
        password_hash=hashed,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------- User endpoints ----------

@app.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with a unique username and email.
    - On success: 201 + UserRead (id, username, email, created_at)
    - On duplicate username/email: 400 + detail containing 'exists'
    """
    # Check for existing username OR email
    existing_user = (
        db.query(User)
        .filter((User.email == user.email) | (User.username == user.username))
        .first()
    )
    if existing_user:
        # 🔴 What the tests expect: status 400 and the word 'exists' in detail
        raise HTTPException(
            status_code=400,
            detail="User with this username or email already exists",
        )

    hashed_pw = hash_password(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pw,
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        # Safety net in case database uniqueness fires first
        raise HTTPException(
            status_code=400,
            detail="User with this username or email already exists",
        )

    return db_user


# ---------- Calculator request schema ----------

from pydantic import BaseModel


class CalcRequest(BaseModel):
    x: float
    y: float


# ---------- Calculator endpoints ----------

@app.post("/add")
def add_numbers(payload: CalcRequest, db: Session = Depends(get_db)) -> Dict[str, float]:
    x = payload.x
    y = payload.y
    result = add(x, y)

    user = get_or_create_default_user(db)
    calc = Calculation(
        operation="add",
        operand_a=x,
        operand_b=y,
        result=result,
        user_id=user.id,
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)

    return {"result": result, "calculation_id": calc.id}


@app.post("/subtract")
def subtract_numbers(
    payload: CalcRequest, db: Session = Depends(get_db)
) -> Dict[str, float]:
    x = payload.x
    y = payload.y
    result = subtract(x, y)

    user = get_or_create_default_user(db)
    calc = Calculation(
        operation="subtract",
        operand_a=x,
        operand_b=y,
        result=result,
        user_id=user.id,
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)

    return {"result": result, "calculation_id": calc.id}


@app.post("/multiply")
def multiply_numbers(
    payload: CalcRequest, db: Session = Depends(get_db)
) -> Dict[str, float]:
    x = payload.x
    y = payload.y
    result = multiply(x, y)

    user = get_or_create_default_user(db)
    calc = Calculation(
        operation="multiply",
        operand_a=x,
        operand_b=y,
        result=result,
        user_id=user.id,
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)

    return {"result": result, "calculation_id": calc.id}


@app.post("/divide")
def divide_numbers(
    payload: CalcRequest, db: Session = Depends(get_db)
) -> Dict[str, float]:
    x = payload.x
    y = payload.y
    try:
        result = divide(x, y)
    except ZeroDivisionError:
        # Integration test expects an HTTP error, not a raw exception
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot divide by zero",
        )

    user = get_or_create_default_user(db)
    calc = Calculation(
        operation="divide",
        operand_a=x,
        operand_b=y,
        result=result,
        user_id=user.id,
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)

    return {"result": result, "calculation_id": calc.id}
