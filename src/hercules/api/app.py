"""
Minimal FastAPI app exposing the tracker service for headless testing.
Use HERCULES_DB to point to a sqlite URL (defaults to sqlite:///hercules.db).
"""
from datetime import datetime
import os
from typing import List

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from hercules.data.models import Base
from hercules.data.repositories import (
    SQLAlchemyWorkoutSessionRepository,
    SQLAlchemyExerciseRepository,
    SQLAlchemySetLogRepository,
)
from hercules.services.tracker_service import WorkoutTrackerService
from hercules.data.schemas import (
    WorkoutSessionCreateSchema,
    WorkoutSessionSchema,
)


DB_URL = os.environ.get("HERCULES_DB") or "sqlite:///hercules.db"

def create_service(db_url: str = DB_URL):
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    db_session = Session(engine)
    session_repo = SQLAlchemyWorkoutSessionRepository(db_session)
    exercise_repo = SQLAlchemyExerciseRepository(db_session)
    set_repo = SQLAlchemySetLogRepository(db_session)
    service = WorkoutTrackerService(session_repo, exercise_repo, set_repo)
    return service


app = FastAPI(title="Hercules Tracker (headless)")
service = create_service()


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/sessions", response_model=List[WorkoutSessionSchema])
def list_sessions():
    return service.list_sessions()


@app.post("/sessions", response_model=WorkoutSessionSchema)
def create_session(payload: WorkoutSessionCreateSchema):
    return service.create_session(payload)


@app.get("/sessions/{session_id}", response_model=WorkoutSessionSchema)
def get_session(session_id: int):
    s = service.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return s


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("hercules.api.app:app", host="0.0.0.0", port=8000, reload=False)
