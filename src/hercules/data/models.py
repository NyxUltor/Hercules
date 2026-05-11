"""
Data models for the Hercules workout tracker.
Uses SQLAlchemy ORM with declarative syntax.
"""

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Float, Integer, String, ForeignKey, Enum as SQLEnum, Column
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class WorkoutStatus(str, enum.Enum):
    """Status of a workout session."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class WorkoutSession(Base):
    """
    Represents a single workout session.
    Scheduled on a specific date with associated exercises.
    """
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    name = Column(String, default="Workout")
    status = Column(SQLEnum(WorkoutStatus), default=WorkoutStatus.SCHEDULED)
    duration_minutes = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    exercises = relationship("Exercise", back_populates="session", cascade="all, delete-orphan")

    def __init__(
        self,
        date: datetime,
        name: str = "Workout",
        status: WorkoutStatus = WorkoutStatus.SCHEDULED,
        duration_minutes: int | None = None,
        notes: str | None = None,
    ):
        self.date = date
        self.name = name
        self.status = status
        self.duration_minutes = duration_minutes
        self.notes = notes
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class Exercise(Base):
    """
    An exercise within a workout session.
    Contains multiple sets.
    """
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("workout_sessions.id"), nullable=False)
    name = Column(String, nullable=False)
    order = Column(Integer, default=0)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    session = relationship("WorkoutSession", back_populates="exercises")
    sets = relationship("SetLog", back_populates="exercise", cascade="all, delete-orphan")

    def __init__(
        self,
        session_id: int,
        name: str,
        order: int = 0,
        notes: str | None = None,
    ):
        self.session_id = session_id
        self.name = name
        self.order = order
        self.notes = notes
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class SetLog(Base):
    """
    A single set within an exercise.
    Records reps, weight, and optional intensity/notes.
    """
    __tablename__ = "set_logs"

    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    set_number = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=False)
    intensity_rating = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    exercise = relationship("Exercise", back_populates="sets")

    def __init__(
        self,
        exercise_id: int,
        set_number: int,
        reps: int,
        weight_kg: float,
        intensity_rating: int | None = None,
        notes: str | None = None,
    ):
        self.exercise_id = exercise_id
        self.set_number = set_number
        self.reps = reps
        self.weight_kg = weight_kg
        self.intensity_rating = intensity_rating
        self.notes = notes
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
