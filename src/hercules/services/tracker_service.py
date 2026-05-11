"""
Service layer for workout tracker logic.
Coordinates between repositories and UI, contains business rules.
"""

from datetime import datetime, date
from typing import Optional, List
from hercules.data.repositories import (
    WorkoutSessionRepository,
    ExerciseRepository,
    SetLogRepository,
)
from hercules.data.schemas import (
    WorkoutSessionSchema,
    ExerciseSchema,
    SetLogSchema,
    WorkoutSessionCreateSchema,
    ExerciseCreateSchema,
    SetLogCreateSchema,
)


class WorkoutTrackerService:
    """
    Main service for workout tracker operations.
    Encapsulates all business logic and coordinates repository access.
    """

    def __init__(
        self,
        session_repo: WorkoutSessionRepository,
        exercise_repo: ExerciseRepository,
        set_repo: SetLogRepository,
    ):
        self.session_repo = session_repo
        self.exercise_repo = exercise_repo
        self.set_repo = set_repo

    # ============================================================================
    # Session Management
    # ============================================================================

    def get_today_session(self) -> Optional[WorkoutSessionSchema]:
        """Get the scheduled session for today, if one exists."""
        return self.session_repo.get_by_date(datetime.now())

    def get_session(self, session_id: int) -> Optional[WorkoutSessionSchema]:
        """Get a session by ID."""
        return self.session_repo.get_by_id(session_id)

    def list_sessions(self) -> List[WorkoutSessionSchema]:
        """List all workout sessions."""
        return self.session_repo.list_all()

    def list_sessions_by_date_range(
        self, start: datetime, end: datetime
    ) -> List[WorkoutSessionSchema]:
        """List sessions within a date range."""
        return self.session_repo.list_by_date_range(start, end)

    def create_session(self, data: WorkoutSessionCreateSchema) -> WorkoutSessionSchema:
        """Create a new workout session."""
        return self.session_repo.create(data)

    def update_session(self, session_id: int, **kwargs) -> WorkoutSessionSchema:
        """Update a session's properties."""
        return self.session_repo.update(session_id, kwargs)

    def delete_session(self, session_id: int) -> bool:
        """Delete a session (and cascade to its exercises/sets)."""
        return self.session_repo.delete(session_id)

    # ============================================================================
    # Exercise Management
    # ============================================================================

    def get_exercise(self, exercise_id: int) -> Optional[ExerciseSchema]:
        """Get an exercise by ID."""
        return self.exercise_repo.get_by_id(exercise_id)

    def list_exercises(self, session_id: int) -> List[ExerciseSchema]:
        """List all exercises in a session, ordered."""
        return self.exercise_repo.list_by_session(session_id)

    def add_exercise(self, session_id: int, name: str, order: int = 0, notes: Optional[str] = None) -> ExerciseSchema:
        """Add a new exercise to a session."""
        schema = ExerciseCreateSchema(name=name, order=order, notes=notes)
        return self.exercise_repo.create(session_id, schema)

    def update_exercise(self, exercise_id: int, **kwargs) -> ExerciseSchema:
        """Update an exercise's properties."""
        return self.exercise_repo.update(exercise_id, kwargs)

    def delete_exercise(self, exercise_id: int) -> bool:
        """Delete an exercise (and cascade to its sets)."""
        return self.exercise_repo.delete(exercise_id)

    def reorder_exercise(self, exercise_id: int, new_order: int) -> ExerciseSchema:
        """Change the display order of an exercise."""
        return self.exercise_repo.reorder(exercise_id, new_order)

    # ============================================================================
    # Set Management
    # ============================================================================

    def get_set(self, set_id: int) -> Optional[SetLogSchema]:
        """Get a set by ID."""
        return self.set_repo.get_by_id(set_id)

    def list_sets(self, exercise_id: int) -> List[SetLogSchema]:
        """List all sets in an exercise, ordered."""
        return self.set_repo.list_by_exercise(exercise_id)

    def add_set(
        self,
        exercise_id: int,
        set_number: int,
        reps: int,
        weight_kg: float,
        intensity_rating: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> SetLogSchema:
        """Add a new set to an exercise."""
        schema = SetLogCreateSchema(
            set_number=set_number,
            reps=reps,
            weight_kg=weight_kg,
            intensity_rating=intensity_rating,
            notes=notes,
        )
        return self.set_repo.create(exercise_id, schema)

    def update_set(self, set_id: int, **kwargs) -> SetLogSchema:
        """Update a set's properties."""
        return self.set_repo.update(set_id, kwargs)

    def delete_set(self, set_id: int) -> bool:
        """Delete a set."""
        return self.set_repo.delete(set_id)

    # ============================================================================
    # Metrics & Analytics
    # ============================================================================

    def calculate_exercise_volume(self, exercise_id: int) -> float:
        """
        Calculate total volume for an exercise.
        Volume = sum(weight * reps * sets)
        """
        sets = self.list_sets(exercise_id)
        volume = sum(s.weight_kg * s.reps for s in sets)
        return volume

    def calculate_session_volume(self, session_id: int) -> float:
        """Calculate total volume for an entire session."""
        exercises = self.list_exercises(session_id)
        total = sum(self.calculate_exercise_volume(ex.id) for ex in exercises)
        return total

    def calculate_session_duration(self, session_id: int) -> Optional[int]:
        """Get session duration in minutes."""
        session = self.get_session(session_id)
        return session.duration_minutes if session else None

    def compute_session_stats(self, session_id: int) -> dict:
        """Compute comprehensive stats for a session."""
        session = self.get_session(session_id)
        if not session:
            return {}

        exercises = self.list_exercises(session_id)
        total_volume = self.calculate_session_volume(session_id)
        
        # Average intensity across sets with ratings
        intensities = []
        for ex in exercises:
            sets = self.list_sets(ex.id)
            for s in sets:
                if s.intensity_rating:
                    intensities.append(s.intensity_rating)
        
        avg_intensity = (sum(intensities) / len(intensities)) if intensities else None

        return {
            "session_id": session_id,
            "date": session.date,
            "name": session.name,
            "duration_minutes": session.duration_minutes,
            "total_volume": total_volume,
            "exercise_count": len(exercises),
            "set_count": sum(len(self.list_sets(ex.id)) for ex in exercises),
            "avg_intensity": avg_intensity,
        }
