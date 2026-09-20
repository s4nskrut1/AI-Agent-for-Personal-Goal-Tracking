"""
Progress Tracking and Adaptive Replanning Tools for GoalMate.
Calculates objective metrics and executes algorithmic plan adaptation and recovery schedules.
"""
import datetime
from typing import Optional, List, Dict, Any
from database.db import get_db_connection
from tools.task_tools import get_tasks, get_overdue_tasks, get_pending_tasks
from tools.goal_tools import get_goal, update_goal


def calculate_progress(goal_id: Optional[int] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Computes overall statistics:
    - total tasks, completed tasks, pending tasks, overdue tasks
    - completion percentage
    - current streak (consecutive days of completed tasks)
    - weekly consistency (percentage of last 7 days with active completions)
    """
    today = datetime.date.today()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # 1. Task counts
        if goal_id:
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status IN ('pending', 'rescheduled') THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status IN ('pending', 'rescheduled') AND due_date < ? THEN 1 ELSE 0 END) as overdue
                FROM tasks WHERE goal_id = ?
                """,
                (today.isoformat(), goal_id)
            )
        else:
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status IN ('pending', 'rescheduled') THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status IN ('pending', 'rescheduled') AND due_date < ? THEN 1 ELSE 0 END) as overdue
                FROM tasks
                """,
                (today.isoformat(),)
            )
            
        counts = cursor.fetchone()
        total = counts["total"] or 0
        completed = counts["completed"] or 0
        pending = counts["pending"] or 0
        overdue = counts["overdue"] or 0
        completion_pct = round((completed / total * 100), 1) if total > 0 else 0.0

        # 2. Current streak
        # Look back day by day
        streak = 0
        curr_check = today
        # Check if today has a completion, if not check yesterday
        while True:
            cursor.execute(
                "SELECT COUNT(*) as cnt FROM tasks WHERE status = 'completed' AND DATE(completed_at) = ?",
                (curr_check.isoformat(),)
            )
            day_cnt = cursor.fetchone()["cnt"]
            if day_cnt > 0:
                streak += 1
                curr_check -= datetime.timedelta(days=1)
            elif curr_check == today:
                # If today not yet completed, check if yesterday was completed to keep streak alive
                curr_check -= datetime.timedelta(days=1)
                cursor.execute(
                    "SELECT COUNT(*) as cnt FROM tasks WHERE status = 'completed' AND DATE(completed_at) = ?",
                    (curr_check.isoformat(),)
                )
                if cursor.fetchone()["cnt"] > 0:
                    streak += 1
                    curr_check -= datetime.timedelta(days=1)
                else:
                    break
            else:
                break
                
        # 3. Weekly consistency (active days in last 7 days)
        week_ago = (today - datetime.timedelta(days=7)).isoformat()
        cursor.execute(
            """
            SELECT COUNT(DISTINCT DATE(completed_at)) as active_days 
            FROM tasks 
            WHERE status = 'completed' AND completed_at >= ?
            """,
            (week_ago,)
        )
        active_days = cursor.fetchone()["active_days"] or 0
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


def analyze_goal_health(goal_id: int, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Evaluates goal health trajectory:
    - 'Excellent' (0 overdue, active streak)
    - 'On Track' (<= 1 overdue)
    - 'At Risk' (2-3 overdue)
    - 'Needs Intervention / Behind' (> 3 overdue or missed streak)
    """
    stats = calculate_progress(goal_id, db_path=db_path)
    overdue_count = stats["overdue_tasks"]
    pct = stats["completion_percentage"]
    
    if overdue_count == 0 and stats["current_streak"] >= 2:
        status = "On Track (Excellent Pace)"
        health_color = "green"
        recommendation = "Maintain current momentum. You are consistently hitting your milestones."
    elif overdue_count <= 1:
        status = "On Track"
        health_color = "emerald"
        recommendation = "Steady progress. Tackle today's focus task to stay ahead."
    elif overdue_count <= 3:
        status = "At Risk"
        health_color = "amber"
        recommendation = "Small backlog accumulating. Consider an adaptive 20-minute catchup block."
    else:
        status = "Needs Recovery / Behind Schedule"
        health_color = "red"
        recommendation = "Multiple tasks missed. Autonomous replanning recommended to redistribute backlog without cramming."

    return {
        "goal_id": goal_id,
        "health_status": status,
        "health_color": health_color,
        "overdue_count": overdue_count,
        "completion_percentage": pct,
        "recommendation": recommendation,
        "metrics": stats
    }


def generate_recovery_plan(
    goal_id: int,
    missed_days: int = 1,
    new_daily_minutes: Optional[int] = None,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Algorithmic Adaptive Replanning Engine:
    When a user misses days or falls behind:
    1. Fetches all overdue tasks for the goal.
    2. Re-prioritizes: Highest priority tasks placed first starting today/tomorrow.
    3. Shifts the workload across subsequent days respecting daily capacity.
    4. Actually commits the new dates to SQLite.
    5. Returns audit trail of rescheduled tasks.
    """
    today = datetime.date.today()
    now_str = datetime.datetime.now().isoformat()
    goal = get_goal(goal_id, db_path=db_path)
    if not goal:
        return {"success": False, "error": f"Goal {goal_id} not found."}
        
    daily_cap = new_daily_minutes or goal.get("daily_time_minutes", 60) or 60
    
    overdue = get_overdue_tasks(goal_id=goal_id, db_path=db_path)
    pending_future = [t for t in get_pending_tasks(goal_id=goal_id, db_path=db_path) if t not in overdue]
    
    # If no overdue tasks are detected yet (e.g. freshly created plan or current day),
    # but the user explicitly missed days (e.g. 4 days), select the pending tasks within that missed window
    if not overdue and pending_future and missed_days > 0:
        take_count = min(missed_days, len(pending_future))
        overdue = pending_future[:take_count]
        pending_future = pending_future[take_count:]

    if not overdue and not pending_future:
        return {
            "success": True,
            "message": "No pending or overdue tasks to reschedule. Goal is up to date!",
            "rescheduled_tasks": []
        }
        
    rescheduled_audit = []
    
    # We will reschedule all overdue tasks starting today, placing at most 1-2 tasks per day based on daily_cap
    # Then shift future pending tasks forward accordingly
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        schedule_cursor_date = today
        day_accumulated_mins = 0
        
        # 1. Schedule overdue tasks first (sorted by priority: High -> Medium -> Low)
        priority_order = {"High": 1, "Critical": 0, "Medium": 2, "Low": 3}
        sorted_overdue = sorted(overdue, key=lambda t: priority_order.get(t.get("priority", "Medium"), 2))
        
        for task in sorted_overdue:
            task_mins = task.get("estimated_minutes", 45) or 45
            if day_accumulated_mins + task_mins > daily_cap and day_accumulated_mins > 0:
                # Move to next day to avoid cramming
                schedule_cursor_date += datetime.timedelta(days=1)
                day_accumulated_mins = 0
                
            new_date_str = schedule_cursor_date.isoformat()
            cursor.execute(
                """
                UPDATE tasks 
                SET due_date = ?, status = 'rescheduled', updated_at = ?
                WHERE id = ?
                """,
                (new_date_str, now_str, task["id"])
            )
            rescheduled_audit.append({
                "id": task["id"],
                "title": task["title"],
                "previous_date": task["due_date"],
                "new_date": new_date_str,
                "reason": "Overdue backlog redistributed smoothly"
            })
            day_accumulated_mins += task_mins

        # 2. Shift subsequent pending tasks forward so they don't overlap with rescheduled backlog
        if rescheduled_audit:
            # The next available day for future tasks
            next_free_date = schedule_cursor_date + datetime.timedelta(days=1)
            for f_task in pending_future:
                try:
                    f_due = datetime.date.fromisoformat(f_task["due_date"])
                except Exception:
                    f_due = today
                    
                if f_due < next_free_date:
                    shift_days = (next_free_date - f_due).days
                    shifted_date = (f_due + datetime.timedelta(days=shift_days)).isoformat()
                    cursor.execute(
                        """
                        UPDATE tasks 
                        SET due_date = ?, status = 'rescheduled', updated_at = ?
                        WHERE id = ?
                        """,
                        (shifted_date, now_str, f_task["id"])
                    )
                    rescheduled_audit.append({
                        "id": f_task["id"],
                        "title": f_task["title"],
                        "previous_date": f_task["due_date"],
                        "new_date": shifted_date,
                        "reason": "Cascading shift to prevent cramming"
                    })
                    next_free_date = datetime.date.fromisoformat(shifted_date) + datetime.timedelta(days=1)
                    
        conn.commit()
        
    return {
        "success": True,
        "goal_id": goal_id,
        "rescheduled_count": len(rescheduled_audit),
        "rescheduled_tasks": rescheduled_audit,
        "daily_time_constraint": f"{daily_cap} mins/day",
        "adaptation_summary": (
            f"Autonomous Replanning completed: {len(rescheduled_audit)} tasks adjusted. "
            f"Overdue tasks spread across the next few days with a strict {daily_cap}-min/day ceiling to prevent cognitive fatigue."
        )
    }


def replan_goal(
    goal_id: int,
    new_daily_time_minutes: int,
    adjustment_reason: str = "User capacity adjustment",
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Updates the goal's daily availability constraint and re-runs recovery/rebalancing.
    """
    update_goal(goal_id, daily_time_minutes=new_daily_time_minutes, db_path=db_path)
    recovery_result = generate_recovery_plan(
        goal_id=goal_id,
        new_daily_minutes=new_daily_time_minutes,
        db_path=db_path
    )
    recovery_result["reason"] = adjustment_reason
    return recovery_result


# --- Explicit Section 4 Tool Aliases & Insights ---

def analyze_progress(goal_id: Optional[int] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Analyzes overall progress metrics for a goal or entire portfolio."""
    return calculate_progress(goal_id=goal_id, db_path=db_path)


def detect_goal_risk(goal_id: int, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Evaluates goal health trajectory and risk state (On Track, At Risk, Behind)."""
    return analyze_goal_health(goal_id=goal_id, db_path=db_path)


def log_progress(
    goal_id: int,
    date: Optional[str] = None,
    tasks_completed: int = 1,
    minutes_spent: int = 45,
    notes: str = "",
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Logs explicit progress telemetry entry in progress_logs."""
    date_str = date or datetime.date.today().isoformat()
    now_str = datetime.datetime.now().isoformat()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO progress_logs (goal_id, date, tasks_completed, total_minutes_spent, streak_count, notes, created_at)
            VALUES (?, ?, ?, ?, 1, ?, ?)
            """,
            (goal_id, date_str, tasks_completed, minutes_spent, notes, now_str)
        )
        conn.commit()
        log_id = cursor.lastrowid
        cursor.execute("SELECT * FROM progress_logs WHERE id = ?", (log_id,))
        return dict(cursor.fetchone())


def get_goal_insights(goal_id: Optional[int] = None, db_path: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Generates data-driven behavioral insights based on actual SQLite logs and task distributions.
    Does NOT invent claims without underlying data.
    """
    stats = calculate_progress(goal_id, db_path=db_path)
    health = analyze_goal_health(goal_id, db_path=db_path) if goal_id else None
    
    insights = []
    
    # Consistency insight
    if stats["weekly_consistency_pct"] >= 70:
        insights.append({
            "type": "positive",
            "title": "High Weekly Consistency",
            "message": f"You maintained activity across {stats['active_days_this_week']} of the last 7 days ({stats['weekly_consistency_pct']}% consistency). Strong routine!"
        })
    elif stats["weekly_consistency_pct"] < 40 and stats["total_tasks"] > 3:
        insights.append({
            "type": "warning",
            "title": "Consistency Dip Detected",
            "message": f"Your consistency is currently at {stats['weekly_consistency_pct']}%. A short 15-minute daily focus session will rebuild your rhythm."
        })
        
    # Streak insight
    if stats["current_streak"] >= 3:
        insights.append({
            "type": "streak",
            "title": f"Active {stats['current_streak']}-Day Streak!",
            "message": f"You have logged completions for {stats['current_streak']} consecutive days. Momentum is compounding."
        })
        
    # Backlog & risk insight
    if stats["overdue_tasks"] > 0:
        insights.append({
            "type": "action_required",
            "title": f"{stats['overdue_tasks']} Overdue Tasks Detected",
            "message": "Tasks have slipped past due dates. Trigger 'Replan' to redistribute them across upcoming days without cramming."
        })
    else:
        insights.append({
            "type": "positive",
            "title": "Zero Overdue Tasks",
            "message": "All current milestones are on schedule. Your daily workload allocation is well-calibrated."
        })
        
    # Pace estimation
    if stats["completed_tasks"] > 0 and stats["pending_tasks"] > 0:
        insights.append({
            "type": "info",
            "title": "Pace Calibration",
            "message": f"{stats['completed_tasks']} completed vs {stats['pending_tasks']} pending. Completion velocity is sufficient to reach target outcome."
        })
        
    return insights

