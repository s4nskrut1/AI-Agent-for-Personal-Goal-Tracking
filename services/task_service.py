"""
Task Service for GoalMate.
Manages tasks, status updates, completion telemetry, and rescheduling with user isolation.
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.models import Task, Goal, ProgressLog
from backend.schemas import TaskCreate, TaskUpdate


def create_task(goal_id: int, user_id: int, data: TaskCreate, db: Session) -> Optional[Task]:
    """Creates a task under a user-owned goal."""
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    if not goal:
        return None
    task = Task(
        goal_id=goal_id,
        milestone_id=data.milestone_id,
        title=data.title.strip(),
        description=(data.description or "").strip(),
        due_date=data.due_date,
        estimated_minutes=data.estimated_minutes,
        priority=data.priority,
        status="pending"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_tasks(
    user_id: int,
    goal_id: Optional[int] = None,
    status: Optional[str] = None,
    due_date: Optional[str] = None,
    db: Session = None
) -> List[Task]:
    """Retrieves tasks owned by user_id with optional filters."""
    query = db.query(Task).join(Goal).filter(Goal.user_id == user_id)
    if goal_id:
        query = query.filter(Task.goal_id == goal_id)
    if status:
        query = query.filter(Task.status == status)
    if due_date:
        query = query.filter(Task.due_date == due_date)
    return query.order_by(Task.due_date.asc(), Task.priority.desc()).all()


def get_today_tasks(user_id: int, goal_id: Optional[int] = None, db: Session = None) -> List[Task]:
    """Retrieves tasks scheduled for today, or pending/overdue from earlier."""
    today_str = date.today().isoformat()
    query = db.query(Task).join(Goal).filter(Goal.user_id == user_id)
    if goal_id:
        query = query.filter(Task.goal_id == goal_id)
    # Include today's tasks OR pending tasks due on or before today
    query = query.filter(
        (Task.due_date == today_str) |
        ((Task.status.in_(["pending", "rescheduled"])) & (Task.due_date <= today_str))
    )
    return query.order_by(Task.status.asc(), Task.due_date.asc(), Task.priority.desc()).all()


def get_pending_tasks(user_id: int, goal_id: Optional[int] = None, db: Session = None) -> List[Task]:
    """Retrieves all pending or rescheduled tasks for user."""
    query = db.query(Task).join(Goal).filter(
        Goal.user_id == user_id,
        Task.status.in_(["pending", "rescheduled"])
    )
    if goal_id:
        query = query.filter(Task.goal_id == goal_id)
    return query.order_by(Task.due_date.asc()).all()


def get_overdue_tasks(user_id: int, goal_id: Optional[int] = None, db: Session = None) -> List[Task]:
    """Retrieves tasks whose due_date is strictly before today and still pending."""
    today_str = date.today().isoformat()
    query = db.query(Task).join(Goal).filter(
        Goal.user_id == user_id,
        Task.status.in_(["pending", "rescheduled"]),
        Task.due_date < today_str
    )
    if goal_id:
        query = query.filter(Task.goal_id == goal_id)
    return query.order_by(Task.due_date.asc()).all()


def complete_task(task_id: int, user_id: int, db: Session) -> Optional[Task]:
    """Marks task completed, updates completion timestamp, and increments progress telemetry."""
    task = db.query(Task).join(Goal).filter(Task.id == task_id, Goal.user_id == user_id).first()
    if not task:
        return None

    now_dt = datetime.now()
    today_str = now_dt.date().isoformat()
    task.status = "completed"
    task.completed_at = now_dt

    # Update or insert into progress_logs
    log = db.query(ProgressLog).filter(
        ProgressLog.user_id == user_id,
        ProgressLog.goal_id == task.goal_id,
        ProgressLog.date == today_str
    ).first()

    est_m = task.estimated_minutes or 45
    if log:
        log.tasks_completed += 1
        log.total_minutes_spent += est_m
    else:
        # Calculate streak
        yesterday_str = (now_dt.date() - timedelta(days=1)).isoformat()
        yesterday_log = db.query(ProgressLog).filter(
            ProgressLog.user_id == user_id,
            ProgressLog.goal_id == task.goal_id,
            ProgressLog.date == yesterday_str
        ).first()
        new_streak = (yesterday_log.streak_count + 1) if yesterday_log else 1

        new_log = ProgressLog(
            user_id=user_id,
            goal_id=task.goal_id,
            date=today_str,
            tasks_completed=1,
            total_minutes_spent=est_m,
            streak_count=new_streak,
            notes="Task completed via GoalMate"
        )
        db.add(new_log)

    db.commit()
    db.refresh(task)
    return task


def uncomplete_task(task_id: int, user_id: int, db: Session) -> Optional[Task]:
    """Reverts a completed task to pending status."""
    task = db.query(Task).join(Goal).filter(Task.id == task_id, Goal.user_id == user_id).first()
    if not task:
        return None
    task.status = "pending"
    task.completed_at = None
    db.commit()
    db.refresh(task)
    return task


def reschedule_task(task_id: int, user_id: int, new_due_date: str, db: Session) -> Optional[Task]:
    """Reschedules a single task to a new date and marks status 'rescheduled'."""
    task = db.query(Task).join(Goal).filter(Task.id == task_id, Goal.user_id == user_id).first()
    if not task:
        return None
    task.due_date = new_due_date
    task.status = "rescheduled"
    db.commit()
    db.refresh(task)
    return task
