"""
Progress and Telemetry Service for GoalMate.
Computes real completion metrics, active streaks, weekly consistency, and goal health trajectories.
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models import Task, Goal, ProgressLog


def calculate_progress(user_id: int, goal_id: Optional[int] = None, db: Session = None) -> Dict[str, Any]:
    """
    Computes overall statistics:
    - total, completed, pending, overdue tasks
    - completion percentage
    - streak (consecutive days of completed tasks)
    - weekly consistency (% of last 7 days with active completions)
    """
    today = date.today()
    today_str = today.isoformat()

    query = db.query(Task).join(Goal).filter(Goal.user_id == user_id)
    if goal_id:
        query = query.filter(Task.goal_id == goal_id)

    all_tasks = query.all()
    total = len(all_tasks)
    completed = sum(1 for t in all_tasks if t.status == "completed")
    pending = sum(1 for t in all_tasks if t.status in ["pending", "rescheduled"])
    overdue = sum(1 for t in all_tasks if t.status in ["pending", "rescheduled"] and t.due_date < today_str)

    completion_pct = round((completed / total * 100), 1) if total > 0 else 0.0

    # Current streak calculation: look back day by day
    streak = 0
    curr_check = today

    # Check completions on given day
    def day_has_completion(check_d: date) -> bool:
        d_str = check_d.isoformat()
        for t in all_tasks:
            if t.status == "completed" and t.completed_at and t.completed_at.date() == check_d:
                return True
        # Also check progress_logs table
        log_cnt = db.query(ProgressLog).filter(
            ProgressLog.user_id == user_id,
            ProgressLog.date == d_str,
            ProgressLog.tasks_completed > 0
        ).count()
        return log_cnt > 0

    if day_has_completion(today):
        streak += 1
        curr_check = today - timedelta(days=1)
        while day_has_completion(curr_check):
            streak += 1
            curr_check -= timedelta(days=1)
    else:
        # Check yesterday to keep existing streak alive before today's session
        yesterday = today - timedelta(days=1)
        if day_has_completion(yesterday):
            streak += 1
            curr_check = yesterday - timedelta(days=1)
            while day_has_completion(curr_check):
                streak += 1
                curr_check -= timedelta(days=1)

    # Weekly consistency (active days in last 7 days)
    week_ago = today - timedelta(days=7)
    active_days = 0
    for i in range(7):
        d = today - timedelta(days=i)
        if day_has_completion(d):
            active_days += 1
    weekly_consistency_pct = round((active_days / 7.0) * 100, 1)

    return {
        "goal_id": goal_id,
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending,
        "overdue_tasks": overdue,
        "completion_percentage": completion_pct,
        "current_streak": streak,
        "weekly_consistency_pct": weekly_consistency_pct,
        "active_days_this_week": active_days
    }


def analyze_goal_health(user_id: int, goal_id: int, db: Session = None) -> Dict[str, Any]:
    """Evaluates goal health trajectory based on real overdue and streak data."""
    stats = calculate_progress(user_id, goal_id, db=db)
    overdue = stats["overdue_tasks"]
    streak = stats["current_streak"]

    if overdue == 0 and streak >= 2:
        status = "On Track (Excellent Pace)"
        health_color = "green"
        recommendation = "Maintain current momentum. You are consistently hitting your milestones."
    elif overdue <= 1:
        status = "On Track"
        health_color = "emerald"
        recommendation = "Steady progress. Tackle today's focus task to stay ahead of schedule."
    elif overdue <= 3:
        status = "At Risk"
        health_color = "amber"
        recommendation = "Small backlog accumulating. Consider a 20-minute adaptive catchup session."
    else:
        status = "Needs Recovery / Behind Schedule"
        health_color = "red"
        recommendation = "Multiple tasks missed. Autonomous replanning recommended to redistribute backlog without cramming."

    return {
        "goal_id": goal_id,
        "health_status": status,
        "health_color": health_color,
        "overdue_count": overdue,
        "completion_percentage": stats["completion_percentage"],
        "recommendation": recommendation,
        "metrics": stats
    }


def get_goal_insights(user_id: int, goal_id: Optional[int] = None, db: Session = None) -> List[Dict[str, str]]:
    """Generates grounded behavioral insights from actual database activity."""
    stats = calculate_progress(user_id, goal_id, db=db)
    insights = []

    if stats["weekly_consistency_pct"] >= 70:
        insights.append({
            "type": "positive",
            "title": "High Weekly Consistency",
            "message": f"You logged completions across {stats['active_days_this_week']} of the last 7 days ({stats['weekly_consistency_pct']}% consistency). Strong routine!"
        })
    elif stats["weekly_consistency_pct"] < 40 and stats["total_tasks"] > 3:
        insights.append({
            "type": "warning",
            "title": "Consistency Dip Detected",
            "message": f"Your weekly consistency is at {stats['weekly_consistency_pct']}%. A short 15-minute daily focus session will rebuild your rhythm."
        })

    if stats["current_streak"] >= 3:
        insights.append({
            "type": "streak",
            "title": f"Active {stats['current_streak']}-Day Streak!",
            "message": f"You have logged completions for {stats['current_streak']} consecutive days. Momentum is compounding."
        })

    if stats["overdue_tasks"] > 0:
        insights.append({
            "type": "action_required",
            "title": f"{stats['overdue_tasks']} Overdue Task(s) Detected",
            "message": "Tasks have slipped past scheduled due dates. Trigger 'Replan' to redistribute them across upcoming days without cramming."
        })
    else:
        insights.append({
            "type": "positive",
            "title": "Zero Overdue Tasks",
            "message": "All current milestones are on schedule. Your workload pacing is well calibrated."
        })

    if stats["completed_tasks"] > 0 and stats["pending_tasks"] > 0:
        insights.append({
            "type": "info",
            "title": "Pace Velocity",
            "message": f"{stats['completed_tasks']} completed vs {stats['pending_tasks']} pending tasks. Pace is sufficient to meet your milestone deadline."
        })

    return insights
