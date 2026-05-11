Hercules — Workout Tracker

This repository contains a production-ready, layered Python desktop/workout tracker.

Quick start (desktop):

1. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
# (optional) editable install for local development
pip install -e .
```

3. Run the GUI (desktop with X11):

```bash
python src/hercules/main.py
```

If you're in a headless environment (codespace, CI), run the headless API to test business logic and data persistence:

```bash
# start the headless FastAPI server (uses sqlite file hercules.db by default)
python -m hercules.api.app
# or with uvicorn
uvicorn hercules.api.app:app --host 127.0.0.1 --port 8000
```

Open `http://localhost:8000/docs` to interact with the API.

Notes:
- To run the GUI locally you need a desktop environment and a system OpenGL library (e.g., libGL.so.1).
- The project uses SQLAlchemy, Pydantic and PyQt6; see `requirements.txt` for full deps.
