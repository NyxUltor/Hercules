"""
Main tracker window view.
Coordinates UI components with the service layer.
"""

from datetime import datetime
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
)

from hercules.services.tracker_service import WorkoutTrackerService
from hercules.data.schemas import WorkoutSessionSchema
from hercules.ui.components import (
    ExerciseCardWidget,
    SessionHeaderWidget,
    SessionFooterWidget,
)


class TrackerWindow(QMainWindow):
    """
    Main application window for the workout tracker.
    Displays a session's exercises and coordinates edits through the service layer.
    """

    def __init__(self, service: WorkoutTrackerService, session: Optional[WorkoutSessionSchema] = None):
        super().__init__()
        self.service = service
        self.session = session or self._load_or_create_session()
        
        self.setWindowTitle("Project Hercules - Workout Tracker")
        self.resize(1400, 900)
        self.setStyleSheet(self._get_global_stylesheet())
        
        self._setup_ui()

    def _get_global_stylesheet(self) -> str:
        return """
            QMainWindow {
                background: #111111;
                color: #f2f2f2;
            }
            QLabel#Title {
                font-size: 28px;
                font-weight: 700;
                color: #f2f2f2;
            }
            QLabel#Subtitle {
                color: #aaaaaa;
            }
            QFrame#Panel {
                background: #181818;
                border: 1px solid #2f2f2f;
                border-radius: 12px;
            }
            QPushButton {
                background: #2a2a2a;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 8px 12px;
                color: #f2f2f2;
            }
            QPushButton:hover {
                background: #333;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background: #101010;
                border: 1px solid #393939;
                border-radius: 6px;
                padding: 6px;
                color: #f2f2f2;
            }
        """

    def _load_or_create_session(self) -> WorkoutSessionSchema:
        """Load today's session or create a new one if none exists."""
        today_session = self.service.get_today_session()
        if today_session:
            return today_session
        
        # Create a new session for today
        from hercules.data.schemas import WorkoutSessionCreateSchema
        schema = WorkoutSessionCreateSchema(date=datetime.now(), name="Today's Workout")
        return self.service.create_session(schema)

    def _setup_ui(self):
        """Build the main window layout."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        root_layout = QVBoxLayout(self.central_widget)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        # Title
        title = QLabel("Hercules")
        title.setObjectName("Title")
        root_layout.addWidget(title)

        # Session header
        self.header_widget = SessionHeaderWidget(
            date_str=self.session.date.strftime("%a, %b %d"),
            status=self.session.status.value,
            duration_min=self.session.duration_minutes or 0,
        )
        root_layout.addWidget(self.header_widget)

        # Content panel
        content_panel = QFrame()
        content_panel.setObjectName("Panel")
        content_layout = QVBoxLayout(content_panel)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)

        # Toolbar
        toolbar = QHBoxLayout()
        
        add_exercise_btn = QPushButton("+ Add Exercise")
        add_exercise_btn.clicked.connect(self._on_add_exercise)
        toolbar.addWidget(add_exercise_btn)

        save_btn = QPushButton("Save Session")
        save_btn.clicked.connect(self._on_save_session)
        toolbar.addWidget(save_btn)

        toolbar.addWidget(QLabel(f"Editing: {self.session.name}"))
        toolbar.addStretch(1)
        content_layout.addLayout(toolbar)

        # Scroll area for exercises
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        self.exercises_layout = QVBoxLayout(scroll_content)
        self.exercises_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.exercises_layout.setSpacing(10)

        scroll.setWidget(scroll_content)
        content_layout.addWidget(scroll, 1)

        # Footer with metrics
        stats = self.service.compute_session_stats(self.session.id)
        self.footer_widget = SessionFooterWidget(
            total_volume=stats.get("total_volume", 0),
            avg_intensity=stats.get("avg_intensity"),
        )
        content_layout.addWidget(self.footer_widget)

        root_layout.addWidget(content_panel, 1)

        # Load exercises for this session
        self._load_exercises()

    def _load_exercises(self):
        """Load and display all exercises for the current session."""
        exercises = self.service.list_exercises(self.session.id)
        
        for exercise in exercises:
            sets = self.service.list_sets(exercise.id)
            set_dicts = [
                {
                    "reps": s.reps,
                    "weight_kg": s.weight_kg,
                    "intensity_rating": s.intensity_rating,
                }
                for s in sets
            ]
            
            card = ExerciseCardWidget(
                exercise_name=exercise.name,
                sets=set_dicts,
            )
            card.name_changed.connect(lambda text, ex_id=exercise.id: self._on_exercise_name_changed(ex_id, text))
            card.set_added.connect(lambda ex_id=exercise.id: self._on_set_added(ex_id))
            card.delete_requested.connect(lambda ex_id=exercise.id: self._on_delete_exercise(ex_id))
            
            self.exercises_layout.addWidget(card)

    def _on_add_exercise(self):
        """Handle add exercise button."""
        exercise = self.service.add_exercise(self.session.id, "New Exercise")
        
        card = ExerciseCardWidget(
            exercise_name=exercise.name,
            sets=[],
        )
        card.name_changed.connect(lambda text, ex_id=exercise.id: self._on_exercise_name_changed(ex_id, text))
        card.set_added.connect(lambda ex_id=exercise.id: self._on_set_added(ex_id))
        card.delete_requested.connect(lambda ex_id=exercise.id: self._on_delete_exercise(ex_id))
        
        self.exercises_layout.addWidget(card)

    def _on_exercise_name_changed(self, exercise_id: int, name: str):
        """Handle exercise name changes."""
        self.service.update_exercise(exercise_id, name=name)

    def _on_set_added(self, exercise_id: int):
        """Handle new set addition (placeholder for now)."""
        pass

    def _on_delete_exercise(self, exercise_id: int):
        """Handle exercise deletion."""
        self.service.delete_exercise(exercise_id)
        self._refresh_ui()

    def _on_save_session(self):
        """Handle save session."""
        # TODO: Persist any pending changes
        print(f"Session saved: {self.session.name}")

    def _refresh_ui(self):
        """Refresh the entire UI (after deletions, etc.)."""
        # Clear exercises layout
        while self.exercises_layout.count():
            widget = self.exercises_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        
        # Reload
        self._load_exercises()
