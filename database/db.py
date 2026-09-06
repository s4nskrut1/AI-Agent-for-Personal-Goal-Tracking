"""
Database Connection Manager and Helper Methods for GoalMate.
Provides robust connection handling, schema initialization, and demo seeding.
"""
import sqlite3
import datetime
from pathlib import Path
from typing import Optional

from config import DB_PATH
from database.schema import SCHEMA_SQL


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Returns a SQLite connection with Row factory and foreign keys enabled."""
    target_path = db_path or DB_PATH
    Path(target_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(target_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initializes tables and indexes defined in SCHEMA_SQL."""
    with get_db_connection(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()


def reset_db(db_path: Optional[str] = None) -> None:
    """Drops all tables and re-initializes schema for fresh runs."""
    target_path = db_path or DB_PATH
    with get_db_connection(target_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF;")
        tables = ["tasks", "milestones", "progress_logs", "goals", "user_memories", "conversations"]
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
        cursor.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
    init_db(target_path)


def seed_demo_data(db_path: Optional[str] = None) -> int:
    """
    Seeds a sample goal with milestones and tasks.
    Useful for quick testing or initial dashboard view.
    """
    init_db(db_path)
    today = datetime.date.today()
    now_str = datetime.datetime.now().isoformat()
    
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Check if already seeded
        cursor.execute("SELECT COUNT(*) as count FROM goals;")
        if cursor.fetchone()["count"] > 0:
            cursor.execute("SELECT id FROM goals ORDER BY id ASC LIMIT 1;")
            return cursor.fetchone()["id"]
        
        # Insert Goal
        target_date = (today + datetime.timedelta(days=60)).isoformat()
        cursor.execute(
            """
            INSERT INTO goals (title, description, category, target_date, priority, daily_time_minutes, preferred_schedule, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "Learn Python & Agentic AI",
                "Master Python fundamentals, OOP, APIs, and build agentic AI systems.",
                "Education",
                target_date,
                "High",
                60,
                "evening",
                "active",
                now_str,
                now_str
            )
        )
        goal_id = cursor.lastrowid
        
        # Insert Milestones
        milestones_data = [
            ("Python Core Fundamentals", "Syntax, variables, control flow, functions", 1, (today + datetime.timedelta(days=14)).isoformat()),
            ("Data Structures & Modules", "Lists, dicts, packages, file I/O", 2, (today + datetime.timedelta(days=28)).isoformat()),
            ("OOP & Web APIs", "Classes, inheritance, requests, FastAPI", 3, (today + datetime.timedelta(days=45)).isoformat()),
            ("Agentic AI Project", "Build GoalMate with Gradio and multi-agent workflow", 4, target_date),
        ]
        
        milestone_ids = []
        for title, desc, idx, m_date in milestones_data:
            cursor.execute(
                """
                INSERT INTO milestones (goal_id, title, description, order_index, target_date, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'pending', ?)
                """,
                (goal_id, title, desc, idx, m_date, now_str)
            )
            milestone_ids.append(cursor.lastrowid)
            
        # Insert Sample Tasks: 2 completed in past, 1 due today, 3 due in coming days
        tasks_data = [
            (milestone_ids[0], "Install Python 3.13 and set up virtual environment", (today - datetime.timedelta(days=2)).isoformat(), 45, "High", "completed", (today - datetime.timedelta(days=2)).isoformat()),
            (milestone_ids[0], "Practice Variables, Conditionals, and Loops", (today - datetime.timedelta(days=1)).isoformat(), 60, "High", "completed", (today - datetime.timedelta(days=1)).isoformat()),
            (milestone_ids[0], "Write Functions & Scope exercises in Jupyter", today.isoformat(), 60, "High", "pending", None),
            (milestone_ids[0], "Solve 5 Python practice problems on CodeWars/LeetCode", (today + datetime.timedelta(days=1)).isoformat(), 60, "Medium", "pending", None),
            (milestone_ids[1], "Explore Lists, Dictionaries, and Sets comprehension", (today + datetime.timedelta(days=2)).isoformat(), 60, "Medium", "pending", None),
            (milestone_ids[1], "File I/O and JSON serialization project", (today + datetime.timedelta(days=3)).isoformat(), 60, "High", "pending", None),
        ]
        
        for m_id, title, due_d, est_m, prio, stat, comp_at in tasks_data:
            cursor.execute(
                """
                INSERT INTO tasks (goal_id, milestone_id, title, description, due_date, estimated_minutes, priority, status, completed_at, created_at, updated_at)
                VALUES (?, ?, ?, '', ?, ?, ?, ?, ?, ?, ?)
                """,
                (goal_id, m_id, title, due_d, est_m, prio, stat, comp_at, now_str, now_str)
            )
            
        # Add a sample memory entry
        cursor.execute(
            """
            INSERT OR REPLACE INTO user_memories (key, value, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("preferred_study_time", "Prefers evening sessions around 8 PM", "preference", now_str, now_str)
        )
        
        # Add sample progress log for streak
        cursor.execute(
            """
            INSERT INTO progress_logs (goal_id, date, tasks_completed, total_minutes_spent, streak_count, notes, created_at)
            VALUES (?, ?, 1, 60, 2, 'Great progress on conditionals and loops.', ?)
            """,
            (goal_id, (today - datetime.timedelta(days=1)).isoformat(), now_str)
        )
        
        conn.commit()
        return goal_id
