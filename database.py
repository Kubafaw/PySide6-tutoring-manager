"""Database access and persistence for Tutor++."""

import sqlite3
from datetime import datetime


class DB:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.setup()

    def setup(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL DEFAULT '',
            unpaid_hours REAL NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS lessons(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            lesson_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            duration REAL NOT NULL,
            paid INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS weekly_plan(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            weekday INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            duration REAL NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS monthly_revenue(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT UNIQUE NOT NULL,
            hours INTEGER NOT NULL DEFAULT 0,
            amount REAL NOT NULL DEFAULT 0,
            notes TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT
        );

        INSERT OR IGNORE INTO settings(key, value)
        VALUES('hourly_price', '50');
        """)
        self.conn.commit()

    def price(self):
        return float(self.conn.execute(
            "SELECT value FROM settings WHERE key='hourly_price'"
        ).fetchone()[0])

    def set_price(self, value):
        self.conn.execute(
            "INSERT OR REPLACE INTO settings(key,value) VALUES('hourly_price',?)",
            (str(value),)
        )
        self.conn.commit()

    def students(self):
        return self.conn.execute(
            "SELECT id,name,unpaid_hours FROM students ORDER BY name"
        ).fetchall()

    def add_student(self, name):
        self.conn.execute("INSERT INTO students(name) VALUES(?)", (name,))
        self.conn.commit()

    def update_student(self, sid, name):
        self.conn.execute("UPDATE students SET name=? WHERE id=?", (name, sid))
        self.conn.commit()

    def delete_student(self, sid):
        self.conn.execute("DELETE FROM students WHERE id=?", (sid,))
        self.conn.commit()

    def set_unpaid_hours(self, sid, hours):
        self.conn.execute(
            "UPDATE students SET unpaid_hours=? WHERE id=?", (float(hours), sid)
        )
        self.conn.commit()

    def add_paid_hours(self, hours):
        hours = float(hours)
        if hours <= 0:
            return 0.0
        amount = hours * self.price()
        month = datetime.now().strftime("%Y-%m")
        existing = self.conn.execute(
            "SELECT id, hours, amount FROM monthly_revenue WHERE month=?", (month,)
        ).fetchone()
        if existing:
            self.conn.execute(
                "UPDATE monthly_revenue SET hours=?, amount=? WHERE id=?",
                (int(existing[1]) + int(hours), float(existing[2]) + amount, existing[0])
            )
        else:
            self.conn.execute(
                "INSERT INTO monthly_revenue(month, hours, amount, notes) VALUES(?,?,?,?)",
                (month, int(hours), amount, "")
            )
        self.conn.commit()
        return amount

    def mark_student_paid(self, sid):
        row = self.conn.execute(
            "SELECT unpaid_hours FROM students WHERE id=?", (sid,)
        ).fetchone()
        if not row:
            return 0.0
        unpaid = float(row[0] or 0)
        amount = unpaid * self.price()
        month = datetime.now().strftime("%Y-%m")

        existing = self.conn.execute(
            "SELECT id, hours, amount FROM monthly_revenue WHERE month=?", (month,)
        ).fetchone()

        if existing:
            self.conn.execute(
                "UPDATE monthly_revenue SET hours=?, amount=? WHERE id=?",
                (int(existing[1]) + int(unpaid), float(existing[2]) + amount, existing[0])
            )
        else:
            self.conn.execute(
                "INSERT INTO monthly_revenue(month, hours, amount, notes) VALUES(?,?,?,?)",
                (month, int(unpaid), amount, "")
            )

        self.conn.execute(
            "UPDATE students SET unpaid_hours=0 WHERE id=?", (sid,)
        )
        self.conn.commit()
        return amount

    def lessons_for_student(self, sid):
        return self.conn.execute(
            "SELECT duration,paid FROM lessons WHERE student_id=?", (sid,)
        ).fetchall()

    def refresh_unpaid(self):
        rows = self.conn.execute("SELECT id FROM students").fetchall()
        for (sid,) in rows:
            unpaid = self.conn.execute(
                "SELECT COALESCE(SUM(duration),0) FROM lessons "
                "WHERE student_id=? AND paid=0", (sid,)
            ).fetchone()[0]
            self.conn.execute(
                "UPDATE students SET unpaid_hours=? WHERE id=?", (unpaid, sid)
            )
        self.conn.commit()

    def weekly(self):
        return self.conn.execute("""
            SELECT w.id,w.student_id,s.name,w.weekday,w.start_time,w.duration
            FROM weekly_plan w JOIN students s ON s.id=w.student_id
            ORDER BY w.weekday,w.start_time
        """).fetchall()

    def add_weekly(self, sid, weekday, start, duration):
        self.conn.execute(
            "INSERT INTO weekly_plan(student_id,weekday,start_time,duration) VALUES(?,?,?,?)",
            (sid, weekday, start, duration)
        )
        self.conn.commit()

    def delete_weekly(self, wid):
        self.conn.execute("DELETE FROM weekly_plan WHERE id=?", (wid,))
        self.conn.commit()

    def revenue(self):
        return self.conn.execute(
            "SELECT id,month,hours,amount,notes FROM monthly_revenue ORDER BY month DESC"
        ).fetchall()

    def add_revenue(self, month, hours, amount, notes):
        self.conn.execute(
            "INSERT INTO monthly_revenue(month,hours,amount,notes) VALUES(?,?,?,?)",
            (month, int(hours), amount, notes)
        )
        self.conn.commit()

    def update_revenue(self, rid, month, hours, amount, notes):
        self.conn.execute(
            "UPDATE monthly_revenue SET month=?,hours=?,amount=?,notes=? WHERE id=?",
            (month, int(hours), amount, notes, rid)
        )
        self.conn.commit()

    def delete_revenue(self, rid):
        self.conn.execute("DELETE FROM monthly_revenue WHERE id=?", (rid,))
        self.conn.commit()

