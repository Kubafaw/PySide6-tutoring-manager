# Tutor++

**Tutor++** is a desktop application designed to simplify the management of private tutoring. It helps tutors organize students, track unpaid hours, manage weekly schedules, and monitor monthly revenue in one place.

Built with Python and PySide6, the application features a dark user interface, Polish and English language support, and SQLite database storage.

## Features

- **Student Management** — Add, edit, and remove students.
- **Unpaid Hours Tracking** — Track the number of hours each student needs to pay for and calculate the amount due.
- **Payment Management** — Mark a student's outstanding hours as paid and automatically record the payment.
- **Weekly Schedule** — Manage tutoring sessions using a weekly timetable with hourly time slots.
- **Monthly Revenue Tracking** — Store and manage monthly revenue, including the number of hours and additional notes.
- **Hourly Rate Configuration** — Set a global hourly rate used to calculate payment amounts.
- **Manual Revenue Entries** — Record paid hours independently of individual student records.
- **Bilingual Interface** — Switch between Polish and English.
- **Persistent Storage** — Save application data in a local SQLite database.
- **Windows Executable** — Package the application as a standalone Windows executable using PyInstaller.

## Technology Stack

- **Python** — Application logic
- **PySide6** — Desktop graphical user interface
- **SQLite** — Local database
- **PyInstaller** — Windows executable packaging

## Project Structure

```text
Tutor++/
├── main.py              # Application entry point
├── main_window.py       # Main window and interface logic
├── database.py          # Database operations
├── dialogs.py           # Dialog windows
├── translations.py      # Polish and English translations
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── tutoring.db          # Local application database
```

## Getting Started

### Requirements

- Python 3.12 or a compatible Python version
- PyCharm or another Python IDE

### Installation

1. Clone or download this repository.
2. Open the project directory in PyCharm.
3. Install the required dependencies using the PyCharm Terminal:

```powershell
python -m pip install -r requirements.txt
```

### Running the Application

Run `main.py` from PyCharm or execute:

```powershell
python main.py
```

The application uses a local SQLite database named `tutoring.db`.

## Building a Windows Executable

Install PyInstaller:

```powershell
python -m pip install pyinstaller
```

Build the application:

```powershell
python -m PyInstaller --onefile --windowed main.py
```

The executable will be generated in the `dist` directory.

When distributing the executable, keep `tutoring.db` next to the `.exe`. The application should use the database path relative to the executable so that saved data remains persistent.

## Data Storage

Tutor++ stores student information, unpaid hours, weekly schedule entries, application settings, and monthly revenue in SQLite.

Keep a backup of `tutoring.db` to preserve your data when moving or updating the application.

## License

No license has been specified yet. Add a `LICENSE` file before distributing the project under an open-source license.
