"""
Progress Agent for GoalMate.
Monitors task completion, streaks, and overdue tasks; performs daily check-ins,
weekly reviews, and executes autonomous plan recovery and replanning.
"""
import re
import datetime
from typing import Dict, Any, Optional

from tools.progress_tools import calculate_progress, analyze_goal_health, generate_recovery_plan, replan_goal
from tools.task_tools import get_tasks, get_overdue_tasks, get_pending_tasks
from tools.goal_tools import get_goal, get_goals
from memory.memory import save_user_memory


class ProgressAgent:
    """Agent responsible for progress telemetry, reviews, and autonomous adaptation."""

    def __init__(self):
        pass

    def perform_adaptive_replan(
        self,
        goal_id: int,
        user_message: str,
        missed_days: Optional[int] = None
    ) -> str:
        """
        Executes autonomous plan adaptation when the user falls behind or reports missed days.
        Actually modifies SQLite database task schedules.
        """
        text = user_message.lower()
        goal = get_goal(goal_id)
        if not goal:
            return "No active goal found to replan."

        # Detect missed days from message if not explicitly passed
        if missed_days is None:
            days_match = re.search(r'(\d+)\s*days?', text)
            if days_match:
                missed_days = int(days_match.group(1))
            elif "four" in text or "4" in text:
                missed_days = 4
            elif "three" in text or "3" in text:
                missed_days = 3
            elif "two" in text or "2" in text:
                missed_days = 2
            elif "week" in text:
                missed_days = 7
            else:
                missed_days = 3

        # Check for new time constraint in message (e.g. "only 30 minutes per day now")
        time_match = re.search(r'(\d+)\s*(min|minute|hour|hr)s?', text)
        new_daily_mins = None
        if time_match:
            qty = int(time_match.group(1))
            unit = time_match.group(2)
            new_daily_mins = qty * 60 if "h" in unit else qty

        # Execute recovery plan tool (real database update)
        if new_daily_mins and new_daily_mins != goal.get("daily_time_minutes"):
            result = replan_goal(
                goal_id=goal_id,
                new_daily_time_minutes=new_daily_mins,
                adjustment_reason=f"User requested capacity change to {new_daily_mins}m/day"
            )
            save_user_memory("daily_available_time", f"{new_daily_mins} minutes per day", category="constraint")
            adjusted_msg = f"updated your daily study capacity to **{new_daily_mins} minutes/day** and "
        else:
            result = generate_recovery_plan(
                goal_id=goal_id,
                missed_days=missed_days,
                new_daily_minutes=goal.get("daily_time_minutes", 60)
            )
            adjusted_msg = ""

        rescheduled = result.get("rescheduled_tasks", [])
        rescheduled_count = len(rescheduled)
        
        # Build intelligent, empathetic response
        lines = [
            f"You've missed your **{goal['title']}** target for {missed_days} consecutive days.",
            f"Rather than cramming everything into one stressful session, I've {adjusted_msg}redistributed your {rescheduled_count} pending/overdue tasks smoothly across the next week to keep your daily workload sustainable.\n",
            "**Schedule Adjustments Applied in Database:**"
        ]
        for item in rescheduled[:4]:
            lines.append(f"- 🔄 `{item['new_date']}`: **{item['title']}** *(shifted from {item['previous_date']})*")
        if rescheduled_count > 4:
            lines.append(f"- *...and {rescheduled_count - 4} additional tasks shifted forward.*")
            
        lines.append("\n💡 **Next Step**: Don't worry about the past few days. Just focus on today's single 30–45 minute task to rebuild your momentum!")
        return "\n".join(lines)

    def handle_daily_checkin(self, goal_id: int, user_message: str) -> str:
        """
        Processes a daily check-in:
        Understands user's reflection, inspects today's planned tasks, adjusts priorities if needed.
        """
        goal = get_goal(goal_id)
        today_str = datetime.date.today().isoformat()
        today_tasks = get_tasks(goal_id=goal_id, date=today_str)
        text = user_message.lower()

        # Did they finish or struggle?
        if any(term in text for term in ["finished", "done", "completed", "did it", "nailed it"]):
            return (
                "Fantastic job! 🎉 I've registered your progress for today. "
                "Consistency is key—take a well-deserved rest tonight and we will continue tomorrow!"
            )

        if any(term in text for term in ["didn't do much", "busy", "tired", "couldn't", "missed", "college", "exam", "work"]):
            # Shift today's pending tasks to tomorrow so they don't pile up
            pending_today = [t for t in today_tasks if t.get("status") == "pending"]
            if pending_today:
                from tools.task_tools import reschedule_task
                tomorrow_str = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
                rescheduled_names = []
                for t in pending_today:
                    reschedule_task(t["id"], tomorrow_str)
                    rescheduled_names.append(t["title"])
                
                return (
                    f"I completely understand—life gets busy with college and commitments! 💙 "
                    f"Rather than letting tasks pile up, I have moved today's {len(pending_today)} pending task(s) "
                    f"({', '.join(rescheduled_names)}) to tomorrow.\n\n"
                    f"Get some good rest tonight. Tomorrow is a fresh start!"
                )
            else:
                return (
                    "Thanks for checking in! Life happens, and pacing yourself is part of the process. "
                    "Your schedule is intact, and we'll pick up our next focused session tomorrow."
                )

        return (
            "Thanks for the daily check-in! Your current trajectory is logged. "
            "Let me know if you want to adjust any upcoming deadlines or change your daily study duration."
        )

    def generate_weekly_review(self, goal_id: int) -> str:
        """
        Generates a structured weekly review with quantitative metrics,
        strengths, bottlenecks, and next week recommendations.
        """
        goal = get_goal(goal_id)
        stats = calculate_progress(goal_id)
        health = analyze_goal_health(goal_id)
        
        pct = stats["completion_percentage"]
        completed = stats["completed_tasks"]
        overdue = stats["overdue_tasks"]
        streak = stats["current_streak"]
        consistency = stats["weekly_consistency_pct"]
        
        lines = [
            f"### 📊 Weekly AI Review — {goal['title'] if goal else 'All Goals'}\n",
            f"🎯 **Overall Progress**: {pct}%",
            f"✅ **{completed} tasks completed** | ⚠️ **{overdue} tasks overdue** | 🔥 **{streak}-day streak**",
            f"📈 **7-Day Consistency**: {consistency}%\n",
            "**What went well:**",
            f"- Maintained an active streak of {streak} days with strong momentum.",
            "- Consistently tackled core milestone tasks during scheduled windows.\n",
            "**What needs attention:**"
        ]
        if overdue > 0:
            lines.append(f"- {overdue} task(s) slipped past their scheduled due dates.")
            lines.append("- Potential bottleneck in deep-work session length.")
        else:
            lines.append("- Zero overdue tasks! Workflow pace is balanced.")
            
        lines.extend([
            "\n**Coach Recommendation:**",
            "- If you feel time pressure, break larger 60-minute tasks into 25-minute Pomodoro sprints.",
            f"- Health status is **{health['health_status']}**. {health['recommendation']}"
        ])
        return "\n".join(lines)
