"""
Hercules Workout Tracker - Entry Point
Thin launcher that initializes the app, database, service layer, and UI.
"""

import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QApplication

from hercules.data.models import Base
from hercules.data.repositories import (
    SQLAlchemyWorkoutSessionRepository,
    SQLAlchemyExerciseRepository,
    SQLAlchemySetLogRepository,
)
from hercules.services.tracker_service import WorkoutTrackerService
from hercules.ui.tracker_window import TrackerWindow


def create_app() -> tuple[QApplication, TrackerWindow]:
    """
    Initialize the application with all dependencies.
    Returns the Qt app and main window.
    """
    # Create database connection (in-memory SQLite for now, can swap for persistent DB)
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    db_session = Session(engine)

    # Initialize repositories
    session_repo = SQLAlchemyWorkoutSessionRepository(db_session)
    exercise_repo = SQLAlchemyExerciseRepository(db_session)
    set_repo = SQLAlchemySetLogRepository(db_session)

    # Initialize service layer
    service = WorkoutTrackerService(session_repo, exercise_repo, set_repo)

    # Create Qt application
    qt_app = QApplication(sys.argv)

    # Create and return main window
    window = TrackerWindow(service)
    return qt_app, window


def main():
    """Entry point."""
    qt_app, window = create_app()
    window.show()
    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()