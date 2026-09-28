#!/usr/bin/env python3
"""
studylytics.py

STUDYLYTICS - a small, growing toolbox of study tools.

Subjects: a persistent tab bar at the top of the app (e.g. "CCNA",
"Security+"). Every tool below it - Study Timer and Scheduler - is scoped
to whichever subject tab is active, so tasks/sessions/goals/reviews from
different subjects never mix. Use the "+" to add a subject, and "clear"
on a tab to wipe that subject's data (optionally deleting the tab too)
once you're done with it.

Tools:
  - Study Timer: time study sessions, see totals/averages/goal progress.
  - Scheduler:   spaced-repetition review calendar. The first time you log
                 a session for a task, reviews are auto-scheduled at
                 whatever intervals you've set. Today's due reviews also
                 show as a checklist on the home screen.

This file is the whole app. Uses only tkinter + sqlite3, both built into
Python - no installs needed.

Run with:
    python3 studylytics.py

Or, on Linux, run install_launcher.sh once to add a proper clickable app
icon to your app menu (and pin it to your dock/taskbar from there).
"""

import calendar
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date, timedelta

DB_FILE = "study_data.db"
DEFAULT_SUBJECT = "General"

# ---------------------------------------------------------------------------
# Retro color palette + fonts, shared across the whole app
# ---------------------------------------------------------------------------

COLORS = {
    "bg": "#f0e6d2",        # warm cream background
    "panel": "#e4d5b7",     # slightly darker cream for panels/cards
    "fg": "#2b2320",        # near-black brown text
    "accent": "#b5451b",    # rust orange (Study Timer)
    "accent2": "#3a6b5c",   # muted teal (Scheduler)
    "accent3": "#4c6b8a",   # muted slate blue (Notes)
    "accent4": "#8a3a3a",   # brick red (Mistake Log)
    "accent5": "#4f7c4f",   # muted green (Pace Tracker)
    "border": "#2b2320",
    "muted": "#8a7f6d",
    "highlight": "#f5d16f", # gold - used to highlight linked note segments
}

FONT_TITLE = ("Courier New", 28, "bold")
FONT_SUBTITLE = ("Courier New", 11)
FONT_HEADER = ("Courier New", 14, "bold")
FONT_BODY = ("Courier New", 10)
FONT_BODY_BOLD = ("Courier New", 10, "bold")
FONT_MONO_BIG = ("Consolas", 28)


# ---------------------------------------------------------------------------
# Tiny pixel-art icons (8x8 bitmaps drawn on a Canvas - no image files needed)
# ---------------------------------------------------------------------------

STOPWATCH_ICON = [
    "..####..",
    ".#....#.",
    "#.####.#",
    "#.#..#.#",
    "#.#..#.#",
    "#.####.#",
    ".#....#.",
    "..####..",
]

CALENDAR_ICON = [
    "########",
    "#......#",
    "#.####.#",
    "#.#..#.#",
    "#.####.#",
    "#.#..#.#",
    "#.####.#",
    "########",
]

NOTE_ICON = [
    "........",
    "########",
    "........",
    "########",
    "........",
    "########",
    "........",
    "........",
]

MISTAKE_ICON = [
    "#......#",
    ".#....#.",
    "..#..#..",
    "...##...",
    "...##...",
    "..#..#..",
    ".#....#.",
    "#......#",
]

PACE_ICON = [
    "........",
    "........",
    "......##",
    ".....###",
    "....####",
    "...#####",
    "..######",
    "########",
]


def draw_pixel_icon(canvas, pattern, x0, y0, pixel_size, color):
    for row_index, row in enumerate(pattern):
        for col_index, char in enumerate(row):
            if char == "#":
                x1 = x0 + col_index * pixel_size
                y1 = y0 + row_index * pixel_size
                canvas.create_rectangle(
                    x1, y1, x1 + pixel_size, y1 + pixel_size,
                    fill=color, outline=""
                )


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_connection():
    return sqlite3.connect(DB_FILE)


def _column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            subject TEXT NOT NULL DEFAULT 'General',
            start_time TEXT NOT NULL,
            stop_time TEXT NOT NULL,
            duration_minutes REAL NOT NULL
        )
    """)
    if not _column_exists(cur, "sessions", "subject"):
        cur.execute("ALTER TABLE sessions ADD COLUMN subject TEXT NOT NULL DEFAULT 'General'")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            subject TEXT NOT NULL DEFAULT 'General',
            review_date TEXT NOT NULL,
            interval_days INTEGER NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0
        )
    """)
    if not _column_exists(cur, "scheduled_reviews", "subject"):
        cur.execute("ALTER TABLE scheduled_reviews ADD COLUMN subject TEXT NOT NULL DEFAULT 'General'")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS review_intervals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            days INTEGER NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            subject TEXT PRIMARY KEY,
            content TEXT NOT NULL DEFAULT ''
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS subject_goals (
            subject TEXT PRIMARY KEY,
            daily_goal_minutes REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS mistakes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            due_date TEXT NOT NULL
        )
    """)

    # goals needs a composite primary key (task, subject). If an old
    # single-subject goals table exists, migrate its rows into 'General'.
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='goals'")
    goals_exists = cur.fetchone() is not None
    if not goals_exists:
        cur.execute("""
            CREATE TABLE goals (
                task TEXT NOT NULL,
                subject TEXT NOT NULL DEFAULT 'General',
                allotted_minutes REAL NOT NULL,
                PRIMARY KEY (task, subject)
            )
        """)
    elif not _column_exists(cur, "goals", "subject"):
        cur.execute("ALTER TABLE goals RENAME TO goals_old")
        cur.execute("""
            CREATE TABLE goals (
                task TEXT NOT NULL,
                subject TEXT NOT NULL DEFAULT 'General',
                allotted_minutes REAL NOT NULL,
                PRIMARY KEY (task, subject)
            )
        """)
        cur.execute("INSERT INTO goals (task, subject, allotted_minutes) "
                    "SELECT task, 'General', allotted_minutes FROM goals_old")
        cur.execute("DROP TABLE goals_old")

    # Seed default review intervals the first time the app runs
    cur.execute("SELECT COUNT(*) FROM review_intervals")
    if cur.fetchone()[0] == 0:
        for days in (1, 3, 7, 14, 30):
            cur.execute("INSERT INTO review_intervals (days) VALUES (?)", (days,))

    # Always have at least one subject tab to land on
    cur.execute("SELECT COUNT(*) FROM subjects")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO subjects (name) VALUES (?)", (DEFAULT_SUBJECT,))

    conn.commit()
    conn.close()


# --- Subjects ---

def get_subjects():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM subjects ORDER BY id")
    names = [r[0] for r in cur.fetchall()]
    conn.close()
    return names


def add_subject(name):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # already exists
    conn.close()


def delete_subject(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM subjects WHERE name = ?", (name,))
    conn.commit()
    conn.close()


def clear_subject_data(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE subject = ?", (name,))
    cur.execute("DELETE FROM goals WHERE subject = ?", (name,))
    cur.execute("DELETE FROM scheduled_reviews WHERE subject = ?", (name,))
    cur.execute("DELETE FROM notes WHERE subject = ?", (name,))
    cur.execute("DELETE FROM subject_goals WHERE subject = ?", (name,))
    cur.execute("DELETE FROM mistakes WHERE subject = ?", (name,))
    conn.commit()
    conn.close()


# --- Study Timer data (all scoped to a subject) ---

def add_session(task, start_dt, stop_dt, subject):
    duration_minutes = round((stop_dt - start_dt).total_seconds() / 60, 2)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (task, subject, start_time, stop_time, duration_minutes) VALUES (?, ?, ?, ?, ?)",
        (task, subject, start_dt.strftime("%Y-%m-%d %H:%M:%S"), stop_dt.strftime("%Y-%m-%d %H:%M:%S"), duration_minutes),
    )
    conn.commit()
    conn.close()
    return duration_minutes


def get_all_sessions(subject):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT task, start_time, stop_time, duration_minutes FROM sessions WHERE subject = ? ORDER BY start_time DESC",
        (subject,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_known_tasks(subject):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT task FROM sessions WHERE subject = ? ORDER BY task", (subject,))
    tasks = [row[0] for row in cur.fetchall()]
    conn.close()
    return tasks


def get_stats(subject):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT task,
               SUM(duration_minutes) AS total_minutes,
               COUNT(*) AS session_count,
               AVG(duration_minutes) AS avg_minutes
        FROM sessions
        WHERE subject = ?
        GROUP BY task
        ORDER BY total_minutes DESC
    """, (subject,))
    rows = cur.fetchall()
    conn.close()
    return rows


def set_goal(task, subject, minutes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM goals WHERE task = ? AND subject = ?", (task, subject))
    cur.execute("INSERT INTO goals (task, subject, allotted_minutes) VALUES (?, ?, ?)", (task, subject, minutes))
    conn.commit()
    conn.close()


def get_goals(subject):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT task, allotted_minutes FROM goals WHERE subject = ? ORDER BY task", (subject,))
    rows = cur.fetchall()
    conn.close()
    return dict(rows)


def delete_goal(task, subject):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM goals WHERE task = ? AND subject = ?", (task, subject))
    conn.commit()
    conn.close()


# --- Scheduler data ---
# Review intervals are shared/global across all subjects (not per-subject).

def get_intervals():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT days FROM review_intervals ORDER BY days")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows


def add_interval(days):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO review_intervals (days) VALUES (?)", (days,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()


def delete_interval(days):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM review_intervals WHERE days = ?", (days,))
    conn.commit()
    conn.close()


def task_has_schedule(task, subject):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM scheduled_reviews WHERE task = ? AND subject = ?", (task, subject))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0


def create_schedule_for_task(task, subject, start_date):
    intervals = get_intervals()
    if not intervals:
        return
    conn = get_connection()
    cur = conn.cursor()
    for days in intervals:
        review_date = (start_date + timedelta(days=days)).isoformat()
        cur.execute(
            "INSERT INTO scheduled_reviews (task, subject, review_date, interval_days, completed) "
            "VALUES (?, ?, ?, ?, 0)",
            (task, subject, review_date, days),
        )
    conn.commit()
    conn.close()


def get_reviews_for_date(date_str, subject):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, task, interval_days, completed FROM scheduled_reviews "
        "WHERE review_date = ? AND subject = ? ORDER BY task",
        (date_str, subject),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_today_incomplete_reviews(subject):
    today_str = date.today().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, task, interval_days FROM scheduled_reviews "
        "WHERE review_date = ? AND subject = ? AND completed = 0 ORDER BY task",
        (today_str, subject),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def set_review_completed(review_id, completed):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE scheduled_reviews SET completed = ? WHERE id = ?", (1 if completed else 0, review_id))
    conn.commit()
    conn.close()


def get_review_dates_in_month(year, month, subject):
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT review_date, completed FROM scheduled_reviews "
        "WHERE subject = ? AND review_date >= ? AND review_date < ?",
        (subject, start.isoformat(), end.isoformat()),
    )
    rows = cur.fetchall()
    conn.close()

    result = {}
    for review_date, completed in rows:
        if review_date not in result:
            result[review_date] = "completed" if completed else "incomplete"
        elif not completed:
            result[review_date] = "incomplete"
    return result


# --- Notes data ---

def get_notes(subject):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT content FROM notes WHERE subject = ?", (subject,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else ""


def save_notes(subject, content):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO notes (subject, content) VALUES (?, ?) "
        "ON CONFLICT(subject) DO UPDATE SET content = excluded.content",
        (subject, content),
    )
    conn.commit()
    conn.close()


# --- Pace tracker data ---

def get_daily_goal(subject):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT daily_goal_minutes FROM subject_goals WHERE subject = ?", (subject,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def set_daily_goal(subject, minutes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO subject_goals (subject, daily_goal_minutes) VALUES (?, ?) "
        "ON CONFLICT(subject) DO UPDATE SET daily_goal_minutes = excluded.daily_goal_minutes",
        (subject, minutes),
    )
    conn.commit()
    conn.close()


def get_today_minutes(subject):
    today_str = date.today().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COALESCE(SUM(duration_minutes), 0) FROM sessions WHERE subject = ? AND start_time LIKE ?",
        (subject, f"{today_str}%"),
    )
    total = cur.fetchone()[0]
    conn.close()
    return total


def get_total_minutes(subject):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(duration_minutes), 0) FROM sessions WHERE subject = ?", (subject,))
    total = cur.fetchone()[0]
    conn.close()
    return total


# --- Mistake log data ---
# A mistake starts due today. Answer it right -> gone for good. Answer it
# wrong -> due again tomorrow.

def add_mistake(subject, question, answer):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO mistakes (subject, question, answer, due_date) VALUES (?, ?, ?, ?)",
        (subject, question, answer, date.today().isoformat()),
    )
    conn.commit()
    conn.close()


def get_due_mistakes(subject):
    today_str = date.today().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, question, answer FROM mistakes WHERE subject = ? AND due_date <= ? ORDER BY due_date, id",
        (subject, today_str),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_mistakes(subject):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, question, answer, due_date FROM mistakes WHERE subject = ? ORDER BY due_date, id",
        (subject,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def resolve_mistake_correct(mistake_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM mistakes WHERE id = ?", (mistake_id,))
    conn.commit()
    conn.close()


def resolve_mistake_incorrect(mistake_id):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE mistakes SET due_date = ? WHERE id = ?", (tomorrow, mistake_id))
    conn.commit()
    conn.close()


def delete_mistake(mistake_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM mistakes WHERE id = ?", (mistake_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Study Timer: Timer / History / Stats / Settings tabs (subject-scoped)
# ---------------------------------------------------------------------------

class TimerTab(ttk.Frame):
    NO_REVIEW_LABEL = "-- not a scheduled review, just log time --"

    def __init__(self, parent, on_session_logged, get_subject):
        super().__init__(parent, padding=20)
        self.on_session_logged = on_session_logged
        self.get_subject = get_subject
        self.running = False
        self.start_time = None
        self.tick_job = None
        self.review_options = {}
        self.selected_review_id = None

        ttk.Label(self, text="DEDICATE THIS SESSION TO A SCHEDULED REVIEW?", font=FONT_BODY_BOLD).pack(anchor="w")
        ttk.Label(self, text="Picking one checks it off instead of creating a separate entry.",
                  foreground=COLORS["muted"], font=FONT_BODY).pack(anchor="w", pady=(0, 4))

        self.review_var = tk.StringVar()
        self.review_combo = ttk.Combobox(self, textvariable=self.review_var, state="readonly", font=FONT_BODY)
        self.review_combo.pack(fill="x", pady=(0, 16))
        self.review_combo.bind("<<ComboboxSelected>>", self.on_review_selected)

        ttk.Label(self, text="WHAT ARE YOU STUDYING?", font=FONT_BODY_BOLD).pack(anchor="w")

        self.task_var = tk.StringVar()
        self.task_combo = ttk.Combobox(self, textvariable=self.task_var, values=[], font=FONT_BODY)
        self.task_combo.pack(fill="x", pady=(4, 16))

        self.elapsed_var = tk.StringVar(value="00:00:00")
        ttk.Label(self, textvariable=self.elapsed_var, font=FONT_MONO_BIG).pack(pady=10)

        self.toggle_btn = ttk.Button(self, text="START", command=self.toggle_timer)
        self.toggle_btn.pack(pady=10, ipadx=20, ipady=6)

        self.status_var = tk.StringVar(value="Not running.")
        ttk.Label(self, textvariable=self.status_var, foreground=COLORS["muted"], font=FONT_BODY).pack(pady=(10, 0))

        self.refresh_all()

    def refresh_all(self):
        """Call whenever the active subject may have changed."""
        self.task_combo.config(values=get_known_tasks(self.get_subject()))
        self.refresh_review_dropdown()

    def refresh_review_dropdown(self):
        self.review_options = {}
        labels = [self.NO_REVIEW_LABEL]
        for review_id, task, interval_days in get_today_incomplete_reviews(self.get_subject()):
            label = f"{task}  (day {interval_days} review)"
            self.review_options[label] = (review_id, task)
            labels.append(label)
        self.review_combo.config(values=labels)
        self.review_var.set(self.NO_REVIEW_LABEL)
        self.selected_review_id = None
        self.task_combo.config(state="normal")

    def on_review_selected(self, event):
        label = self.review_var.get()
        if label == self.NO_REVIEW_LABEL:
            self.selected_review_id = None
            self.task_combo.config(state="normal")
            return
        review_id, task = self.review_options[label]
        self.selected_review_id = review_id
        self.task_var.set(task)
        self.task_combo.config(state="disabled")

    def toggle_timer(self):
        if not self.running:
            task = self.task_var.get().strip()
            if not task:
                messagebox.showwarning("Missing task", "Type or pick what you're studying first.")
                return
            self.running = True
            self.start_time = datetime.now()
            self.toggle_btn.config(text="STOP")
            self.task_combo.config(state="disabled")
            self.review_combo.config(state="disabled")
            self.status_var.set(f"Timing '{task}'...")
            self.tick()
        else:
            self.running = False
            stop_time = datetime.now()
            task = self.task_var.get().strip()
            subject = self.get_subject()
            duration = add_session(task, self.start_time, stop_time, subject)

            if self.selected_review_id is not None:
                set_review_completed(self.selected_review_id, True)
            elif not task_has_schedule(task, subject):
                create_schedule_for_task(task, subject, stop_time.date())

            if self.tick_job:
                self.after_cancel(self.tick_job)
            self.toggle_btn.config(text="START")
            self.review_combo.config(state="readonly")
            self.elapsed_var.set("00:00:00")
            self.status_var.set(f"Logged {duration} minutes for '{task}'.")
            self.refresh_all()
            self.on_session_logged()

    def tick(self):
        if not self.running:
            return
        elapsed = datetime.now() - self.start_time
        total_seconds = int(elapsed.total_seconds())
        h, remainder = divmod(total_seconds, 3600)
        m, s = divmod(remainder, 60)
        self.elapsed_var.set(f"{h:02}:{m:02}:{s:02}")
        self.tick_job = self.after(1000, self.tick)


class HistoryTab(ttk.Frame):
    def __init__(self, parent, get_subject):
        super().__init__(parent, padding=20)
        self.get_subject = get_subject

        columns = ("task", "start_time", "stop_time", "duration_minutes")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col, label, width in [
            ("task", "Task", 160),
            ("start_time", "Start", 150),
            ("stop_time", "Stop", 150),
            ("duration_minutes", "Minutes", 80),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)

        ttk.Button(self, text="Refresh", command=self.refresh).pack(pady=(10, 0))

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for row in get_all_sessions(self.get_subject()):
            self.tree.insert("", "end", values=row)


class StatsTab(ttk.Frame):
    def __init__(self, parent, get_subject):
        super().__init__(parent, padding=20)
        self.get_subject = get_subject

        columns = ("task", "total_minutes", "sessions", "avg_minutes", "goal_progress")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col, label, width in [
            ("task", "Task", 160),
            ("total_minutes", "Total (min)", 90),
            ("sessions", "Sessions", 80),
            ("avg_minutes", "Avg/session (min)", 130),
            ("goal_progress", "Goal progress", 140),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)

        ttk.Button(self, text="Refresh", command=self.refresh).pack(pady=(10, 0))

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        subject = self.get_subject()
        goals = get_goals(subject)
        for task, total_minutes, session_count, avg_minutes in get_stats(subject):
            goal = goals.get(task)
            if goal:
                pct = round(min(total_minutes / goal, 1) * 100, 1)
                progress = f"{round(total_minutes)}/{round(goal)} min ({pct}%)"
            else:
                progress = "no goal set"
            self.tree.insert("", "end", values=(
                task, round(total_minutes, 1), session_count, round(avg_minutes, 1), progress
            ))


class SettingsTab(ttk.Frame):
    def __init__(self, parent, on_goals_changed, get_subject):
        super().__init__(parent, padding=20)
        self.on_goals_changed = on_goals_changed
        self.get_subject = get_subject

        ttk.Label(self, text="SET AN ALLOTTED-TIME GOAL FOR A TASK", font=FONT_BODY_BOLD).pack(anchor="w")

        form = ttk.Frame(self)
        form.pack(fill="x", pady=(6, 16))

        ttk.Label(form, text="Task:", font=FONT_BODY).grid(row=0, column=0, sticky="w")
        self.task_var = tk.StringVar()
        self.task_combo = ttk.Combobox(form, textvariable=self.task_var, values=[], font=FONT_BODY)
        self.task_combo.grid(row=0, column=1, sticky="ew", padx=8)

        ttk.Label(form, text="Goal (minutes):", font=FONT_BODY).grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.minutes_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.minutes_var, font=FONT_BODY).grid(row=1, column=1, sticky="ew", padx=8, pady=(8, 0))

        form.columnconfigure(1, weight=1)

        ttk.Button(self, text="Save goal", command=self.save_goal).pack(anchor="w")

        ttk.Label(self, text="CURRENT GOALS", font=FONT_BODY_BOLD).pack(anchor="w", pady=(20, 4))

        self.goals_tree = ttk.Treeview(self, columns=("task", "minutes"), show="headings", height=6)
        self.goals_tree.heading("task", text="Task")
        self.goals_tree.heading("minutes", text="Allotted minutes")
        self.goals_tree.pack(fill="x")

        ttk.Button(self, text="Delete selected goal", command=self.delete_selected_goal).pack(anchor="w", pady=(8, 0))

        self.refresh_goals()

    def save_goal(self):
        task = self.task_var.get().strip()
        minutes_text = self.minutes_var.get().strip()
        if not task or not minutes_text:
            messagebox.showwarning("Missing info", "Enter both a task and a goal in minutes.")
            return
        try:
            minutes = float(minutes_text)
        except ValueError:
            messagebox.showwarning("Invalid number", "Goal minutes must be a number.")
            return
        set_goal(task, self.get_subject(), minutes)
        self.minutes_var.set("")
        self.refresh_goals()
        self.on_goals_changed()

    def delete_selected_goal(self):
        selected = self.goals_tree.selection()
        if not selected:
            return
        task = self.goals_tree.item(selected[0], "values")[0]
        delete_goal(task, self.get_subject())
        self.refresh_goals()
        self.on_goals_changed()

    def refresh_goals(self):
        self.goals_tree.delete(*self.goals_tree.get_children())
        subject = self.get_subject()
        for task, minutes in get_goals(subject).items():
            self.goals_tree.insert("", "end", values=(task, minutes))
        self.task_combo.config(values=get_known_tasks(subject))


# ---------------------------------------------------------------------------
# Scheduler: Calendar tab (subject-scoped) + Settings (intervals, global)
# ---------------------------------------------------------------------------

class CalendarTab(ttk.Frame):
    def __init__(self, parent, get_subject, on_change=None):
        super().__init__(parent, padding=16)
        self.get_subject = get_subject
        self.on_change = on_change
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.selected_date = today

        nav = tk.Frame(self, bg=COLORS["bg"])
        nav.pack(fill="x")
        ttk.Button(nav, text="<", width=3, command=self.prev_month).pack(side="left")
        self.month_label_var = tk.StringVar()
        tk.Label(nav, textvariable=self.month_label_var, font=FONT_HEADER,
                 bg=COLORS["bg"], fg=COLORS["fg"]).pack(side="left", expand=True)
        ttk.Button(nav, text=">", width=3, command=self.next_month).pack(side="right")

        self.grid_frame = tk.Frame(self, bg=COLORS["bg"])
        self.grid_frame.pack(pady=(12, 0))

        self.detail_title_var = tk.StringVar()
        tk.Label(self, textvariable=self.detail_title_var, font=FONT_BODY_BOLD,
                 bg=COLORS["bg"], fg=COLORS["accent2"]).pack(anchor="w", pady=(20, 4))

        self.detail_frame = tk.Frame(self, bg=COLORS["bg"])
        self.detail_frame.pack(fill="both", expand=True)

        self.render_calendar()

    def prev_month(self):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.render_calendar()

    def next_month(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.render_calendar()

    def render_calendar(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.month_label_var.set(f"{calendar.month_name[self.current_month].upper()} {self.current_year}")

        for col, name in enumerate(["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]):
            tk.Label(self.grid_frame, text=name, font=FONT_BODY_BOLD, bg=COLORS["bg"],
                     fg=COLORS["muted"], width=6).grid(row=0, column=col, pady=(0, 4))

        cal = calendar.Calendar(firstweekday=6)
        weeks = cal.monthdayscalendar(self.current_year, self.current_month)
        review_info = get_review_dates_in_month(self.current_year, self.current_month, self.get_subject())
        today = date.today()

        for row_index, week in enumerate(weeks, start=1):
            for col_index, day_num in enumerate(week):
                if day_num == 0:
                    tk.Label(self.grid_frame, text="", bg=COLORS["bg"], width=6, height=2).grid(
                        row=row_index, column=col_index, padx=2, pady=2)
                    continue

                this_date = date(self.current_year, self.current_month, day_num)
                marker = review_info.get(this_date.isoformat())

                bg, fg = COLORS["panel"], COLORS["fg"]
                if this_date == self.selected_date:
                    bg, fg = COLORS["accent"], COLORS["bg"]
                elif this_date == today:
                    bg, fg = COLORS["accent2"], COLORS["bg"]

                cell = tk.Frame(self.grid_frame, width=60, height=48, bg=bg, relief="ridge", bd=1, cursor="hand2")
                cell.grid(row=row_index, column=col_index, padx=2, pady=2)
                cell.grid_propagate(False)

                clickable_widgets = [cell]

                day_label = tk.Label(cell, text=str(day_num), font=FONT_BODY, bg=bg, fg=fg)
                day_label.place(relx=0.5, rely=0.55, anchor="center")
                clickable_widgets.append(day_label)

                if marker == "completed":
                    dot_label = tk.Label(cell, text=".", font=FONT_BODY_BOLD, bg=bg, fg=fg)
                    dot_label.place(relx=0.5, rely=0.85, anchor="center")
                    clickable_widgets.append(dot_label)
                elif marker == "incomplete":
                    badge = tk.Label(cell, text="!", font=("Courier New", 13, "bold"),
                                      bg=bg, fg="#d1291b")
                    badge.place(relx=0.92, rely=0.1, anchor="ne")
                    clickable_widgets.append(badge)

                for widget in clickable_widgets:
                    widget.bind("<Button-1>", lambda event, d=this_date: self.select_day(d))

        self.render_day_details()

    def select_day(self, the_date):
        self.selected_date = the_date
        self.render_calendar()

    def render_day_details(self):
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        label_date = self.selected_date.strftime("%A, %B %d").upper()
        self.detail_title_var.set(f"REVIEWS FOR {label_date}")

        reviews = get_reviews_for_date(self.selected_date.isoformat(), self.get_subject())
        if not reviews:
            tk.Label(self.detail_frame, text="No reviews scheduled.", font=FONT_BODY,
                     bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w")
            return

        for review_id, task, interval_days, completed in reviews:
            var = tk.IntVar(value=completed)
            label_text = f"{task}   (day {interval_days} review)"
            tk.Checkbutton(
                self.detail_frame, text=label_text, variable=var, font=FONT_BODY,
                bg=COLORS["bg"], fg=COLORS["fg"], selectcolor=COLORS["panel"],
                activebackground=COLORS["bg"], anchor="w",
                command=lambda rid=review_id, v=var: self.on_toggle(rid, v)
            ).pack(anchor="w", pady=2)

    def on_toggle(self, review_id, var):
        set_review_completed(review_id, bool(var.get()))
        self.render_calendar()
        if self.on_change:
            self.on_change()


class IntervalSettingsTab(ttk.Frame):
    def __init__(self, parent, on_change=None):
        super().__init__(parent, padding=20)
        self.on_change = on_change

        tk.Label(self, text="REVIEW INTERVALS (DAYS AFTER INITIAL LEARNING)", font=FONT_BODY_BOLD,
                 bg=COLORS["bg"], fg=COLORS["fg"]).pack(anchor="w")
        tk.Label(self, text="Shared across every subject. When you first log time on a new task, "
                             "reviews are automatically scheduled this many days later.",
                 font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["muted"], wraplength=480,
                 justify="left").pack(anchor="w", pady=(2, 12))

        form = ttk.Frame(self)
        form.pack(fill="x")
        self.days_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.days_var, width=10, font=FONT_BODY).pack(side="left")
        ttk.Button(form, text="Add interval", command=self.add_interval_clicked).pack(side="left", padx=8)

        self.list_frame = tk.Frame(self, bg=COLORS["bg"])
        self.list_frame.pack(fill="x", pady=(16, 0))

        self.refresh()

    def add_interval_clicked(self):
        text = self.days_var.get().strip()
        if not text:
            return
        try:
            days = int(text)
            if days <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid number", "Enter a whole number of days greater than 0.")
            return
        add_interval(days)
        self.days_var.set("")
        self.refresh()
        if self.on_change:
            self.on_change()

    def delete_interval_clicked(self, days):
        delete_interval(days)
        self.refresh()
        if self.on_change:
            self.on_change()

    def refresh(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        intervals = get_intervals()
        if not intervals:
            tk.Label(self.list_frame, text="No intervals set - reviews won't auto-schedule until you add one.",
                     font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w")
            return
        for days in intervals:
            row = tk.Frame(self.list_frame, bg=COLORS["bg"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"Review {days} day{'s' if days != 1 else ''} after learning",
                     font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["fg"]).pack(side="left")
            ttk.Button(row, text="Delete", command=lambda d=days: self.delete_interval_clicked(d)).pack(side="right")


# ---------------------------------------------------------------------------
# Pages: MenuPage, StudyTimerPage, SchedulerPage
# ---------------------------------------------------------------------------

class ToolTile(tk.Frame):
    def __init__(self, parent, icon_pattern, icon_color, title, description, on_click=None, enabled=True):
        super().__init__(
            parent, bg=COLORS["panel"], highlightbackground=COLORS["border"],
            highlightthickness=2, bd=0, cursor="hand2" if enabled else "arrow"
        )
        self.on_click = on_click
        self.enabled = enabled

        canvas = tk.Canvas(self, width=64, height=64, bg=COLORS["panel"], highlightthickness=0)
        canvas.pack(side="left", padx=16, pady=16)
        draw_pixel_icon(canvas, icon_pattern, x0=0, y0=0, pixel_size=8,
                         color=icon_color if enabled else COLORS["muted"])

        text_frame = tk.Frame(self, bg=COLORS["panel"])
        text_frame.pack(side="left", fill="both", expand=True, pady=16, padx=(0, 16))

        title_color = COLORS["fg"] if enabled else COLORS["muted"]
        tk.Label(text_frame, text=title, font=FONT_HEADER, bg=COLORS["panel"], fg=title_color,
                 anchor="w").pack(fill="x")
        tk.Label(text_frame, text=description, font=FONT_BODY, bg=COLORS["panel"], fg=COLORS["muted"],
                 anchor="w", justify="left", wraplength=280).pack(fill="x", pady=(4, 0))

        if not enabled:
            tk.Label(text_frame, text="[ COMING SOON ]", font=FONT_BODY_BOLD, bg=COLORS["panel"],
                     fg=COLORS["accent2"], anchor="w").pack(fill="x", pady=(6, 0))

        if enabled:
            for widget in (self, canvas, text_frame, *text_frame.winfo_children()):
                widget.bind("<Button-1>", self._handle_click)
                widget.bind("<Enter>", self._on_enter)
                widget.bind("<Leave>", self._on_leave)

    def _handle_click(self, event):
        if self.on_click:
            self.on_click()

    def _on_enter(self, event):
        self.config(highlightbackground=COLORS["accent"])

    def _on_leave(self, event):
        self.config(highlightbackground=COLORS["border"])


class MenuPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Bg.TFrame")
        self.controller = controller

        # The home screen has grown past one screenful, so it scrolls. The
        # canvas + inner frame is the standard tkinter scrolling pattern.
        canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLORS["bg"])

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _scroll_up(event):
            canvas.yview_scroll(-3 if event.num == 4 else int(-1 * (event.delta / 120)), "units")

        def _scroll_down(event):
            canvas.yview_scroll(3 if event.num == 5 else int(-1 * (event.delta / 120)), "units")

        def _bind_scroll(event):
            canvas.bind_all("<MouseWheel>", _scroll_up)
            canvas.bind_all("<Button-4>", _scroll_up)
            canvas.bind_all("<Button-5>", _scroll_down)

        def _unbind_scroll(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        canvas.bind("<Enter>", _bind_scroll)
        canvas.bind("<Leave>", _unbind_scroll)

        header = tk.Frame(scroll_frame, bg=COLORS["bg"])
        header.pack(fill="x", pady=(24, 8))
        tk.Label(header, text="S T U D Y L Y T I C S", font=FONT_TITLE,
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack()
        tk.Label(header, text="// your study toolbox", font=FONT_SUBTITLE,
                 bg=COLORS["bg"], fg=COLORS["muted"]).pack(pady=(2, 0))

        tk.Frame(scroll_frame, bg=COLORS["border"], height=2).pack(fill="x", padx=40, pady=(10, 16))

        tiles_container = tk.Frame(scroll_frame, bg=COLORS["bg"])
        tiles_container.pack(fill="x", padx=40)

        ToolTile(
            tiles_container, icon_pattern=STOPWATCH_ICON, icon_color=COLORS["accent"],
            title="STUDY TIMER",
            description="Time your study sessions and see totals, averages, and goal progress per task.",
            on_click=lambda: controller.show_page("study_timer"), enabled=True,
        ).pack(fill="x", pady=6)

        ToolTile(
            tiles_container, icon_pattern=CALENDAR_ICON, icon_color=COLORS["accent2"],
            title="SCHEDULER",
            description="Auto-schedules spaced-repetition reviews based on what you've studied.",
            on_click=lambda: controller.show_page("scheduler"), enabled=True,
        ).pack(fill="x", pady=6)

        ToolTile(
            tiles_container, icon_pattern=NOTE_ICON, icon_color=COLORS["accent3"],
            title="NOTES",
            description="Paste notes and highlight how two concepts relate to each other nearby.",
            on_click=lambda: controller.show_page("notes"), enabled=True,
        ).pack(fill="x", pady=6)

        ToolTile(
            tiles_container, icon_pattern=MISTAKE_ICON, icon_color=COLORS["accent4"],
            title="MISTAKE LOG",
            description="Log missed practice questions - answer them right once and they're gone for good.",
            on_click=lambda: controller.show_page("mistake_log"), enabled=True,
        ).pack(fill="x", pady=6)

        ToolTile(
            tiles_container, icon_pattern=PACE_ICON, icon_color=COLORS["accent5"],
            title="PACE TRACKER",
            description="Set a daily study-time goal per subject and see your all-time totals.",
            on_click=lambda: controller.show_page("pace_tracker"), enabled=True,
        ).pack(fill="x", pady=6)

        tk.Frame(scroll_frame, bg=COLORS["border"], height=2).pack(fill="x", padx=40, pady=(16, 8))

        goal_header = tk.Frame(scroll_frame, bg=COLORS["bg"])
        goal_header.pack(fill="x", padx=40)
        self.goal_title_var = tk.StringVar(value="TODAY'S GOAL")
        tk.Label(goal_header, textvariable=self.goal_title_var, font=FONT_BODY_BOLD,
                 bg=COLORS["bg"], fg=COLORS["accent5"]).pack(anchor="w")

        self.goal_progress_var = tk.StringVar()
        tk.Label(scroll_frame, textvariable=self.goal_progress_var, font=FONT_BODY,
                 bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w", padx=40, pady=(2, 4))

        self._goal_pct = 0
        self.goal_canvas = tk.Canvas(scroll_frame, height=18, bg=COLORS["panel"],
                                      highlightthickness=1, highlightbackground=COLORS["border"])
        self.goal_canvas.pack(fill="x", padx=40, pady=(0, 20))
        self.goal_canvas.bind("<Configure>", lambda e: self._draw_goal_bar())

        todo_header = tk.Frame(scroll_frame, bg=COLORS["bg"])
        todo_header.pack(fill="x", padx=40)
        self.todo_title_var = tk.StringVar(value="TODAY'S REVIEWS")
        tk.Label(todo_header, textvariable=self.todo_title_var, font=FONT_BODY_BOLD,
                 bg=COLORS["bg"], fg=COLORS["accent2"]).pack(anchor="w")

        self.todo_frame = tk.Frame(scroll_frame, bg=COLORS["bg"])
        self.todo_frame.pack(fill="both", expand=True, padx=40, pady=(4, 20))

        mistakes_header = tk.Frame(scroll_frame, bg=COLORS["bg"])
        mistakes_header.pack(fill="x", padx=40)
        self.mistakes_title_var = tk.StringVar(value="MISTAKES TO REVIEW")
        tk.Label(mistakes_header, textvariable=self.mistakes_title_var, font=FONT_BODY_BOLD,
                 bg=COLORS["bg"], fg=COLORS["accent4"]).pack(anchor="w")

        self.mistake_frame = tk.Frame(scroll_frame, bg=COLORS["bg"])
        self.mistake_frame.pack(fill="both", expand=True, padx=40, pady=(4, 30))

        self.refresh_all()

    def on_show(self):
        self.refresh_all()

    def refresh_all(self):
        self.refresh_goal_bar()
        self.refresh_todo()
        self.refresh_mistake_review()

    # --- Today's goal progress bar ---

    def refresh_goal_bar(self):
        subject = self.controller.current_subject
        goal = get_daily_goal(subject)
        today_minutes = get_today_minutes(subject)

        if goal:
            pct = min(today_minutes / goal, 1.0) * 100
            self.goal_progress_var.set(f"{subject}: {round(today_minutes)} / {round(goal)} min ({round(pct)}%)")
        else:
            pct = 0
            self.goal_progress_var.set(f"{subject}: {round(today_minutes)} min logged (no daily goal set)")

        self._goal_pct = pct
        self._draw_goal_bar()

    def _draw_goal_bar(self):
        self.goal_canvas.delete("all")
        width = self.goal_canvas.winfo_width()
        if width <= 1:
            return
        fill_width = int(width * (self._goal_pct / 100))
        self.goal_canvas.create_rectangle(0, 0, fill_width, 18, fill=COLORS["accent5"], outline="")

    # --- Today's scheduled reviews ---

    def refresh_todo(self):
        for widget in self.todo_frame.winfo_children():
            widget.destroy()

        subject = self.controller.current_subject
        self.todo_title_var.set(f"TODAY'S REVIEWS - {subject}")

        reviews = get_today_incomplete_reviews(subject)
        if not reviews:
            tk.Label(self.todo_frame, text="Nothing due today.", font=FONT_BODY,
                     bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w")
            return

        for review_id, task, interval_days in reviews:
            self._add_todo_row(review_id, task, interval_days)

    def _add_todo_row(self, review_id, task, interval_days):
        row = tk.Frame(self.todo_frame, bg=COLORS["bg"])
        row.pack(fill="x", pady=2, anchor="w")
        var = tk.IntVar(value=0)

        def on_check():
            set_review_completed(review_id, True)
            row.destroy()

        tk.Checkbutton(
            row, text=f"Review: {task}   (day {interval_days})", variable=var, font=FONT_BODY,
            bg=COLORS["bg"], fg=COLORS["fg"], selectcolor=COLORS["panel"],
            activebackground=COLORS["bg"], anchor="w", command=on_check
        ).pack(anchor="w")

    # --- Mistake-log flashcard review, one card at a time ---

    def refresh_mistake_review(self):
        for widget in self.mistake_frame.winfo_children():
            widget.destroy()

        subject = self.controller.current_subject
        self.mistakes_title_var.set(f"MISTAKES TO REVIEW - {subject}")

        due = get_due_mistakes(subject)
        if not due:
            tk.Label(self.mistake_frame, text="Nothing to review right now.", font=FONT_BODY,
                     bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w")
            return

        mistake_id, question, answer = due[0]
        remaining = len(due)

        card = tk.Frame(self.mistake_frame, bg=COLORS["panel"], relief="ridge", bd=1)
        card.pack(fill="x", pady=4)

        tk.Label(card, text=f"{remaining} card{'s' if remaining != 1 else ''} due", font=FONT_BODY,
                 bg=COLORS["panel"], fg=COLORS["muted"]).pack(anchor="w", padx=14, pady=(10, 0))
        tk.Label(card, text=question, font=FONT_BODY_BOLD, bg=COLORS["panel"], fg=COLORS["fg"],
                 wraplength=480, justify="left").pack(anchor="w", padx=14, pady=(4, 10))

        answer_var = tk.StringVar(value="")
        tk.Label(card, textvariable=answer_var, font=FONT_BODY, bg=COLORS["panel"],
                 fg=COLORS["accent4"], wraplength=480, justify="left").pack(anchor="w", padx=14)

        button_row = tk.Frame(card, bg=COLORS["panel"])
        button_row.pack(anchor="w", padx=14, pady=(8, 14))

        def show_answer():
            answer_var.set(answer)
            show_btn.pack_forget()
            right_btn.pack(side="left", padx=(0, 8))
            wrong_btn.pack(side="left")

        def mark_right():
            resolve_mistake_correct(mistake_id)
            self.refresh_mistake_review()

        def mark_wrong():
            resolve_mistake_incorrect(mistake_id)
            self.refresh_mistake_review()

        show_btn = ttk.Button(button_row, text="Show answer", command=show_answer)
        show_btn.pack(side="left")

        right_btn = ttk.Button(button_row, text="Got it right", command=mark_right)
        wrong_btn = ttk.Button(button_row, text="Got it wrong", command=mark_wrong)


class StudyTimerPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        top_bar = tk.Frame(self, bg=COLORS["bg"])
        top_bar.pack(fill="x")
        ttk.Button(top_bar, text="< MENU", command=lambda: controller.show_page("menu")).pack(
            side="left", padx=16, pady=12)
        self.header_var = tk.StringVar(value="STUDY TIMER")
        tk.Label(top_bar, textvariable=self.header_var, font=FONT_HEADER, bg=COLORS["bg"],
                 fg=COLORS["accent"]).pack(side="left", padx=10)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        get_subject = lambda: self.controller.current_subject

        self.history_tab = HistoryTab(notebook, get_subject=get_subject)
        self.stats_tab = StatsTab(notebook, get_subject=get_subject)
        self.settings_tab = SettingsTab(notebook, on_goals_changed=self.stats_tab.refresh, get_subject=get_subject)
        self.timer_tab = TimerTab(notebook, on_session_logged=self.handle_session_logged, get_subject=get_subject)

        notebook.add(self.timer_tab, text="Timer")
        notebook.add(self.history_tab, text="History")
        notebook.add(self.stats_tab, text="Stats")
        notebook.add(self.settings_tab, text="Settings")

        notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.notebook = notebook

    def on_tab_changed(self, event):
        tab_text = self.notebook.tab(self.notebook.select(), "text")
        if tab_text == "History":
            self.history_tab.refresh()
        elif tab_text == "Stats":
            self.stats_tab.refresh()

    def refresh_data_tabs(self):
        self.history_tab.refresh()
        self.stats_tab.refresh()

    def handle_session_logged(self):
        self.refresh_data_tabs()
        self.controller.refresh_home()

    def on_show(self):
        self.header_var.set(f"STUDY TIMER \u00b7 {self.controller.current_subject}")
        self.refresh_data_tabs()
        self.timer_tab.refresh_all()


class SchedulerPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        top_bar = tk.Frame(self, bg=COLORS["bg"])
        top_bar.pack(fill="x")
        ttk.Button(top_bar, text="< MENU", command=lambda: controller.show_page("menu")).pack(
            side="left", padx=16, pady=12)
        self.header_var = tk.StringVar(value="SCHEDULER")
        tk.Label(top_bar, textvariable=self.header_var, font=FONT_HEADER, bg=COLORS["bg"],
                 fg=COLORS["accent2"]).pack(side="left", padx=10)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.calendar_tab = CalendarTab(notebook, get_subject=lambda: self.controller.current_subject,
                                         on_change=self.notify_change)
        self.settings_tab = IntervalSettingsTab(notebook, on_change=self.notify_change)

        notebook.add(self.calendar_tab, text="Calendar")
        notebook.add(self.settings_tab, text="Settings")

    def notify_change(self):
        self.controller.refresh_home()

    def on_show(self):
        self.header_var.set(f"SCHEDULER \u00b7 {self.controller.current_subject}")
        self.calendar_tab.render_calendar()
        self.settings_tab.refresh()


# ---------------------------------------------------------------------------
# Notes: paste study notes, highlight how two concepts relate nearby
# ---------------------------------------------------------------------------

class NotesPage(ttk.Frame):
    """A notepad per subject. Enter two keywords and 'Highlight Links':
    for every occurrence of keyword 1, the 15 lines above and 15 lines
    below it are checked for keyword 2. If found, everything from
    keyword 1 to keyword 2 (whichever comes first in the text) gets
    highlighted, so you can see how nearby concepts connect."""

    LINE_WINDOW = 15

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.loaded_subject = None

        top_bar = tk.Frame(self, bg=COLORS["bg"])
        top_bar.pack(fill="x")
        ttk.Button(top_bar, text="< MENU", command=self.go_to_menu).pack(side="left", padx=16, pady=12)
        self.header_var = tk.StringVar(value="NOTES")
        tk.Label(top_bar, textvariable=self.header_var, font=FONT_HEADER, bg=COLORS["bg"],
                 fg=COLORS["accent3"]).pack(side="left", padx=10)

        body = ttk.Frame(self, padding=(16, 0, 16, 12))
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Paste your notes below.", font=FONT_BODY_BOLD,
                 bg=COLORS["bg"], fg=COLORS["fg"]).pack(anchor="w")
        tk.Label(body, text="Then enter two related terms and hit 'Highlight links' - any spot where "
                             "keyword 2 shows up within 15 lines of keyword 1 gets highlighted between them.",
                 font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["muted"], wraplength=560,
                 justify="left").pack(anchor="w", pady=(2, 10))

        text_frame = tk.Frame(body, bg=COLORS["bg"])
        text_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        self.notes_text = tk.Text(
            text_frame, wrap="word", font=("Consolas", 10), undo=True,
            bg="#fbf6ea", fg=COLORS["fg"], insertbackground=COLORS["fg"],
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.notes_text.yview)
        self.notes_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.notes_text.tag_configure("link_highlight", background=COLORS["highlight"])

        controls = tk.Frame(body, bg=COLORS["bg"])
        controls.pack(fill="x", pady=(12, 0))

        tk.Label(controls, text="Keyword 1:", font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["fg"]).grid(
            row=0, column=0, sticky="w")
        self.keyword1_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.keyword1_var, font=FONT_BODY, width=18).grid(
            row=0, column=1, padx=(6, 16))

        tk.Label(controls, text="Keyword 2:", font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["fg"]).grid(
            row=0, column=2, sticky="w")
        self.keyword2_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.keyword2_var, font=FONT_BODY, width=18).grid(
            row=0, column=3, padx=(6, 16))

        ttk.Button(controls, text="Highlight links", command=self.run_highlight).grid(row=0, column=4, padx=(0, 8))
        ttk.Button(controls, text="Clear highlights", command=self.clear_highlights).grid(row=0, column=5, padx=(0, 8))
        ttk.Button(controls, text="Save notes", command=self.save_current).grid(row=0, column=6)

        self.status_var = tk.StringVar(value="")
        tk.Label(body, textvariable=self.status_var, font=FONT_BODY, bg=COLORS["bg"],
                 fg=COLORS["muted"]).pack(anchor="w", pady=(8, 0))

    # --- navigation / persistence ---

    def go_to_menu(self):
        self.save_current()
        self.controller.show_page("menu")

    def on_show(self):
        new_subject = self.controller.current_subject
        if self.loaded_subject is not None and self.loaded_subject != new_subject:
            self.save_current()
        if new_subject != self.loaded_subject:
            content = get_notes(new_subject)
            self.notes_text.delete("1.0", "end")
            self.notes_text.insert("1.0", content)
            self.notes_text.tag_remove("link_highlight", "1.0", "end")
            self.status_var.set("")
        self.loaded_subject = new_subject
        self.header_var.set(f"NOTES \u00b7 {new_subject}")

    def save_current(self):
        if self.loaded_subject is not None:
            content = self.notes_text.get("1.0", "end-1c")
            save_notes(self.loaded_subject, content)

    # --- the actual keyword-linking scan ---

    def clear_highlights(self):
        self.notes_text.tag_remove("link_highlight", "1.0", "end")
        self.status_var.set("Highlights cleared.")

    def run_highlight(self):
        keyword1 = self.keyword1_var.get().strip()
        keyword2 = self.keyword2_var.get().strip()
        if not keyword1 or not keyword2:
            messagebox.showwarning("Missing keywords", "Enter both keywords to link.")
            return

        self.save_current()  # never lose text while scanning it

        text_widget = self.notes_text
        text_widget.tag_remove("link_highlight", "1.0", "end")

        last_line = int(text_widget.index("end-1c").split(".")[0])

        # Every occurrence of keyword 1
        keyword1_hits = []
        cursor = "1.0"
        while True:
            pos = text_widget.search(keyword1, cursor, stopindex="end", nocase=True)
            if not pos:
                break
            pos_end = f"{pos}+{len(keyword1)}c"
            keyword1_hits.append((pos, pos_end))
            cursor = pos_end

        match_count = 0
        for k1_start, k1_end in keyword1_hits:
            k1_line = int(k1_start.split(".")[0])
            window_start = f"{max(1, k1_line - self.LINE_WINDOW)}.0"
            window_end = f"{min(last_line, k1_line + self.LINE_WINDOW)}.end"

            # Find every keyword-2 hit in that window, keep the closest one
            best_span = None
            best_distance = None
            search_cursor = window_start
            while True:
                pos2 = text_widget.search(keyword2, search_cursor, stopindex=window_end, nocase=True)
                if not pos2:
                    break
                pos2_end = f"{pos2}+{len(keyword2)}c"
                pos2_line = int(pos2.split(".")[0])
                distance = abs(pos2_line - k1_line)
                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best_span = (pos2, pos2_end)
                search_cursor = pos2_end

            if best_span:
                k2_start, k2_end = best_span
                if text_widget.compare(k1_start, "<=", k2_start):
                    span_start, span_end = k1_start, k2_end
                else:
                    span_start, span_end = k2_start, k1_end
                text_widget.tag_add("link_highlight", span_start, span_end)
                match_count += 1

        if match_count:
            self.status_var.set(f"Highlighted {match_count} linked segment(s).")
        else:
            self.status_var.set("No nearby matches found - try different keywords or check spelling.")


# ---------------------------------------------------------------------------
# Mistake Log: log missed practice questions; reviewed as flashcards on Home
# ---------------------------------------------------------------------------

class MistakeLogPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        top_bar = tk.Frame(self, bg=COLORS["bg"])
        top_bar.pack(fill="x")
        ttk.Button(top_bar, text="< MENU", command=lambda: controller.show_page("menu")).pack(
            side="left", padx=16, pady=12)
        self.header_var = tk.StringVar(value="MISTAKE LOG")
        tk.Label(top_bar, textvariable=self.header_var, font=FONT_HEADER, bg=COLORS["bg"],
                 fg=COLORS["accent4"]).pack(side="left", padx=10)

        body = ttk.Frame(self, padding=(16, 0, 16, 12))
        body.pack(fill="both", expand=True)

        tk.Label(body, text="LOG A MISSED QUESTION", font=FONT_BODY_BOLD, bg=COLORS["bg"],
                 fg=COLORS["fg"]).pack(anchor="w")
        tk.Label(body, text="Add it here right after a practice test. Get it right on review and "
                             "it's gone for good; get it wrong and it comes back tomorrow.",
                 font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["muted"], wraplength=560,
                 justify="left").pack(anchor="w", pady=(2, 12))

        form = ttk.Frame(body)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        tk.Label(form, text="Question / concept:", font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["fg"]).grid(
            row=0, column=0, sticky="nw", pady=(2, 0))
        self.question_text = tk.Text(form, height=3, font=FONT_BODY, wrap="word")
        self.question_text.grid(row=0, column=1, sticky="ew", padx=8, pady=(0, 8))

        tk.Label(form, text="Correct answer:", font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["fg"]).grid(
            row=1, column=0, sticky="nw", pady=(2, 0))
        self.answer_text = tk.Text(form, height=3, font=FONT_BODY, wrap="word")
        self.answer_text.grid(row=1, column=1, sticky="ew", padx=8)

        ttk.Button(body, text="Add mistake", command=self.add_mistake_clicked).pack(anchor="w", pady=(10, 20))

        tk.Label(body, text="ALL LOGGED MISTAKES", font=FONT_BODY_BOLD, bg=COLORS["bg"],
                 fg=COLORS["fg"]).pack(anchor="w")

        columns = ("question", "answer", "due_date")
        self.tree = ttk.Treeview(body, columns=columns, show="headings", height=10)
        self.tree.heading("question", text="Question")
        self.tree.heading("answer", text="Answer")
        self.tree.heading("due_date", text="Next due")
        self.tree.column("question", width=220)
        self.tree.column("answer", width=220)
        self.tree.column("due_date", width=100)
        self.tree.pack(fill="both", expand=True, pady=(6, 6))

        ttk.Button(body, text="Delete selected", command=self.delete_selected).pack(anchor="w")

    def add_mistake_clicked(self):
        question = self.question_text.get("1.0", "end-1c").strip()
        answer = self.answer_text.get("1.0", "end-1c").strip()
        if not question or not answer:
            messagebox.showwarning("Missing info", "Enter both the question and the correct answer.")
            return
        add_mistake(self.controller.current_subject, question, answer)
        self.question_text.delete("1.0", "end")
        self.answer_text.delete("1.0", "end")
        self.refresh()
        self.controller.refresh_home()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        mistake_id = int(self.tree.item(selected[0], "tags")[0])
        delete_mistake(mistake_id)
        self.refresh()
        self.controller.refresh_home()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for mistake_id, question, answer, due_date in get_all_mistakes(self.controller.current_subject):
            q_display = question if len(question) <= 60 else question[:57] + "..."
            a_display = answer if len(answer) <= 60 else answer[:57] + "..."
            self.tree.insert("", "end", values=(q_display, a_display, due_date), tags=(str(mistake_id),))

    def on_show(self):
        self.header_var.set(f"MISTAKE LOG \u00b7 {self.controller.current_subject}")
        self.refresh()


# ---------------------------------------------------------------------------
# Pace Tracker: daily study-time goal per subject + all-time totals
# ---------------------------------------------------------------------------

class PaceTrackerPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._current_pct = 0

        top_bar = tk.Frame(self, bg=COLORS["bg"])
        top_bar.pack(fill="x")
        ttk.Button(top_bar, text="< MENU", command=lambda: controller.show_page("menu")).pack(
            side="left", padx=16, pady=12)
        self.header_var = tk.StringVar(value="PACE TRACKER")
        tk.Label(top_bar, textvariable=self.header_var, font=FONT_HEADER, bg=COLORS["bg"],
                 fg=COLORS["accent5"]).pack(side="left", padx=10)

        body = ttk.Frame(self, padding=(16, 8, 16, 12))
        body.pack(fill="both", expand=True)

        tk.Label(body, text="DAILY STUDY GOAL", font=FONT_BODY_BOLD, bg=COLORS["bg"],
                 fg=COLORS["fg"]).pack(anchor="w")
        tk.Label(body, text="Each subject keeps its own goal, so time spent on one won't quietly "
                             "eat into another's.", font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["muted"],
                 wraplength=560, justify="left").pack(anchor="w", pady=(2, 10))

        goal_form = tk.Frame(body, bg=COLORS["bg"])
        goal_form.pack(fill="x")
        tk.Label(goal_form, text="Goal (minutes):", font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["fg"]).pack(side="left")
        self.goal_var = tk.StringVar()
        ttk.Entry(goal_form, textvariable=self.goal_var, width=10, font=FONT_BODY).pack(side="left", padx=8)
        ttk.Button(goal_form, text="Save goal", command=self.save_goal_clicked).pack(side="left")

        self.progress_label_var = tk.StringVar()
        tk.Label(body, textvariable=self.progress_label_var, font=FONT_BODY_BOLD, bg=COLORS["bg"],
                 fg=COLORS["accent5"]).pack(anchor="w", pady=(20, 4))

        self.progress_canvas = tk.Canvas(body, height=24, bg=COLORS["panel"], highlightthickness=1,
                                          highlightbackground=COLORS["border"])
        self.progress_canvas.pack(fill="x", pady=(0, 24))
        self.progress_canvas.bind("<Configure>", lambda e: self._draw_bar())

        tk.Frame(body, bg=COLORS["border"], height=2).pack(fill="x", pady=(0, 20))

        self.total_label_var = tk.StringVar()
        tk.Label(body, textvariable=self.total_label_var, font=("Courier New", 15, "bold"),
                 bg=COLORS["bg"], fg=COLORS["accent5"], wraplength=560, justify="left").pack(anchor="w")

    def save_goal_clicked(self):
        text = self.goal_var.get().strip()
        if not text:
            return
        try:
            minutes = float(text)
            if minutes <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid number", "Enter a positive number of minutes.")
            return
        set_daily_goal(self.controller.current_subject, minutes)
        self.refresh()
        self.controller.refresh_home()

    def refresh(self):
        subject = self.controller.current_subject
        goal = get_daily_goal(subject)
        today_minutes = get_today_minutes(subject)

        if goal:
            self.goal_var.set(str(int(goal)) if goal == int(goal) else str(goal))
            pct = min(today_minutes / goal, 1.0) * 100
            self.progress_label_var.set(f"TODAY: {round(today_minutes)} / {round(goal)} min ({round(pct)}%)")
        else:
            self.goal_var.set("")
            pct = 0
            self.progress_label_var.set(f"TODAY: {round(today_minutes)} min logged (no goal set yet)")

        self._current_pct = pct
        self._draw_bar()

        total_hours = round(get_total_minutes(subject) / 60, 1)
        self.total_label_var.set(f"YOU'VE STUDIED {total_hours} HOURS ON {subject.upper()}!")

    def _draw_bar(self):
        self.progress_canvas.delete("all")
        width = self.progress_canvas.winfo_width()
        if width <= 1:
            return
        fill_width = int(width * (self._current_pct / 100))
        self.progress_canvas.create_rectangle(0, 0, fill_width, 24, fill=COLORS["accent5"], outline="")

    def on_show(self):
        self.header_var.set(f"PACE TRACKER \u00b7 {self.controller.current_subject}")
        self.refresh()


class SubjectBar(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["border"])
        self.controller = controller

        self.tabs_container = tk.Frame(self, bg=COLORS["border"])
        self.tabs_container.pack(side="left", fill="x", expand=True, padx=(6, 0), pady=4)

        tk.Button(
            self, text="+ SUBJECT", font=FONT_BODY_BOLD, command=self.controller.prompt_add_subject,
            bg=COLORS["accent2"], fg=COLORS["bg"], relief="flat", padx=10, cursor="hand2"
        ).pack(side="right", padx=6, pady=4)

        self.render()

    def render(self):
        for widget in self.tabs_container.winfo_children():
            widget.destroy()
        for name in get_subjects():
            self._add_tab(name)

    def _add_tab(self, name):
        is_active = (name == self.controller.current_subject)
        tab_bg = COLORS["accent"] if is_active else COLORS["panel"]
        tab_fg = COLORS["bg"] if is_active else COLORS["fg"]

        tab = tk.Frame(self.tabs_container, bg=tab_bg, relief="ridge", bd=1)
        tab.pack(side="left", padx=(0, 6))

        label = tk.Label(tab, text=name, font=FONT_BODY_BOLD, bg=tab_bg, fg=tab_fg,
                          padx=10, pady=4, cursor="hand2")
        label.pack(side="left")
        label.bind("<Button-1>", lambda e, n=name: self.controller.set_current_subject(n))

        clear_label = tk.Label(tab, text="clear", font=("Courier New", 8), bg=tab_bg,
                                fg=tab_fg, padx=6, cursor="hand2")
        clear_label.pack(side="left", padx=(0, 6))
        clear_label.bind("<Button-1>", lambda e, n=name: self.controller.prompt_clear_subject(n))


# ---------------------------------------------------------------------------
# Main app: subject bar + a simple frame-swapping "router" between pages
# ---------------------------------------------------------------------------

class StudylyticsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Studylytics")
        self.geometry("680x640")
        self.configure(bg=COLORS["bg"])

        # Use the app icon for the window/taskbar if it's sitting next to
        # this script; harmless (just skipped) if it's not there.
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "studylytics_icon.png")
            if os.path.exists(icon_path):
                self._icon_image = tk.PhotoImage(file=icon_path)
                self.iconphoto(True, self._icon_image)
        except tk.TclError:
            pass

        style = ttk.Style()
        style.configure("Bg.TFrame", background=COLORS["bg"])
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["fg"], font=FONT_BODY)
        style.configure("TButton", font=FONT_BODY_BOLD, padding=6)
        style.configure("TNotebook", background=COLORS["bg"])
        style.configure("TNotebook.Tab", font=FONT_BODY_BOLD, padding=(12, 6))
        style.configure("Treeview", rowheight=28, font=FONT_BODY)
        style.configure("Treeview.Heading", font=FONT_BODY_BOLD)

        self.current_subject = get_subjects()[0]
        self.current_page_name = "menu"

        self.subject_bar = SubjectBar(self, self)
        self.subject_bar.pack(side="top", fill="x")

        container = tk.Frame(self, bg=COLORS["bg"])
        container.pack(fill="both", expand=True)

        self.pages = {}
        for name, PageClass in [
            ("menu", MenuPage),
            ("study_timer", StudyTimerPage),
            ("scheduler", SchedulerPage),
            ("notes", NotesPage),
            ("mistake_log", MistakeLogPage),
            ("pace_tracker", PaceTrackerPage),
        ]:
            page = PageClass(container, self)
            self.pages[name] = page
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_page("menu")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        # Make sure any notes typed but not explicitly saved aren't lost.
        self.pages["notes"].save_current()
        self.destroy()

    def show_page(self, name):
        self.current_page_name = name
        page = self.pages[name]
        page.tkraise()
        if hasattr(page, "on_show"):
            page.on_show()

    def refresh_home(self):
        self.pages["menu"].refresh_all()

    def refresh_current_page(self):
        page = self.pages.get(self.current_page_name)
        if page and hasattr(page, "on_show"):
            page.on_show()

    # --- Subject management ---

    def set_current_subject(self, name):
        self.current_subject = name
        self.subject_bar.render()
        self.refresh_current_page()

    def prompt_add_subject(self):
        name = simpledialog.askstring(
            "New subject",
            "Name this subject/tab (e.g. 'Security+'):",
            parent=self,
        )
        if not name:
            return
        name = name.strip()
        if not name:
            return

        add_subject(name)

        goal_text = simpledialog.askstring(
            "Daily study goal",
            f"Daily study goal for '{name}', in hours (e.g. 1.5)?\nLeave blank to skip - you can set one "
            f"later in Pace Tracker.",
            parent=self,
        )
        if goal_text and goal_text.strip():
            try:
                hours = float(goal_text.strip())
                if hours > 0:
                    set_daily_goal(name, hours * 60)
            except ValueError:
                messagebox.showwarning(
                    "Invalid number",
                    "Couldn't read that as a number - no goal was set. You can set one later in Pace Tracker."
                )

        self.subject_bar.render()
        self.set_current_subject(name)

    def prompt_clear_subject(self, name):
        dialog = tk.Toplevel(self)
        dialog.title(f"Clear '{name}'")
        dialog.configure(bg=COLORS["bg"])
        dialog.resizable(False, False)

        tk.Label(dialog, text=f"Clear all data for '{name}'?", font=FONT_BODY_BOLD,
                 bg=COLORS["bg"], fg=COLORS["fg"]).pack(padx=20, pady=(20, 4))
        tk.Label(dialog, text="This removes its logged sessions, goals, and scheduled reviews.",
                 font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["muted"], wraplength=320,
                 justify="left").pack(padx=20)

        delete_tab_var = tk.BooleanVar(value=False)
        tk.Checkbutton(dialog, text="Also delete this tab", variable=delete_tab_var, font=FONT_BODY,
                       bg=COLORS["bg"], fg=COLORS["fg"], selectcolor=COLORS["panel"],
                       activebackground=COLORS["bg"]).pack(padx=20, pady=(10, 4), anchor="w")

        btn_row = tk.Frame(dialog, bg=COLORS["bg"])
        btn_row.pack(pady=16)

        def on_cancel():
            dialog.destroy()

        def on_clear():
            dialog.destroy()
            self._confirm_and_clear_subject(name, delete_tab_var.get())

        ttk.Button(btn_row, text="Cancel", command=on_cancel).pack(side="left", padx=6)
        ttk.Button(btn_row, text="Clear", command=on_clear).pack(side="left", padx=6)

        # Size and center the window based on its actual content BEFORE
        # grabbing focus - grabbing too early can leave a tiny, blank-looking
        # window on some platforms because layout hasn't been computed yet.
        dialog.update_idletasks()
        width = dialog.winfo_reqwidth()
        height = dialog.winfo_reqheight()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (width // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        dialog.transient(self)
        dialog.wait_visibility()
        dialog.grab_set()

    def _confirm_and_clear_subject(self, name, also_delete_tab):
        if also_delete_tab and len(get_subjects()) <= 1:
            messagebox.showwarning(
                "Can't delete",
                "You need at least one subject tab. Clear its data instead, or add another subject first."
            )
            also_delete_tab = False

        warning = f"This permanently deletes all sessions, goals, and scheduled reviews for '{name}'"
        if also_delete_tab:
            warning += ", and removes its tab"
        warning += ". This cannot be undone."

        if not messagebox.askyesno("Are you sure?", warning, icon="warning"):
            return

        clear_subject_data(name)
        if also_delete_tab:
            delete_subject(name)
            if self.current_subject == name:
                self.current_subject = get_subjects()[0]

        self.subject_bar.render()
        self.refresh_current_page()
        self.refresh_home()


if __name__ == "__main__":
    init_db()
    app = StudylyticsApp()
    app.mainloop()