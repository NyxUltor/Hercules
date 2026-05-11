"""
Repository layer for data access.
Abstracts database operations behind a clean interface.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func

from hercules.data.models import WorkoutSession, Exercise, SetLog, WorkoutStatus
from hercules.data.schemas import (
    WorkoutSessionSchema,
    ExerciseSchema,
    SetLogSchema,
    WorkoutSessionCreateSchema,
    ExerciseCreateSchema,
    SetLogCreateSchema,
)


class WorkoutSessionRepository(ABC):
    """Interface for workout session data access."""

    @abstractmethod
    def get_by_id(self, session_id: int) -> Optional[WorkoutSessionSchema]:
        """Fetch a session by ID."""
        pass

    @abstractmethod
    def get_by_date(self, date: datetime) -> Optional[WorkoutSessionSchema]:
        """Fetch a session by date."""
        pass

    @abstractmethod
    def list_all(self) -> List[WorkoutSessionSchema]:
        """Fetch all sessions."""
        pass

    @abstractmethod
    def list_by_date_range(
        self, start: datetime, end: datetime
    ) -> List[WorkoutSessionSchema]:
        """Fetch sessions within a date range."""
        pass

    @abstractmethod
    def create(self, data: WorkoutSessionCreateSchema) -> WorkoutSessionSchema:
        """Create a new session."""
        pass

    @abstractmethod
    def update(self, session_id: int, data: dict) -> WorkoutSessionSchema:
        """Update a session."""
        pass

    @abstractmethod
    def delete(self, session_id: int) -> bool:
        """Delete a session."""
        pass


class ExerciseRepository(ABC):
    """Interface for exercise data access."""

    @abstractmethod
    def get_by_id(self, exercise_id: int) -> Optional[ExerciseSchema]:
        """Fetch an exercise by ID."""
        pass

    @abstractmethod
    def list_by_session(self, session_id: int) -> List[ExerciseSchema]:
        """Fetch all exercises in a session."""
        pass

    @abstractmethod
    def create(self, session_id: int, data: ExerciseCreateSchema) -> ExerciseSchema:
        """Create a new exercise in a session."""
        pass

    @abstractmethod
    def update(self, exercise_id: int, data: dict) -> ExerciseSchema:
        """Update an exercise."""
        pass

    @abstractmethod
    def delete(self, exercise_id: int) -> bool:
        """Delete an exercise."""
        pass

    @abstractmethod
    def reorder(self, exercise_id: int, new_order: int) -> ExerciseSchema:
        """Change the display order of an exercise."""
        pass


class SetLogRepository(ABC):
    """Interface for set log data access."""

    @abstractmethod
    def get_by_id(self, set_id: int) -> Optional[SetLogSchema]:
        """Fetch a set by ID."""
        pass

    @abstractmethod
    def list_by_exercise(self, exercise_id: int) -> List[SetLogSchema]:
        """Fetch all sets in an exercise."""
        pass

    @abstractmethod
    def create(self, exercise_id: int, data: SetLogCreateSchema) -> SetLogSchema:
        """Create a new set log."""
        pass

    @abstractmethod
    def update(self, set_id: int, data: dict) -> SetLogSchema:
        """Update a set log."""
        pass

    @abstractmethod
    def delete(self, set_id: int) -> bool:
        """Delete a set log."""
        pass


class SQLAlchemyWorkoutSessionRepository(WorkoutSessionRepository):
    """SQLAlchemy implementation of WorkoutSessionRepository."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_id(self, session_id: int) -> Optional[WorkoutSessionSchema]:
        model = self.db.query(WorkoutSession).filter(
            WorkoutSession.id == session_id
        ).first()
        return WorkoutSessionSchema.from_orm(model) if model else None

    def get_by_date(self, date: datetime) -> Optional[WorkoutSessionSchema]:
        model = self.db.query(WorkoutSession).filter(
            func.date(WorkoutSession.date) == date.date()
        ).first()
        return WorkoutSessionSchema.from_orm(model) if model else None

    def list_all(self) -> List[WorkoutSessionSchema]:
        models = self.db.query(WorkoutSession).order_by(WorkoutSession.date).all()
        return [WorkoutSessionSchema.from_orm(m) for m in models]

    def list_by_date_range(
        self, start: datetime, end: datetime
    ) -> List[WorkoutSessionSchema]:
        models = self.db.query(WorkoutSession).filter(
            WorkoutSession.date >= start,
            WorkoutSession.date <= end
        ).order_by(WorkoutSession.date).all()
        return [WorkoutSessionSchema.from_orm(m) for m in models]

    def create(self, data: WorkoutSessionCreateSchema) -> WorkoutSessionSchema:
        model = WorkoutSession(
            date=data.date,
            name=data.name,
            status=data.status,
            duration_minutes=data.duration_minutes,
            notes=data.notes,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return WorkoutSessionSchema.from_orm(model)

    def update(self, session_id: int, data: dict) -> WorkoutSessionSchema:
        model = self.db.query(WorkoutSession).filter(
            WorkoutSession.id == session_id
        ).first()
        if not model:
            raise ValueError(f"Session {session_id} not found")
        for key, value in data.items():
            if hasattr(model, key):
                setattr(model, key, value)
        model.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(model)
        return WorkoutSessionSchema.from_orm(model)

    def delete(self, session_id: int) -> bool:
        model = self.db.query(WorkoutSession).filter(
            WorkoutSession.id == session_id
        ).first()
        if not model:
            return False
        self.db.delete(model)
        self.db.commit()
        return True


class SQLAlchemyExerciseRepository(ExerciseRepository):
    """SQLAlchemy implementation of ExerciseRepository."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_id(self, exercise_id: int) -> Optional[ExerciseSchema]:
        model = self.db.query(Exercise).filter(Exercise.id == exercise_id).first()
        return ExerciseSchema.from_orm(model) if model else None

    def list_by_session(self, session_id: int) -> List[ExerciseSchema]:
        models = self.db.query(Exercise).filter(
            Exercise.session_id == session_id
        ).order_by(Exercise.order).all()
        return [ExerciseSchema.from_orm(m) for m in models]

    def create(self, session_id: int, data: ExerciseCreateSchema) -> ExerciseSchema:
        model = Exercise(
            session_id=session_id,
            name=data.name,
            order=data.order,
            notes=data.notes,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return ExerciseSchema.from_orm(model)

    def update(self, exercise_id: int, data: dict) -> ExerciseSchema:
        model = self.db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not model:
            raise ValueError(f"Exercise {exercise_id} not found")
        for key, value in data.items():
            if hasattr(model, key):
                setattr(model, key, value)
        model.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(model)
        return ExerciseSchema.from_orm(model)

    def delete(self, exercise_id: int) -> bool:
        model = self.db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not model:
            return False
        self.db.delete(model)
        self.db.commit()
        return True

    def reorder(self, exercise_id: int, new_order: int) -> ExerciseSchema:
        model = self.db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not model:
            raise ValueError(f"Exercise {exercise_id} not found")
        model.order = new_order
        model.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(model)
        return ExerciseSchema.from_orm(model)


class SQLAlchemySetLogRepository(SetLogRepository):
    """SQLAlchemy implementation of SetLogRepository."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_id(self, set_id: int) -> Optional[SetLogSchema]:
        model = self.db.query(SetLog).filter(SetLog.id == set_id).first()
        return SetLogSchema.from_orm(model) if model else None

    def list_by_exercise(self, exercise_id: int) -> List[SetLogSchema]:
        models = self.db.query(SetLog).filter(
            SetLog.exercise_id == exercise_id
        ).order_by(SetLog.set_number).all()
        return [SetLogSchema.from_orm(m) for m in models]

    def create(self, exercise_id: int, data: SetLogCreateSchema) -> SetLogSchema:
        model = SetLog(
            exercise_id=exercise_id,
            set_number=data.set_number,
            reps=data.reps,
            weight_kg=data.weight_kg,
            intensity_rating=data.intensity_rating,
            notes=data.notes,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return SetLogSchema.from_orm(model)

    def update(self, set_id: int, data: dict) -> SetLogSchema:
        model = self.db.query(SetLog).filter(SetLog.id == set_id).first()
        if not model:
            raise ValueError(f"Set {set_id} not found")
        for key, value in data.items():
            if hasattr(model, key):
                setattr(model, key, value)
        model.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(model)
        return SetLogSchema.from_orm(model)

    def delete(self, set_id: int) -> bool:
        model = self.db.query(SetLog).filter(SetLog.id == set_id).first()
        if not model:
            return False
        self.db.delete(model)
        self.db.commit()
        return True
