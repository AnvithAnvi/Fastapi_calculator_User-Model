# app/models.py

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # One-to-many relationship: one user → many calculations
    calculations = relationship("Calculation", back_populates="user")


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, nullable=False)
    operand_a = Column(Float, nullable=False)
    operand_b = Column(Float, nullable=False)
    result = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # ✅ Allow NULL so old tests that don't send a user_id still work
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationship back to User
    user = relationship("User", back_populates="calculations")
