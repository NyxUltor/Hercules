"""
Reusable UI components for the workout tracker.
These are stateless display widgets that emit signals for state changes.
"""

import sys
from typing import Optional, List, Callable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QFrame,
    QGridLayout,
)


# Signal Emitter Mixins
class SetChangedSignal(QWidget):
    """Mixin for set changes."""
    set_changed = pyqtSignal(dict)  # Emits dict with reps, weight, intensity, notes


class ExerciseChangedSignal(QWidget):
    """Mixin for exercise changes."""
    exercise_changed = pyqtSignal(dict)  # Emits dict with name, notes


# ============================================================================
# Set Row Widget
# ============================================================================

class SetRowWidget(QWidget):
    """
    Display a single set row with reps, weight, intensity.
    Emits signals when values change.
    """

    set_changed = pyqtSignal(dict)
    delete_requested = pyqtSignal()

    def __init__(self, set_number: int, reps: int = 0, weight_kg: float = 0.0, intensity: Optional[int] = None, parent=None):
        super().__init__(parent)

        self.set_number = set_number
        self._setup_ui(reps, weight_kg, intensity)

    def _setup_ui(self, reps: int, weight_kg: float, intensity: Optional[int]):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(8)

        # Set number label
        set_label = QLabel(f"Set {self.set_number}")
        set_label.setMinimumWidth(60)
        layout.addWidget(set_label)

        # Reps
        self.reps_spin = QSpinBox()
        self.reps_spin.setRange(0, 999)
        self.reps_spin.setValue(reps)
        self.reps_spin.setSuffix(" reps")
        self.reps_spin.setMinimumWidth(80)
        self.reps_spin.valueChanged.connect(self._emit_change)
        layout.addWidget(self.reps_spin)

        # Weight
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0, 9999)
        self.weight_spin.setValue(weight_kg)
        self.weight_spin.setSingleStep(0.5)
        self.weight_spin.setSuffix(" kg")
        self.weight_spin.setMinimumWidth(80)
        self.weight_spin.valueChanged.connect(self._emit_change)
        layout.addWidget(self.weight_spin)

        # Intensity
        self.intensity_spin = QSpinBox()
        self.intensity_spin.setRange(0, 10)
        self.intensity_spin.setValue(intensity or 0)
        self.intensity_spin.setSuffix("/10")
        self.intensity_spin.setMinimumWidth(60)
        self.intensity_spin.valueChanged.connect(self._emit_change)
        layout.addWidget(self.intensity_spin)

        # Delete button
        delete_btn = QPushButton("✕")
        delete_btn.setMaximumWidth(30)
        delete_btn.clicked.connect(self.delete_requested.emit)
        layout.addWidget(delete_btn)

        layout.addStretch(1)

    def _emit_change(self):
        """Emit current state."""
        self.set_changed.emit({
            "reps": self.reps_spin.value(),
            "weight_kg": self.weight_spin.value(),
            "intensity_rating": self.intensity_spin.value() if self.intensity_spin.value() > 0 else None,
        })

    def get_data(self) -> dict:
        """Return current set data."""
        return {
            "set_number": self.set_number,
            "reps": self.reps_spin.value(),
            "weight_kg": self.weight_spin.value(),
            "intensity_rating": self.intensity_spin.value() if self.intensity_spin.value() > 0 else None,
        }


# ============================================================================
# Exercise Card Widget
# ============================================================================

class ExerciseCardWidget(QWidget):
    """
    Display a single exercise with its sets.
    Manages add/remove sets, edit name.
    """

    name_changed = pyqtSignal(str)
    set_added = pyqtSignal()
    delete_requested = pyqtSignal()

    def __init__(self, exercise_name: str = "", sets: Optional[List[dict]] = None, parent=None):
        super().__init__(parent)

        self.exercise_name = exercise_name
        self.set_rows: List[SetRowWidget] = []
        self.sets_layout = None
        self._setup_ui(sets or [])

    def _setup_ui(self, sets: List[dict]):
        self.setStyleSheet("""
            QWidget#ExerciseCard {
                background: #1c1c1c;
                border: 1px solid #333;
                border-radius: 10px;
            }
            QLineEdit {
                background: #111;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 6px;
                color: #f2f2f2;
            }
            QPushButton {
                background: #2b2b2b;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px 10px;
                color: #f2f2f2;
            }
            QPushButton:hover {
                background: #333;
            }
        """)

        self.setObjectName("ExerciseCard")
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(12, 12, 12, 12)
        outer_layout.setSpacing(10)

        # Header: name and delete button
        header_layout = QHBoxLayout()
        
        name_input = QLineEdit(self.exercise_name)
        name_input.setPlaceholderText("Exercise name")
        name_input.textChanged.connect(lambda text: self.name_changed.emit(text))
        header_layout.addWidget(name_input, 1)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_requested.emit)
        header_layout.addWidget(delete_btn)

        outer_layout.addLayout(header_layout)

        # Sets container
        self.sets_layout = QVBoxLayout()
        self.sets_layout.setSpacing(4)
        
        # Add existing sets
        for i, set_data in enumerate(sets, 1):
            self._add_set_row(i, set_data)

        outer_layout.addLayout(self.sets_layout)

        # Add set button
        add_set_btn = QPushButton("+ Add Set")
        add_set_btn.clicked.connect(self._on_add_set)
        outer_layout.addWidget(add_set_btn)

    def _add_set_row(self, set_number: int, data: dict):
        """Add a set row widget."""
        row = SetRowWidget(
            set_number,
            reps=data.get("reps", 0),
            weight_kg=data.get("weight_kg", 0),
            intensity=data.get("intensity_rating"),
        )
        row.set_changed.connect(self._on_set_changed)
        row.delete_requested.connect(lambda: self._remove_set_row(row))
        
        self.set_rows.append(row)
        self.sets_layout.addWidget(row)

    def _remove_set_row(self, row: SetRowWidget):
        """Remove a set row."""
        if row in self.set_rows:
            self.set_rows.remove(row)
            self.sets_layout.removeWidget(row)
            row.deleteLater()

    def _on_add_set(self):
        """Add a new set."""
        next_set_number = len(self.set_rows) + 1
        self._add_set_row(next_set_number, {})
        self.set_added.emit()

    def _on_set_changed(self, data: dict):
        """Handle set data changes (for future enhancement)."""
        pass

    def get_data(self) -> dict:
        """Return all exercise data."""
        return {
            "name": self.exercise_name,
            "sets": [row.get_data() for row in self.set_rows],
        }


# ============================================================================
# Session Header Widget
# ============================================================================

class SessionHeaderWidget(QWidget):
    """Display session date, status, and basic info."""

    def __init__(self, date_str: str = "", status: str = "", duration_min: int = 0, parent=None):
        super().__init__(parent)
        self._setup_ui(date_str, status, duration_min)

    def _setup_ui(self, date_str: str, status: str, duration_min: int):
        self.setStyleSheet("""
            QFrame#TopBar {
                background: #151515;
                border: 1px solid #2a2a2a;
                border-radius: 12px;
            }
            QLabel {
                color: #f2f2f2;
            }
            QLabel#Label {
                color: #aaaaaa;
                font-size: 12px;
            }
            QLabel#Value {
                font-size: 16px;
                font-weight: 600;
            }
        """)

        frame = QFrame()
        frame.setObjectName("TopBar")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for label_text, value_text in [
            ("Date", date_str),
            ("Status", status),
            ("Duration", f"{duration_min} min"),
        ]:
            block = self._make_info_block(label_text, value_text)
            layout.addWidget(block)

        layout.addStretch(1)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(frame)

    def _make_info_block(self, label_text: str, value_text: str) -> QWidget:
        """Create a label-value info block."""
        block = QWidget()
        layout = QVBoxLayout(block)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        label = QLabel(label_text)
        label.setObjectName("Label")
        value = QLabel(value_text)
        value.setObjectName("Value")

        layout.addWidget(label)
        layout.addWidget(value)
        return block


# ============================================================================
# Session Footer Widget
# ============================================================================

class SessionFooterWidget(QWidget):
    """Display session metrics: total volume, intensity."""

    def __init__(self, total_volume: float = 0.0, avg_intensity: Optional[float] = None, parent=None):
        super().__init__(parent)
        self._setup_ui(total_volume, avg_intensity)

    def _setup_ui(self, total_volume: float, avg_intensity: Optional[float]):
        self.setStyleSheet("""
            QLabel {
                color: #f2f2f2;
                font-size: 13px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(20)

        volume_label = QLabel(f"Total Volume: {total_volume:.1f} kg×reps")
        layout.addWidget(volume_label)

        if avg_intensity is not None:
            intensity_label = QLabel(f"Avg Intensity: {avg_intensity:.1f}/10")
            layout.addWidget(intensity_label)
        else:
            intensity_label = QLabel("Avg Intensity: N/A")
            layout.addWidget(intensity_label)

        layout.addStretch(1)

    def update_stats(self, total_volume: float, avg_intensity: Optional[float]):
        """Update displayed stats."""
        # This would be replaced with real updates in production
        pass
