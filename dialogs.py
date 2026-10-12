"""Dialog windows used by the application."""

from datetime import datetime

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
)
try:
    from .translations import T
except ImportError:
    from translations import T


class StudentDialog(QDialog):
    def __init__(self, parent, lang, name=""):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(T[lang]["students"])
        layout = QFormLayout(self)
        self.name = QLineEdit(name)
        layout.addRow(T[lang]["name"], self.name)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText(T[lang]["save"])
        buttons.button(QDialogButtonBox.Cancel).setText(T[lang]["cancel"])
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)


class WeeklyDialog(QDialog):
    def __init__(self, parent, lang, students, weekday, hour):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(T[lang]["weekly"])
        form = QFormLayout(self)
        self.student = QComboBox()
        for sid, name, _ in students:
            self.student.addItem(name, sid)
        self.hour = QComboBox()
        for h in range(8, 22):
            self.hour.addItem(f"{h:02d}:00")
        initial = f"{hour:02d}:00"
        idx = self.hour.findText(initial)
        if idx >= 0:
            self.hour.setCurrentIndex(idx)
        form.addRow(T[lang]["student"], self.student)
        form.addRow(T[lang]["time"], self.hour)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)
        self.weekday = weekday


class RevenueDialog(QDialog):
    def __init__(self, parent, lang, row=None):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(T[lang]["revenue"])
        form = QFormLayout(self)
        self.month = QLineEdit(row[1] if row else datetime.now().strftime("%Y-%m"))
        self.hours = QSpinBox()
        self.hours.setRange(0, 1000000)
        self.hours.setSingleStep(1)
        self.hours.setValue(int(row[2] if row else 0))
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0, 999999999)
        self.amount.setDecimals(2)
        self.amount.setValue(row[3] if row else 0)
        self.notes = QLineEdit(row[4] if row else "")
        form.addRow(T[lang]["month"], self.month)
        form.addRow(T[lang]["revenue_hours"], self.hours)
        form.addRow(T[lang]["revenue_amount"], self.amount)
        form.addRow(T[lang]["notes"], self.notes)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

