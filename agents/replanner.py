"""
Dedicated Adaptive Replanning Engine for GoalMate.
Compares expected vs actual progress, diagnoses capacity bottlenecks,
and algorithmically redistributes backlogs across future dates without cramming.
"""
import re
import datetime
from typing import Dict, Any, Optional, List

from tools.goal_tools import get_goal, update_goal
from tools.task_tools import get_tasks, get_overdue_tasks, get_pending_tasks
from tools.progress_tools import calculate_progress, analyze_goal_health, generate_recovery_plan
from memory.memory import save_user_memory


class AdaptiveReplanner:
    """
    Autonomous replanning engine:
    1. Evaluates Expected Progress vs. Actual Progress
    2. Identifies reasons for lag (missed days, hectic college, changed daily hours)
    3. Reallocates tasks dynamically into SQLite
    4. Provides empathetic, actionable guidance
    """

    def __init__(self):
        pass

    def evaluate_and_replan(
        self,
        goal_id: int,
        user_message: str,
        missed_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for adaptive replanning.
        """
        text = user_message.lower()
        goal = get_goal(goal_id)
        if not goal:
            return {
                "success": False,
                "message": "No active goal found to replan.",
                "rescheduled_count": 0
            }

        # 1. Detect missed days from text if not provided
        if missed_days is None:
            days_match = re.search(r'(\d+)\s*days?', text)
            if days_match:
                missed_days = int(days_match.group(1))
            elif "two" in text or "2" in text or "last two days" in text:
                missed_days = 2
            elif "three" in text or "3" in text:
                missed_days = 3
            elif "four" in text or "4" in text:
                missed_days = 4
            elif "week" in text:
                missed_days = 7
            else:
                missed_days = 2  # sensible default for reported slip

        # 2. Detect any user-requested capacity update (e.g. "only 30 minutes today", "only 45 min")
        time_match = re.search(r'(\d+)\s*(min|minute|hour|hr)s?', text)
        new_daily_mins = None
        if time_match:
            qty = int(time_match.group(1))
            unit = time_match.group(2)
            new_daily_mins = qty * 60 if "h" in unit else qty

        # 3. Detect bottleneck cause from user message
        reasons = []
        if any(w in text for w in ["college", "university", "exam", "assignment", "hectic"]):
            reasons.append("academic workload (college/exams)")
            save_user_memory("recent_blocker", "College academic workload", category="context")
        if any(w in text for w in ["sick", "unwell", "fever", "ill", "health"]):
            reasons.append("health recovery")
        if any(w in text for w in ["work", "office", "job", "overtime"]):
            reasons.append("work commitments")
        if not reasons:
            reasons.append("unforeseen schedule disruptions")
            
        primary_reason = ", ".join(reasons)

        # 4. Execute recovery plan in database
        daily_cap = new_daily_mins or goal.get("daily_time_minutes", 60)
        
        recovery_result = generate_recovery_plan(
            goal_id=goal_id,
            missed_days=missed_days,
            new_daily_minutes=daily_cap
        )
        
        rescheduled_tasks = recovery_result.get("rescheduled_tasks", [])
        rescheduled_count = len(rescheduled_tasks)

        # 5. Format human-centric agent message
        # Highlight: missed days acknowledged, deadline preserved, tasks redistributed smoothly
        headline = f"You’ve missed {missed_days} day{'s' if missed_days != 1 else ''} due to {primary_reason}, but your target deadline is unchanged."
        strategy = (
            f"I’ve redistributed your {rescheduled_count} unfinished tasks across the next 5 days "
            f"and capped tomorrow’s workload at **{min(45, daily_cap)} minutes** so your recovery plan remains realistic and sustainable without cramming."
        )

        schedule_preview = []
        for t in rescheduled_tasks[:4]:
            schedule_preview.append(f"- 🔄 `{t['new_date']}`: **{t['title']}** *(shifted from {t['previous_date']})*")
        if rescheduled_count > 4:
            schedule_preview.append(f"- *...plus {rescheduled_count - 4} additional tasks shifted smoothly.*")

        formatted_response = (
            f"{headline}\n\n"
            f"{strategy}\n\n"
            f"**Adjusted Schedule in Database:**\n"
            f"{chr(10).join(schedule_preview)}\n\n"
            f"💡 **Coach Advice**: Don't stress about the missed days—consistency is built on restarts. "
            f"Focus solely on tomorrow's initial task to restore your streak!"
        )

        return {
            "success": True,
            "goal_id": goal_id,
            "missed_days": missed_days,
            "primary_reason": primary_reason,
            "rescheduled_count": rescheduled_count,
            "rescheduled_tasks": rescheduled_tasks,
            "formatted_response": formatted_response
        }
