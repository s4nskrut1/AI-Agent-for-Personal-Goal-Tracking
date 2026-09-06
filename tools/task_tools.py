"""
Task Management Tools for GoalMate.
Handles creation, status updates, completion tracking, and rescheduling of tasks.
"""
import datetime
from typing import Optional, List, Dict, Any
from database.db import get_db_connection


def create_task(
    goal_id: int,
    title: str,
    milestone_id: Optional[int] = None,
    description: str = "",
    due_date: Optional[str] = None,
    estimated_minutes: int = 45,
    priority: str = "Medium",
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Creates a new task in the database."""
    now_str = datetime.datetime.now().isoformat()
    if not due_date:
        due_date = datetime.date.today().isoformat()
        
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (
                goal_id, milestone_id, title, description, due_date,
                estimated_minutes, priority, status, completed_at, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', NULL, ?, ?)
            """,
            (
                goal_id,
                milestone_id,
                title.strip(),
                description.strip(),
                due_date,
                estimated_minutes,
                priority,
                now_str,
                now_str
            )
        )
        task_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return dict(cursor.fetchone())


def get_tasks(
    goal_id: Optional[int] = None,
    status: Optional[str] = None,
    date: Optional[str] = None,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieves tasks based on optional filters (goal_id, status, due date)."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM tasks WHERE 1=1"
        params: List[Any] = []
        
        if goal_id:
            query += " AND goal_id = ?"
            params.append(goal_id)
        if status:
            query += " AND status = ?"
            params.append(status)
        if date:
            query += " AND due_date = ?"
            params.append(date)
            
        query += " ORDER BY due_date ASC, priority DESC, id ASC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_pending_tasks(goal_id: Optional[int] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all tasks that are currently pending or rescheduled."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        if goal_id:
            cursor.execute(
                "SELECT * FROM tasks WHERE goal_id = ? AND status IN ('pending', 'rescheduled') ORDER BY due_date ASC",
                (goal_id,)
            )
        else:
            cursor.execute(
                "SELECT * FROM tasks WHERE status IN ('pending', 'rescheduled') ORDER BY due_date ASC"
            )
        return [dict(row) for row in cursor.fetchall()]


def get_overdue_tasks(
    goal_id: Optional[int] = None,
    as_of_date: Optional[str] = None,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves tasks that are pending but whose due_date is strictly before as_of_date (defaults to today).
    """
    check_date = as_of_date or datetime.date.today().isoformat()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        if goal_id:
            cursor.execute(
                """
                SELECT * FROM tasks 
                WHERE goal_id = ? AND status IN ('pending', 'rescheduled') AND due_date < ?
                ORDER BY due_date ASC
                """,
                (goal_id, check_date)
            )
        else:
            cursor.execute(
                """
                SELECT * FROM tasks 
                WHERE status IN ('pending', 'rescheduled') AND due_date < ?
                ORDER BY due_date ASC
                """,
                (check_date,)
            )
        return [dict(row) for row in cursor.fetchall()]


def complete_task(task_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Marks a task as completed, sets completed_at timestamp, and logs progress.
    """
    now = datetime.datetime.now()
    now_str = now.isoformat()
    today_str = now.date().isoformat()
    
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task_row = cursor.fetchone()
        if not task_row:
            return None
            
        task = dict(task_row)
        goal_id = task["goal_id"]
        est_mins = task.get("estimated_minutes", 45) or 45
        
        # Update task
        cursor.execute(
            """
            UPDATE tasks 
            SET status = 'completed', completed_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (now_str, now_str, task_id)
        )
        
        # Update / Insert into progress_logs
        cursor.execute(
            "SELECT * FROM progress_logs WHERE goal_id = ? AND date = ?",
            (goal_id, today_str)
        )
        existing_log = cursor.fetchone()
        if existing_log:
            cursor.execute(
                """
                UPDATE progress_logs 
                SET tasks_completed = tasks_completed + 1,
                    total_minutes_spent = total_minutes_spent + ?
                WHERE id = ?
                """,
                (est_mins, existing_log["id"])
            )
        else:
            # Calculate streak
            cursor.execute(
                """
                SELECT streak_count FROM progress_logs 
                WHERE goal_id = ? AND date = ?
                """,
                (goal_id, (now.date() - datetime.timedelta(days=1)).isoformat())
            )
            yesterday_log = cursor.fetchone()
            new_streak = (yesterday_log["streak_count"] + 1) if yesterday_log else 1
            
            cursor.execute(
                """
                INSERT INTO progress_logs (goal_id, date, tasks_completed, total_minutes_spent, streak_count, notes, created_at)
                VALUES (?, ?, 1, ?, ?, 'Task completed', ?)
                """,
                (goal_id, today_str, est_mins, new_streak, now_str)
            )
            
        conn.commit()
        
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return dict(cursor.fetchone())


def update_task(task_id: int, db_path: Optional[str] = None, **fields) -> Optional[Dict[str, Any]]:
    """Updates fields of a specific task."""
    valid_keys = {"title", "description", "due_date", "estimated_minutes", "priority", "status"}
    updates = {k: v for k, v in fields.items() if k in valid_keys and v is not None}
    if not updates:
        with get_db_connection(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cur.fetchone()
            return dict(row) if row else None
            
    updates["updated_at"] = datetime.datetime.now().isoformat()
    set_clauses = [f"{k} = ?" for k in updates.keys()]
    values = list(updates.values()) + [task_id]
    
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = ?", values)
        conn.commit()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def reschedule_task(task_id: int, new_due_date: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Reschedules a single task to a new due date and sets status to 'rescheduled'."""
    now_str = datetime.datetime.now().isoformat()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE tasks 
            SET due_date = ?, status = 'rescheduled', updated_at = ?
            WHERE id = ?
            """,
            (new_due_date, now_str, task_id)
        )
        conn.commit()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def batch_reschedule_tasks(
    task_ids: List[int],
    shift_days: int,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Shifts multiple tasks forward by a specific number of days.
    """
    updated_tasks = []
    now_str = datetime.datetime.now().isoformat()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        for t_id in task_ids:
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (t_id,))
            t = cursor.fetchone()
            if t:
                try:
                    curr_date = datetime.date.fromisoformat(t["due_date"])
                    new_date = (curr_date + datetime.timedelta(days=shift_days)).isoformat()
                except Exception:
                    new_date = (datetime.date.today() + datetime.timedelta(days=shift_days)).isoformat()
                    
                cursor.execute(
                    """
                    UPDATE tasks 
                    SET due_date = ?, status = 'rescheduled', updated_at = ?
                    WHERE id = ?
                    """,
                    (new_date, now_str, t_id)
                )
                updated_tasks.append({
                    "id": t_id,
                    "title": t["title"],
                    "old_date": t["due_date"],
                    "new_date": new_date
                })
        conn.commit()
    return updated_tasks
