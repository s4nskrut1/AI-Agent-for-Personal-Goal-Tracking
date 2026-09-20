"""
GoalMate — Goal and Task Service Layer.
All business logic for creating, updating, analyzing goals/tasks.
"""
import os
import json
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from backend.models import Goal, Milestone, Task, ActivityLog, SessionLocal

logger = logging.getLogger("goalmate-services")


def get_session() -> Session:
    return SessionLocal()


# ─────────────────────────── GOAL OPERATIONS ────────────────────────────────

def get_all_goals(db: Session = None) -> List[Goal]:
    close = db is None
    if db is None:
        db = get_session()
    try:
        return (db.query(Goal)
                .options(joinedload(Goal.milestones).joinedload(Milestone.tasks),
                         joinedload(Goal.tasks))
                .filter(Goal.status != "deleted")
                .order_by(Goal.created_at.desc())
                .all())
    finally:
        if close:
            db.close()


def get_goal(goal_id: int, db: Session = None) -> Optional[Goal]:
    close = db is None
    if db is None:
        db = get_session()
    try:
        return (db.query(Goal)
                .options(joinedload(Goal.milestones).joinedload(Milestone.tasks),
                         joinedload(Goal.tasks))
                .filter(Goal.id == goal_id)
                .first())

    finally:
        if close:
            db.close()


def create_goal_record(
    title: str,
    description: str = "",
    category: str = "General",
    duration_days: int = 30,
    start_date: date = None,
    db: Session = None
) -> Goal:
    close = db is None
    if db is None:
        db = get_session()
    try:
        if start_date is None:
            start_date = datetime.now().date()
        deadline = start_date + timedelta(days=duration_days)
        goal = Goal(
            title=title,
            description=description,
            category=category,
            duration_days=duration_days,
            start_date=start_date,
            deadline=deadline,
            status="active"
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        log_activity(db, goal.id, "goal_created", f"Goal created: {title}", "🎯")
        return goal
    finally:
        if close:
            db.close()


def update_goal(goal_id: int, updates: Dict[str, Any], db: Session = None) -> Optional[Goal]:
    close = db is None
    if db is None:
        db = get_session()
    try:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return None
        for k, v in updates.items():
            if hasattr(goal, k):
                setattr(goal, k, v)
        goal.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(goal)
        return goal
    finally:
        if close:
            db.close()


def delete_goal(goal_id: int, db: Session = None) -> bool:
    close = db is None
    if db is None:
        db = get_session()
    try:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return False
        db.delete(goal)
        db.commit()
        return True
    finally:
        if close:
            db.close()


# ─────────────────────────── MILESTONE OPERATIONS ───────────────────────────

def create_milestone(goal_id: int, title: str, description: str = "", order_index: int = 0, db: Session = None) -> Milestone:
    close = db is None
    if db is None:
        db = get_session()
    try:
        m = Milestone(goal_id=goal_id, title=title, description=description, order_index=order_index)
        db.add(m)
        db.commit()
        db.refresh(m)
        return m
    finally:
        if close:
            db.close()


def get_milestones(goal_id: int, db: Session = None) -> List[Milestone]:
    close = db is None
    if db is None:
        db = get_session()
    try:
        return db.query(Milestone).filter(Milestone.goal_id == goal_id).order_by(Milestone.order_index).all()
    finally:
        if close:
            db.close()


# ─────────────────────────── TASK OPERATIONS ────────────────────────────────

def create_task(
    goal_id: int,
    title: str,
    scheduled_date: date = None,
    milestone_id: int = None,
    estimated_duration: str = "30 min",
    description: str = "",
    db: Session = None
) -> Task:
    close = db is None
    if db is None:
        db = get_session()
    try:
        task = Task(
            goal_id=goal_id,
            milestone_id=milestone_id,
            title=title,
            description=description,
            scheduled_date=scheduled_date,
            estimated_duration=estimated_duration,
            status="pending"
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    finally:
        if close:
            db.close()


def complete_task(task_id: int, completed: bool = True, db: Session = None) -> Optional[Task]:
    close = db is None
    if db is None:
        db = get_session()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        task.status = "completed" if completed else "pending"
        task.completed_at = datetime.now() if completed else None
        task.updated_at = datetime.now()
        db.commit()
        db.refresh(task)
        action = "completed" if completed else "uncompleted"
        log_activity(db, task.goal_id, "task_completed" if completed else "task_updated",
                     f"Task {action}: {task.title}", "✓" if completed else "↩")
        return task
    finally:
        if close:
            db.close()


def get_tasks_for_goal(goal_id: int, db: Session = None) -> List[Task]:
    close = db is None
    if db is None:
        db = get_session()
    try:
        return db.query(Task).filter(Task.goal_id == goal_id).order_by(Task.scheduled_date).all()
    finally:
        if close:
            db.close()


def get_today_tasks(db: Session = None) -> List[Dict]:
    close = db is None
    if db is None:
        db = get_session()
    try:
        today = datetime.now().date()
        tasks = db.query(Task).filter(Task.scheduled_date == today).order_by(Task.goal_id).all()
        result = []
        for t in tasks:
            goal = db.query(Goal).filter(Goal.id == t.goal_id).first()
            result.append({
                "id": t.id, "title": t.title, "status": t.status,
                "goal_title": goal.title if goal else "Unknown",
                "goal_id": t.goal_id,
                "duration": t.estimated_duration,
                "scheduled_date": str(t.scheduled_date)
            })
        return result
    finally:
        if close:
            db.close()


def get_past_missed_tasks(db: Session = None, limit: int = 15) -> List[Dict]:
    """Return tasks scheduled before today (both pending and completed) for retroactive editing."""
    close = db is None
    if db is None:
        db = get_session()
    try:
        today = datetime.now().date()
        tasks = (db.query(Task)
                 .filter(Task.scheduled_date < today)
                 .order_by(Task.scheduled_date.desc(), Task.id.desc())
                 .limit(limit)
                 .all())
        result = []
        for t in tasks:
            goal = db.query(Goal).filter(Goal.id == t.goal_id).first()
            result.append({
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "goal_title": goal.title if goal else "Unknown",
                "goal_id": t.goal_id,
                "duration": t.estimated_duration or "30 min",
                "scheduled_date": str(t.scheduled_date),
                "is_missed": (t.status == "pending")
            })
        return result
    finally:
        if close:
            db.close()


def get_upcoming_tasks(db: Session = None, limit: int = 15) -> List[Dict]:
    """Return tasks scheduled after today for upcoming schedule."""
    close = db is None
    if db is None:
        db = get_session()
    try:
        today = datetime.now().date()
        tasks = (db.query(Task)
                 .filter(Task.scheduled_date > today)
                 .order_by(Task.scheduled_date.asc(), Task.id.asc())
                 .limit(limit)
                 .all())
        result = []
        for t in tasks:
            goal = db.query(Goal).filter(Goal.id == t.goal_id).first()
            result.append({
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "goal_title": goal.title if goal else "Unknown",
                "goal_id": t.goal_id,
                "duration": t.estimated_duration or "30 min",
                "scheduled_date": str(t.scheduled_date)
            })
        return result
    finally:
        if close:
            db.close()


def get_tasks_by_date(target_date: date, db: Session = None) -> List[Task]:
    close = db is None
    if db is None:
        db = get_session()
    try:
        return db.query(Task).filter(Task.scheduled_date == target_date).all()
    finally:
        if close:
            db.close()


def reschedule_tasks(goal_id: int, new_start: date, db: Session = None) -> int:
    """Reassign task dates for a goal starting from new_start."""
    close = db is None
    if db is None:
        db = get_session()
    try:
        tasks = db.query(Task).filter(
            Task.goal_id == goal_id, Task.status == "pending"
        ).order_by(Task.scheduled_date).all()
        current_date = new_start
        for task in tasks:
            task.scheduled_date = current_date
            current_date += timedelta(days=1)
        db.commit()
        return len(tasks)
    finally:
        if close:
            db.close()

def reschedule_single_task(task_id: int, new_date: date, db: Session = None) -> Optional[Task]:
    """Move a single task to a specific date (today, tomorrow, or custom)."""
    close = db is None
    if db is None:
        db = get_session()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        old_date = task.scheduled_date
        task.scheduled_date = new_date
        task.updated_at = datetime.now()
        db.commit()
        db.refresh(task)
        log_activity(db, task.goal_id, "task_updated",
                     f"Task '{task.title}' moved from {old_date} to {new_date}", "📅")
        return task
    finally:
        if close:
            db.close()


def replan_goal(goal_id: int, new_duration_days: int, db: Session = None) -> Optional[Goal]:
    """Update goal duration and deadline, then reschedule pending tasks."""
    close = db is None
    if db is None:
        db = get_session()
    try:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return None
        goal.duration_days = new_duration_days
        goal.deadline = goal.start_date + timedelta(days=new_duration_days)
        goal.updated_at = datetime.now()
        db.commit()

        # Reschedule pending tasks from today
        today = datetime.now().date()
        pending = db.query(Task).filter(
            Task.goal_id == goal_id, Task.status == "pending"
        ).order_by(Task.scheduled_date).all()
        tasks_per_day = max(1, len(pending) // max(1, (goal.deadline - today).days)) if (goal.deadline - today).days > 0 else 1
        current_date = today
        for i, task in enumerate(pending):
            task.scheduled_date = current_date
            if (i + 1) % tasks_per_day == 0:
                current_date += timedelta(days=1)
        db.commit()
        log_activity(db, goal_id, "goal_updated", f"Goal replanned to {new_duration_days} days", "🔄")
        db.refresh(goal)
        return goal
    finally:
        if close:
            db.close()


# ─────────────────────────── ANALYTICS ──────────────────────────────────────

def get_weekly_data(goal_id: Any = None, db: Session = None) -> List[Dict]:
    if hasattr(goal_id, "query") and db is None:
        db = goal_id
        goal_id = None
    close = db is None
    if db is None:
        db = get_session()
    try:
        today = datetime.now().date()
        start_date = None
        if goal_id:
            g = db.query(Goal).filter(Goal.id == goal_id).first()
            if g and g.start_date:
                start_date = g.start_date
        else:
            primary_goal = db.query(Goal).filter(Goal.status == "active").first()
            if primary_goal and primary_goal.start_date:
                start_date = primary_goal.start_date

        # If goal was created recently (within last 6 days), start from goal creation date!
        # Otherwise start from today (7-day span from today to next week)
        if start_date and start_date <= today and (today - start_date).days <= 6:
            base_date = start_date
        else:
            base_date = today

        result = []
        for i in range(7):
            d = base_date + timedelta(days=i)
            query = db.query(Task).filter(Task.scheduled_date == d)
            if goal_id:
                query = query.filter(Task.goal_id == goal_id)
            tasks = query.all()
            total = len(tasks)
            done = sum(1 for t in tasks if t.status == "completed")
            pct = round((done / total * 100)) if total > 0 else 0
            result.append({
                "day": d.strftime("%a"),
                "date": str(d),
                "total": total,
                "completed": done,
                "pct": pct,
                "is_today": (d == today),
                "is_start": (start_date and d == start_date)
            })
        return result
    finally:
        if close:
            db.close()


def get_goal_daily_progress(goal_id: int, db: Session = None) -> List[Dict]:
    """Calculate day-by-day task completion percentage for a specific goal starting from its start date."""
    return get_weekly_data(goal_id=goal_id, db=db)


def get_visual_velocity_analytics(db: Session = None) -> Dict:
    """Compute visual graph data: 7-day completion curve, velocity, and goal distribution."""
    close = db is None
    if db is None:
        db = get_session()
    try:
        today = datetime.now().date()
        days_points = []
        cumulative = 0
        total_week_done = 0

        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            tasks = db.query(Task).filter(Task.scheduled_date == d).all()
            done = sum(1 for t in tasks if t.status == "completed")
            cumulative += done
            total_week_done += done
            days_points.append({
                "day": d.strftime("%a"),
                "date": str(d),
                "count": done,
                "cumulative": cumulative
            })

        goals = db.query(Goal).filter(Goal.status != "deleted").all()
        goal_breakdown = []
        for g in goals:
            goal_breakdown.append({
                "id": g.id,
                "title": g.title,
                "progress_pct": g.progress_pct,
                "done": g.completed_tasks,
                "total": g.total_tasks
            })

        velocity = round(total_week_done / 7.0, 1)
        consistency = round((sum(1 for p in days_points if p["count"] > 0) / 7.0) * 100)

        return {
            "points": days_points,
            "velocity": velocity,
            "total_week_done": total_week_done,
            "consistency_rate": consistency,
            "goal_breakdown": goal_breakdown
        }
    finally:
        if close:
            db.close()


def get_goal_pace_trajectory(goal_id: int, db: Session = None) -> Dict:
    """Calculate planned linear pace vs actual task completion curve for a goal."""
    close = db is None
    if db is None:
        db = get_session()
    try:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return {"planned": [], "actual": []}
        
        tasks = db.query(Task).filter(Task.goal_id == goal_id).order_by(Task.scheduled_date).all()
        total_tasks = len(tasks)
        if total_tasks == 0:
            return {"planned": [], "actual": []}

        # Build trajectory milestones (5 steps)
        steps = 5
        planned = [round((i / steps) * total_tasks) for i in range(steps + 1)]
        
        # Count actual completed so far
        actual_done = sum(1 for t in tasks if t.status == "completed")
        actual = [0, min(actual_done, round(total_tasks * 0.2)), 
                  min(actual_done, round(total_tasks * 0.5)),
                  min(actual_done, round(total_tasks * 0.8)), actual_done]

        return {
            "labels": ["Start", "25%", "50%", "75%", "Target"],
            "planned": planned,
            "actual": actual,
            "total_tasks": total_tasks,
            "completed_tasks": actual_done
        }
    finally:
        if close:
            db.close()


def get_streak(db: Session = None) -> int:
    close = db is None
    if db is None:
        db = get_session()
    try:
        today = datetime.now().date()
        streak = 0
        for i in range(365):
            d = today - timedelta(days=i)
            tasks = db.query(Task).filter(Task.scheduled_date == d).all()
            if not tasks:
                continue
            completed = all(t.status == "completed" for t in tasks)
            if completed:
                streak += 1
            else:
                break
        return streak
    finally:
        if close:
            db.close()


def get_recent_activity(limit: int = 8, db: Session = None) -> List[Dict]:
    close = db is None
    if db is None:
        db = get_session()
    try:
        logs = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit).all()
        result = []
        for log in logs:
            delta = datetime.now() - log.created_at
            if delta.seconds < 3600:
                time_str = f"Today, {log.created_at.strftime('%I:%M %p')}"
            elif delta.days == 1:
                time_str = f"Yesterday, {log.created_at.strftime('%I:%M %p')}"
            else:
                time_str = log.created_at.strftime("%b %d, %I:%M %p")
            result.append({
                "icon": log.icon,
                "description": log.description,
                "time": time_str,
                "event_type": log.event_type
            })
        return result
    finally:
        if close:
            db.close()


def get_dashboard_stats(db: Session = None) -> Dict:
    close = db is None
    if db is None:
        db = get_session()
    try:
        goals = db.query(Goal).filter(Goal.status == "active").all()
        today = datetime.now().date()
        today_tasks = db.query(Task).filter(Task.scheduled_date == today).all()
        return {
            "total_goals": len(goals),
            "active_tasks": sum(1 for t in today_tasks if t.status == "pending"),
            "completed_today": sum(1 for t in today_tasks if t.status == "completed"),
            "streak": get_streak(db)
        }
    finally:
        if close:
            db.close()


# ─────────────────────────── ACTIVITY LOG ───────────────────────────────────

def log_activity(db: Session, goal_id: Optional[int], event_type: str, description: str, icon: str = "✓"):
    try:
        log = ActivityLog(goal_id=goal_id, event_type=event_type, description=description, icon=icon)
        db.add(log)
        db.commit()
    except Exception as e:
        logger.warning(f"Activity log error: {e}")


def get_one_month_activity(db: Session = None) -> List[Dict]:
    """Generates clean 28-35 days of daily task activity data for the compact 1-month heatmap."""
    close = db is None
    if db is None:
        db = get_session()
    try:
        today = datetime.now().date()
        # Exactly 4-5 weeks aligned to start on Monday
        start_day = today - timedelta(days=27)
        weekday_idx = start_day.weekday()
        aligned_start = start_day - timedelta(days=weekday_idx)

        days_data = []
        curr = aligned_start
        while curr <= today:
            tasks = db.query(Task).filter(Task.scheduled_date == curr).all()
            total = len(tasks)
            done = sum(1 for t in tasks if t.status == "completed")

            if done == 0:
                level = 0
            elif done == 1:
                level = 1
            elif done in (2, 3):
                level = 2
            else:
                level = 3

            days_data.append({
                "date": str(curr),
                "day_name": curr.strftime("%a"),
                "day_num": curr.day,
                "month_name": curr.strftime("%b"),
                "total": total,
                "completed": done,
                "level": level,
                "is_today": (curr == today)
            })
            curr += timedelta(days=1)

        return days_data
    finally:
        if close:
            db.close()


def get_system_progress_overview(db: Session = None) -> Dict:
    """Calculates clean, balanced metrics for the dedicated Progress & Analytics view."""
    close = db is None
    if db is None:
        db = get_session()
    try:
        goals = db.query(Goal).filter(Goal.status != "deleted").all()
        tasks = db.query(Task).all()
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == "completed")
        pending_tasks = total_tasks - completed_tasks
        overall_pct = round((completed_tasks / max(1, total_tasks)) * 100)
        streak = get_streak(db)

        goal_metrics = []
        for g in goals:
            goal_metrics.append({
                "id": g.id,
                "title": g.title,
                "category": g.category or "Learning",
                "progress_pct": g.progress_pct,
                "completed_tasks": g.completed_tasks,
                "total_tasks": g.total_tasks,
                "days_remaining": g.days_remaining
            })

        heatmap = get_one_month_activity(db)
        velocity_stats = get_visual_velocity_analytics(db)

        return {
            "total_goals": len(goals),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "overall_pct": overall_pct,
            "streak": streak,
            "goals": goal_metrics,
            "heatmap": heatmap,
            "velocity": velocity_stats.get("velocity", 0.0),
            "consistency_rate": velocity_stats.get("consistency_rate", 0),
            "total_week_done": velocity_stats.get("total_week_done", 0)
        }
    finally:
        if close:
            db.close()
