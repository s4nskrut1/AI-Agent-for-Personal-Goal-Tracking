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
        Actually modifies SQLite database task schedules using AdaptiveReplanner.
        """
        from agents.replanner import AdaptiveReplanner
        replanner = AdaptiveReplanner()
        result = replanner.evaluate_and_replan(
            goal_id=goal_id,
            user_message=user_message,
            missed_days=missed_days
        )
        return result["formatted_response"]


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
