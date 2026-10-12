"""Main application window and page logic."""

import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QStackedWidget,
    QFrame,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QGridLayout,
    QScrollArea,
    QComboBox,
    QAbstractSpinBox,
)

try:
    from .translations import T
    from .dialogs import StudentDialog, WeeklyDialog, RevenueDialog
except ImportError:
    from translations import T
    from dialogs import StudentDialog, WeeklyDialog, RevenueDialog


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.lang = "pl"
        self.resize(1250, 800)

        self.stack = QStackedWidget()
        root = QWidget()
        outer = QHBoxLayout(root)
        self.setCentralWidget(root)

        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(260)
        sl = QVBoxLayout(side)

        self.title = QLabel("🎓")
        self.title.setObjectName("titleIcon")
        self.title.setAlignment(Qt.AlignCenter)
        sl.addWidget(self.title)

        self.app_name = QLabel(T[self.lang]["title"])
        self.app_name.setObjectName("appName")
        self.app_name.setAlignment(Qt.AlignCenter)
        self.app_name.setWordWrap(True)
        self.app_name.setMinimumHeight(58)
        sl.addWidget(self.app_name)

        outer.addWidget(side)
        outer.addWidget(self.stack)

        # Build pages BEFORE the first refresh.
        self.pages = [
            ("dashboard", self.dashboard()),
            ("students", self.students_page()),
            ("weekly", self.weekly_page()),
            ("revenue", self.revenue_page()),
        ]

        self.nav = []
        for key, page in self.pages:
            b = QPushButton(T[self.lang][key])
            b.setObjectName("nav")
            b.clicked.connect(lambda _, k=key: self.go(k))
            self.nav.append((key, b))
            sl.addWidget(b)

        sl.addStretch()
        self.lang_label = QLabel(T[self.lang]["language"])
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Polski"])
        self.lang_combo.setCurrentIndex(1)
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        sl.addWidget(self.lang_label)
        sl.addWidget(self.lang_combo)

        self.refresh_all()
        self.style()
        self.go("dashboard")

    def page(self, title):
        w = QWidget()
        lay = QVBoxLayout(w)
        label = QLabel(title)
        label.setObjectName("pageTitle")
        lay.addWidget(label)
        self.stack.addWidget(w)
        return w, lay, label

    def dashboard(self):
        self.dashboard_page, lay, self.dashboard_title = self.page(T[self.lang]["dashboard"])
        self.stats_label = QLabel()
        self.stats_label.setObjectName("stats")
        lay.addWidget(self.stats_label)

        form = QFormLayout()
        self.price_box = QSpinBox()
        self.price_box.setRange(0, 100000)
        self.price_box.setSingleStep(1)
        self.price_box.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.price_box.setMinimumWidth(120)
        self.price_save = QPushButton(T[self.lang]["save"])
        self.price_save.clicked.connect(self.save_price)

        self.add_paid_hours = QPushButton(T[self.lang]["add_paid_hours"])
        self.add_paid_hours.clicked.connect(self.add_paid_hours_manually)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(self.price_box, 0)
        row.addWidget(self.price_save, 0)
        row.addStretch()
        self.price_label = QLabel(T[self.lang]["price"])
        form.addRow(self.price_label, row)
        lay.addWidget(self.add_paid_hours)
        lay.addLayout(form)
        lay.addStretch()
        return self.dashboard_page

    def students_page(self):
        self.students_page_widget, lay, self.students_title = self.page(T[self.lang]["students"])
        top = QHBoxLayout()
        self.student_add = QPushButton(T[self.lang]["add"])
        self.student_edit = QPushButton(T[self.lang]["edit"])
        self.student_delete = QPushButton(T[self.lang]["delete"])
        self.student_unpaid = QPushButton(T[self.lang]["set_unpaid"])
        self.student_paid = QPushButton(T[self.lang]["paid"])
        self.student_add.clicked.connect(self.add_student)
        self.student_edit.clicked.connect(self.edit_student)
        self.student_delete.clicked.connect(self.delete_student)
        self.student_unpaid.clicked.connect(self.set_unpaid_hours)
        self.student_paid.clicked.connect(self.mark_student_paid)
        for b in (self.student_add, self.student_edit, self.student_delete,
                  self.student_unpaid, self.student_paid):
            top.addWidget(b)
        top.addStretch()
        lay.addLayout(top)

        self.student_table = QTableWidget(0, 4)
        self.student_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.student_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lay.addWidget(self.student_table)
        return self.students_page_widget

    def weekly_page(self):
        self.weekly_page_widget, lay, self.weekly_title = self.page(T[self.lang]["weekly"])
        self.weekly_hint = QLabel(T[self.lang]["weekly_hint"])
        lay.addWidget(self.weekly_hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.grid = QGridLayout(container)
        self.grid.setSpacing(3)
        self.grid.addWidget(QLabel(""), 0, 0)
        self.day_names = [
            "monday", "tuesday", "wednesday", "thursday",
            "friday", "saturday", "sunday"
        ]
        self.day_labels = []
        for d, key in enumerate(self.day_names):
            lab = QLabel(T[self.lang][key])
            lab.setAlignment(Qt.AlignCenter)
            self.day_labels.append((key, lab))
            self.grid.addWidget(lab, 0, d + 1)

        for slot in range(14):
            h = 8 + slot
            lab = QLabel(f"{h:02d}:00")
            lab.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(lab, slot + 1, 0)

        scroll.setWidget(container)
        lay.addWidget(scroll)
        return self.weekly_page_widget

    def revenue_page(self):
        self.revenue_page_widget, lay, self.revenue_title = self.page(T[self.lang]["revenue"])
        top = QHBoxLayout()
        self.rev_add = QPushButton(T[self.lang]["add"])
        self.rev_edit = QPushButton(T[self.lang]["edit"])
        self.rev_delete = QPushButton(T[self.lang]["delete"])
        self.rev_add.clicked.connect(self.add_revenue)
        self.rev_edit.clicked.connect(self.edit_revenue)
        self.rev_delete.clicked.connect(self.delete_revenue)
        for b in (self.rev_add, self.rev_edit, self.rev_delete):
            top.addWidget(b)
        top.addStretch()
        lay.addLayout(top)

        self.rev_table = QTableWidget(0, 4)
        self.rev_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.rev_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.rev_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lay.addWidget(self.rev_table)
        return self.revenue_page_widget

    def refresh_all(self):
        self.price_box.setValue(self.db.price())
        self.refresh_students()
        self.refresh_weekly()
        self.refresh_revenue()
        students = self.db.students()
        price = self.db.price()
        unpaid = sum(float(r[2]) for r in students)
        amount_due = unpaid * price
        revenue = sum(float(r[3]) for r in self.db.revenue())
        self.stats_label.setText(
            f"{T[self.lang]['summary']}\n\n"
            f"{T[self.lang]['students_count']}: {len(students)}\n"
            f"{T[self.lang]['unpaid_total']}: {unpaid:.0f}\n"
            f"{T[self.lang]['amount_due']}: {amount_due:.2f}\n"
            f"{T[self.lang]['monthly_total']}: {revenue:.2f}"
        )

    def refresh_students(self):
        rows = self.db.students()
        self.student_table.setRowCount(len(rows))
        price = self.db.price()
        for i, (sid, name, unpaid) in enumerate(rows):
            self.student_table.setItem(i, 0, QTableWidgetItem(name))
            self.student_table.setItem(i, 1, QTableWidgetItem(f"{unpaid:.2f}"))
            self.student_table.setItem(i, 2, QTableWidgetItem(f"{unpaid * price:.2f}"))
            self.student_table.setItem(i, 3, QTableWidgetItem(str(sid)))
        self.student_table.setHorizontalHeaderLabels([
            T[self.lang]["name"], T[self.lang]["unpaid"],
            T[self.lang]["amount_due"], "ID"
        ])
        self.student_table.setColumnHidden(3, True)

    def refresh_weekly(self):
        for widget in self.weekly_page_widget.findChildren(QPushButton, "lesson"):
            widget.deleteLater()
        for widget in self.weekly_page_widget.findChildren(QPushButton, "empty"):
            widget.deleteLater()

        for row in self.db.weekly():
            wid, sid, name, weekday, start, duration = row
            try:
                h, m = map(int, start.split(":"))
            except Exception:
                continue
            if m != 0:
                continue
            slot = h - 8
            if slot < 0 or slot >= 14:
                continue
            b = QPushButton(f"{name}")
            b.setObjectName("lesson")
            b.setToolTip(f"{name} | {start}")
            b.clicked.connect(lambda _, x=wid: self.delete_weekly(x))
            self.grid.addWidget(b, slot + 1, weekday + 1)
        self.rebuild_weekly_clicks()

    def refresh_revenue(self):
        rows = self.db.revenue()
        self.rev_table.setRowCount(len(rows))
        for i, (rid, month, hours, amount, notes) in enumerate(rows):
            self.rev_table.setItem(i, 0, QTableWidgetItem(month))
            self.rev_table.setItem(i, 1, QTableWidgetItem(str(hours)))
            self.rev_table.setItem(i, 2, QTableWidgetItem(f"{amount:.2f}"))
            self.rev_table.setItem(i, 3, QTableWidgetItem(notes))
        self.rev_table.setHorizontalHeaderLabels([
            T[self.lang]["month"], T[self.lang]["revenue_hours"],
            T[self.lang]["revenue_amount"], T[self.lang]["notes"]
        ])

    def selected_student_id(self):
        row = self.student_table.currentRow()
        if row < 0:
            return None
        item = self.student_table.item(row, 3)
        if item is None:
            return None
        try:
            return int(item.text())
        except (TypeError, ValueError):
            return None

    def add_student(self):
        d = StudentDialog(self, self.lang)
        if d.exec() and d.name.text().strip():
            try:
                self.db.add_student(d.name.text().strip())
                self.refresh_all()
            except sqlite3.IntegrityError as e:
                QMessageBox.critical(
                    self, T[self.lang]["error"],
                    f"{T[self.lang]['error']}: {e}"
                )

    def edit_student(self):
        sid = self.selected_student_id()
        if sid is None:
            return
        row = self.student_table.currentRow()
        name = self.student_table.item(row, 0).text()
        d = StudentDialog(self, self.lang, name)
        if d.exec() and d.name.text().strip():
            self.db.update_student(sid, d.name.text().strip())
            self.refresh_all()

    def delete_student(self):
        sid = self.selected_student_id()
        if sid is None:
            return
        if QMessageBox.question(self, T[self.lang]["delete"],
                                T[self.lang]["confirm_delete"]) == QMessageBox.Yes:
            self.db.delete_student(sid)
            self.refresh_all()

    def add_paid_hours_manually(self):
        from PySide6.QtWidgets import QInputDialog
        hours, ok = QInputDialog.getInt(
            self,
            T[self.lang]["add_paid_hours"],
            T[self.lang]["hours"],
            1,
            1,
            1000000,
            1
        )
        if ok:
            amount = self.db.add_paid_hours(hours)
            self.refresh_all()
            QMessageBox.information(
                self, T[self.lang]["saved"],
                f"{hours} h = {amount:.2f}"
            )

    def set_unpaid_hours(self):
        # Always obtain the selected row from the table at the moment the
        # button is pressed. This avoids stale selections after refreshes.
        row = self.student_table.currentRow()
        if row < 0:
            QMessageBox.information(
                self, T[self.lang]["set_unpaid"], T[self.lang]["select_student"]
            )
            return

        id_item = self.student_table.item(row, 3)
        if id_item is None:
            return

        try:
            sid = int(id_item.text())
        except (TypeError, ValueError):
            return

        result = self.db.conn.execute(
            "SELECT name, unpaid_hours FROM students WHERE id=?", (sid,)
        ).fetchone()
        if result is None:
            return

        name, current = result

        dialog = QDialog(self)
        dialog.setWindowTitle(T[self.lang]["set_unpaid"])
        dialog.setMinimumWidth(360)
        form = QFormLayout(dialog)

        name_label = QLabel(str(name))
        hours_box = QSpinBox()
        hours_box.setRange(0, 1000000)
        hours_box.setSingleStep(1)
        hours_box.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        hours_box.setMinimumWidth(120)
        hours_box.setValue(int(round(float(current or 0))))

        form.addRow(T[self.lang]["name"], name_label)
        form.addRow(T[self.lang]["unpaid"], hours_box)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.button(QDialogButtonBox.Save).setText(T[self.lang]["save"])
        buttons.button(QDialogButtonBox.Cancel).setText(T[self.lang]["cancel"])
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        if dialog.exec() == QDialog.Accepted:
            self.db.set_unpaid_hours(sid, hours_box.value())
            self.db.conn.commit()
            self.refresh_all()

            # Reselect the same student so the changed value is immediately visible.
            for r in range(self.student_table.rowCount()):
                item = self.student_table.item(r, 3)
                if item and item.text() == str(sid):
                    self.student_table.selectRow(r)
                    break

    def mark_student_paid(self):
        sid = self.selected_student_id()
        if sid is None:
            return

        row = self.student_table.currentRow()
        name = self.student_table.item(row, 0).text()
        unpaid = float(self.student_table.item(row, 1).text())
        amount = unpaid * self.db.price()

        if unpaid <= 0:
            QMessageBox.information(
                self, T[self.lang]["paid"], T[self.lang]["paid"]
            )
            return

        question = (
            f"{name}\n\n"
            f"{T[self.lang]['unpaid']}: {unpaid:.2f}\n"
            f"{T[self.lang]['amount_due']}: {amount:.2f}\n\n"
            f"{T[self.lang]['paid']}?"
        )

        if QMessageBox.question(
            self, T[self.lang]["paid"], question
        ) == QMessageBox.Yes:
            self.db.mark_student_paid(sid)
            self.refresh_all()

    def save_price(self):
        self.db.set_price(self.price_box.value())
        self.refresh_all()
        QMessageBox.information(self, T[self.lang]["saved"], T[self.lang]["saved"])

    def grid_click(self, day, slot):
        students = self.db.students()
        if not students:
            QMessageBox.information(self, T[self.lang]["weekly"],
                                    T[self.lang]["no_students"])
            return
        hour = 8 + slot
        d = WeeklyDialog(self, self.lang, students, day, hour)
        if d.exec():
            start = d.hour.currentText()
            self.db.add_weekly(
                d.student.currentData(), day, start, 1.0
            )
            self.refresh_weekly()

    def rebuild_weekly_clicks(self):
        # Recreate empty-cell buttons.
        for b in self.weekly_page_widget.findChildren(QPushButton, "empty"):
            b.deleteLater()
        occupied = {(r[3], r[4]) for r in self.db.weekly()}
        for slot in range(14):
            h = 8 + slot
            start = f"{h:02d}:00"
            for day in range(7):
                if (day, start) in occupied:
                    continue
                b = QPushButton("+")
                b.setObjectName("empty")
                b.setFixedHeight(30)
                b.clicked.connect(lambda _, dd=day, ss=slot: self.grid_click(dd, ss))
                self.grid.addWidget(b, slot + 1, day + 1)

    def delete_weekly(self, wid):
        if QMessageBox.question(self, T[self.lang]["delete"],
                                T[self.lang]["confirm_delete"]) == QMessageBox.Yes:
            self.db.delete_weekly(wid)
            self.refresh_weekly()

    def selected_revenue_id(self):
        row = self.rev_table.currentRow()
        if row < 0:
            return None
        rows = self.db.revenue()
        return rows[row] if row < len(rows) else None

    def add_revenue(self):
        d = RevenueDialog(self, self.lang)
        if d.exec():
            try:
                self.db.add_revenue(d.month.text().strip(), d.hours.value(), d.amount.value(), d.notes.text())
                self.refresh_all()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, T[self.lang]["revenue"], "This month already exists.")

    def edit_revenue(self):
        row = self.selected_revenue_id()
        if not row:
            return
        d = RevenueDialog(self, self.lang, row)
        if d.exec():
            try:
                self.db.update_revenue(row[0], d.month.text().strip(),
                                       d.hours.value(), d.amount.value(), d.notes.text())
                self.refresh_all()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, T[self.lang]["revenue"], "This month already exists.")

    def delete_revenue(self):
        row = self.selected_revenue_id()
        if not row:
            return
        if QMessageBox.question(self, T[self.lang]["delete"],
                                T[self.lang]["confirm_delete"]) == QMessageBox.Yes:
            self.db.delete_revenue(row[0])
            self.refresh_all()

    def go(self, key):
        for k, b in self.nav:
            if k == key:
                b.setChecked(True)
                for pkey, page in self.pages:
                    if pkey == key:
                        self.stack.setCurrentWidget(page)
                        return

    def change_language(self, index):
        self.lang = "pl" if index == 1 else "en"
        t = T[self.lang]

        self.app_name.setText(t["title"])
        self.dashboard_title.setText(t["dashboard"])
        self.students_title.setText(t["students"])
        self.weekly_title.setText(t["weekly"])
        self.revenue_title.setText(t["revenue"])
        self.weekly_hint.setText(t["weekly_hint"])
        self.price_label.setText(t["price"])

        for key, lab in self.day_labels:
            lab.setText(t[key])

        for key, b in self.nav:
            b.setText(t[key])

        self.lang_label.setText(t["language"])
        self.price_save.setText(t["save"])
        self.add_paid_hours.setText(t["add_paid_hours"])
        self.student_add.setText(t["add"])
        self.student_edit.setText(t["edit"])
        self.student_delete.setText(t["delete"])
        self.student_unpaid.setText(t["set_unpaid"])
        self.student_paid.setText(t["paid"])
        self.rev_add.setText(t["add"])
        self.rev_edit.setText(t["edit"])
        self.rev_delete.setText(t["delete"])

        self.refresh_all()
        self.price_save.setText(T[self.lang]["save"])
        self.add_paid_hours.setText(T[self.lang]["add_paid_hours"])
        self.student_add.setText(T[self.lang]["add"])
        self.student_edit.setText(T[self.lang]["edit"])
        self.student_delete.setText(T[self.lang]["delete"])
        self.student_unpaid.setText(T[self.lang]["set_unpaid"])
        self.student_paid.setText(T[self.lang]["paid"])
        self.rev_add.setText(T[self.lang]["add"])
        self.rev_edit.setText(T[self.lang]["edit"])
        self.rev_delete.setText(T[self.lang]["delete"])
        self.refresh_all()
        self.rebuild_weekly_clicks()

    def style(self):
        self.setStyleSheet("""
        QWidget {
            background: #15171a;
            color: #eeeeee;
            font-size: 14px;
        }
        QFrame#sidebar {
            background: #101214;
            border-right: 1px solid #30343a;
        }
        QLabel#titleIcon {
            font-size: 28px;
            font-weight: bold;
            padding: 8px;
        }
        QLabel#appName {
            font-size: 21px;
            font-weight: bold;
            padding: 6px 4px 14px 4px;
            min-width: 230px;
        }
        QLabel#pageTitle {
            font-size: 27px;
            font-weight: bold;
            padding: 8px 0 15px 0;
        }
        QLabel#stats {
            background: #20242a;
            border: 1px solid #30343a;
            border-radius: 10px;
            padding: 20px;
            font-size: 18px;
        }
        QPushButton#nav {
            text-align: left;
            padding: 12px;
            border: none;
            border-radius: 6px;
            background: transparent;
        }
        QPushButton#nav:hover {
            background: #24282e;
        }
        QPushButton#nav:checked {
            background: #30353d;
            font-weight: bold;
        }
        QPushButton {
            padding: 7px 13px;
            border-radius: 6px;
            border: 1px solid #3b4149;
            background: #252a30;
        }
        QPushButton:hover {
            background: #30363e;
        }
        QPushButton#lesson {
            background: #303944;
            border: 1px solid #596879;
            min-height: 48px;
        }
        QPushButton#empty {
            color: #777e87;
            background: #1b1e22;
            border: 1px solid #272b30;
        }
        QLineEdit, QComboBox, QDateEdit, QTimeEdit {
            background: #20242a;
            border: 1px solid #3a4048;
            border-radius: 5px;
            padding: 6px;
        }

        QSpinBox {
            background: #20242a;
            color: #e7e9ec;
            border: 1px solid #3a4048;
            border-radius: 5px;
            padding-left: 6px;
            padding-right: 28px;
            min-width: 110px;
        }

        QSpinBox::up-button,
        QSpinBox::down-button {
            width: 20px;
            subcontrol-origin: border;
            border: none;
            background: #2a2f36;
        }

        QSpinBox::up-button:hover,
        QSpinBox::down-button:hover {
            background: #39414a;
        }

        QSpinBox::up-button {
            subcontrol-position: top right;
        }

        QSpinBox::down-button {
            subcontrol-position: bottom right;
        }
        QTableWidget {
            background: #1b1e22;
            gridline-color: #343941;
            border: 1px solid #343941;
        }
        QHeaderView::section {
            background: #252a30;
            padding: 8px;
            border: none;
        }
        """)

