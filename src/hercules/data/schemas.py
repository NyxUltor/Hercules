"""
Pydantic schemas for validation and serialization.
These are the contracts between layers and the API.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class WorkoutStatusSchema(str, Enum):
    """Status of a workout session."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class SetLogSchema(BaseModel):
    """Set/rep entry within an exercise."""
    id: Optional[int] = None
    exercise_id: Optional[int] = None
    set_number: int = Field(..., ge=1)
    reps: int = Field(..., ge=0)
    weight_kg: float = Field(..., ge=0)
    intensity_rating: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExerciseSchema(BaseModel):
    """Single exercise within a session."""
    id: Optional[int] = None
    session_id: Optional[int] = None
    name: str = Field(..., min_length=1)
    order: int = Field(0, ge=0)
    notes: Optional[str] = None
    sets: List[SetLogSchema] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkoutSessionSchema(BaseModel):
    """Complete workout session."""
    id: Optional[int] = None
    date: datetime
    name: str = Field("Workout", min_length=1)
    status: WorkoutStatusSchema = WorkoutStatusSchema.SCHEDULED
    duration_minutes: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None
    exercises: List[ExerciseSchema] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkoutSessionCreateSchema(BaseModel):
    """Schema for creating a new workout session."""
    date: datetime
    name: str = Field("Workout", min_length=1)
    status: WorkoutStatusSchema = WorkoutStatusSchema.SCHEDULED
    duration_minutes: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None


class ExerciseCreateSchema(BaseModel):
    """Schema for creating a new exercise."""
    name: str = Field(..., min_length=1)
    order: int = Field(0, ge=0)
    notes: Optional[str] = None


class SetLogCreateSchema(BaseModel):
    """Schema for creating a new set log."""
    set_number: int = Field(..., ge=1)
    reps: int = Field(..., ge=0)
    weight_kg: float = Field(..., ge=0)
    intensity_rating: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
