"""
Adaptive Replanner Engine for GoalMate.
Dynamically recalculates task schedules when user slips or falls behind,
capping tomorrow at <= 45m and distributing backlog smoothly without cramming.
"""
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.models import Task, Goal
from services import task_service, goal_service


class AdaptiveReplanner:
    """Intelligently repairs slipped schedules without cognitive or task overload."""

    @staticmethod
    def replan_goal(
        user_id: int,
        goal_id: int,
        user_reason: str = "Unexpected schedule crunch",
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Executes adaptive rescheduling for a user goal:
        1. Identifies overdue & pending tasks.
        2. Sets tomorrow as a gentle 'Restart Day' (max 1 task, <= 45m).
        3. Smoothly spreads remaining backlog across subsequent days.
        4. Persists new due dates and 'rescheduled' status in SQLite.
        """
        goal = goal_service.get_goal(goal_id, user_id, db)
        if not goal:
            return {"success": False, "error": "Goal not found or unauthorized"}

        today = date.today()
        today_str = today.isoformat()

        # Find all overdue tasks + today's pending tasks
        all_pending = task_service.get_pending_tasks(user_id, goal_id=goal_id, db=db)
        overdue_tasks = [t for t in all_pending if t.due_date < today_str]
        today_tasks = [t for t in all_pending if t.due_date == today_str]
        future_tasks = [t for t in all_pending if t.due_date > today_str]

        backlog = overdue_tasks + today_tasks
        if not backlog:
            # If no overdue tasks, check if user simply wants to ease the future pace
            backlog = future_tasks[:4]
            future_tasks = future_tasks[4:]

        if not backlog:
            return {
                "success": True,
                "message": "All current tasks are up to date! No rescheduling needed.",
                "tasks_rescheduled": 0,
                "schedule": []
            }

        # Calculate estimated slipped days
        earliest_due = min([t.due_date for t in backlog])
        try:
            earliest_date = date.fromisoformat(earliest_due)
            slipped_days = max(1, (today - earliest_date).days)
        except Exception:
            slipped_days = 2

        # Step 1: Design Tomorrow as Gentle Restart Day (Day +1)
        tomorrow = today + timedelta(days=1)
        tomorrow_str = tomorrow.isoformat()

        # Pick the most foundational / first task for tomorrow
        restart_task = backlog[0]
        restart_task.due_date = tomorrow_str
        restart_task.status = "rescheduled"
        # Cap time at 45 minutes for gentle on-ramp
        if restart_task.estimated_minutes and restart_task.estimated_minutes > 45:
            restart_task.estimated_minutes = 45

        rescheduled_summary = [
            {
                "task_id": restart_task.id,
                "title": restart_task.title,
                "new_date": tomorrow_str,
                "day_label": f"Tomorrow ({tomorrow.strftime('%a, %b %d')}) - Gentle Restart",
                "estimated_minutes": restart_task.estimated_minutes
            }
        ]

        # Step 2: Distribute remaining backlog across subsequent days (Day +2, +3, ...)
        remaining_backlog = backlog[1:]
        current_day_offset = 2
        for t in remaining_backlog:
            target_date = today + timedelta(days=current_day_offset)
            t.due_date = target_date.isoformat()
            t.status = "rescheduled"
            rescheduled_summary.append({
                "task_id": t.id,
                "title": t.title,
                "new_date": t.due_date,
                "day_label": target_date.strftime("%a, %b %d"),
                "estimated_minutes": t.estimated_minutes
            })
            current_day_offset += 1

        # Step 3: Shift remaining future tasks forward so they don't collide
        shift_days = current_day_offset
        for ft in future_tasks:
            try:
                ft_date = date.fromisoformat(ft.due_date)
                new_ft_date = ft_date + timedelta(days=shift_days)
                ft.due_date = new_ft_date.isoformat()
                ft.status = "rescheduled"
            except Exception:
                pass

        # Commit all changes to SQLite
        db.commit()

        # Build coaching message
        coaching_msg = (
            f"I hear you! Life happens, and '{user_reason}' is completely valid. "
            f"Instead of piling everything on you, I've recalibrated your schedule. "
            f"Tomorrow is a gentle restart session with just **'{restart_task.title}'** ({restart_task.estimated_minutes} mins). "
            f"The remaining backlog has been smoothed across the next few days so you stay consistent without stress!"
        )

        return {
            "success": True,
            "goal_id": goal_id,
            "goal_title": goal.title,
            "user_reason": user_reason,
            "slipped_days": slipped_days,
            "tasks_rescheduled": len(rescheduled_summary),
            "coaching_message": coaching_msg,
            "restart_task": {
                "id": restart_task.id,
                "title": restart_task.title,
                "due_date": tomorrow_str,
                "minutes": restart_task.estimated_minutes
            },
            "schedule": rescheduled_summary
        }
