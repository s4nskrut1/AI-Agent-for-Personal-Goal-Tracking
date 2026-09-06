"""
Goal Management Tools for GoalMate.
Provides deterministic functions to query, create, update, and delete goals and milestones.
"""
import datetime
from typing import Optional, List, Dict, Any
from database.db import get_db_connection


def create_goal(
    title: str,
    description: str = "",
    category: str = "General",
    target_date: Optional[str] = None,
    priority: str = "Medium",
    daily_time_minutes: int = 60,
    preferred_schedule: str = "flexible",
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates a new goal record in the database.
    Returns the created goal dict.
    """
    now_str = datetime.datetime.now().isoformat()
    if not target_date:
        # Default target date: 60 days out
        target_date = (datetime.date.today() + datetime.timedelta(days=60)).isoformat()
        
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO goals (
                title, description, category, target_date, priority,
                daily_time_minutes, preferred_schedule, status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
            """,
            (
                title.strip(),
                description.strip(),
                category.strip(),
                target_date,
                priority,
                daily_time_minutes,
                preferred_schedule,
                now_str,
                now_str
            )
        )
        goal_id = cursor.lastrowid
        conn.commit()
        
    return get_goal(goal_id, db_path=db_path)


def get_goals(status: Optional[str] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all goals, optionally filtered by status ('active', 'completed', etc.)."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute("SELECT * FROM goals WHERE status = ? ORDER BY id DESC", (status,))
        else:
            cursor.execute("SELECT * FROM goals ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]


def get_goal(goal_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves a single goal by its ID."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_goal(goal_id: int, db_path: Optional[str] = None, **fields) -> Optional[Dict[str, Any]]:
    """Updates specific fields of a goal (e.g. title, daily_time_minutes, status)."""
    valid_keys = {
        "title", "description", "category", "target_date", "priority",
        "daily_time_minutes", "preferred_schedule", "status"
    }
    updates = {k: v for k, v in fields.items() if k in valid_keys and v is not None}
    if not updates:
        return get_goal(goal_id, db_path=db_path)
        
    updates["updated_at"] = datetime.datetime.now().isoformat()
    set_clauses = [f"{k} = ?" for k in updates.keys()]
    values = list(updates.values()) + [goal_id]
    
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        query = f"UPDATE goals SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        
    return get_goal(goal_id, db_path=db_path)


def delete_goal(goal_id: int, db_path: Optional[str] = None) -> bool:
    """Deletes a goal and cascades to its milestones and tasks."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        conn.commit()
        return cursor.rowcount > 0


def create_milestone(
    goal_id: int,
    title: str,
    description: str = "",
    order_index: int = 1,
    target_date: Optional[str] = None,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Creates a milestone for a given goal."""
    now_str = datetime.datetime.now().isoformat()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO milestones (goal_id, title, description, order_index, target_date, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
            """,
            (goal_id, title.strip(), description.strip(), order_index, target_date, now_str)
        )
        milestone_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM milestones WHERE id = ?", (milestone_id,))
        return dict(cursor.fetchone())


def get_milestones(goal_id: int, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all milestones for a goal ordered by their sequence index."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM milestones WHERE goal_id = ? ORDER BY order_index ASC", (goal_id,))
        return [dict(row) for row in cursor.fetchall()]
