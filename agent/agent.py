"""
Master AI Goal Coach Agent for GoalMate.
Coordinates LLM inference, heuristic fallbacks, deterministic tool execution,
and adaptive replanning.
"""
import re
from datetime import date, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from agent.llm import llm_client
from agent.prompts import (
    COACH_SYSTEM_INSTRUCTION,
    CLARIFY_GOAL_PROMPT,
    PLAN_GOAL_PROMPT,
    REPLAN_PROMPT
)
from agent.replanner import AdaptiveReplanner
from agent.tools import (
    tool_create_goal,
    tool_create_milestones,
    tool_create_tasks,
    tool_complete_task,
    tool_get_today_tasks,
    tool_get_goal_health,
    tool_search_resources
)
from services import goal_service, task_service, progress_service


class GoalMateAgent:
    """Conversational and autonomous AI Goal Coach orchestrator."""

    def __init__(self):
        self.llm = llm_client

    def process_message(
        self,
        user_message: str,
        user_id: int,
        db: Session,
        active_goal_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Main cognitive pipeline:
        1. Classify intent.
        2. Execute tools / adapt schedule.
        3. Formulate response with suggested action chips.
        """
        msg_lower = user_message.lower().strip()

        # Resolve active goal if not passed
        if not active_goal_id:
            user_goals = goal_service.get_goals(user_id, db=db)
            if user_goals:
                active_goal_id = user_goals[0].id

        # -------------------------------------------------------------
        # 1. INTENT: ADAPTIVE REPLANNING (Missed days / Slipped schedule)
        # -------------------------------------------------------------
        replan_keywords = ["couldn't study", "could not study", "missed", "fell behind", "hectic",
                           "college", "exam", "sick", "replan", "reschedule", "busy", "behind schedule",
                           "catch up", "overwhelmed"]
        if any(kw in msg_lower for kw in replan_keywords):
            return self._handle_replanning(user_message, user_id, active_goal_id, db)

        # -------------------------------------------------------------
        # 2. INTENT: TASK COMPLETION
        # -------------------------------------------------------------
        complete_keywords = ["completed task", "finished task", "mark done", "done with", "checked off"]
        if any(kw in msg_lower for kw in complete_keywords) or (msg_lower.startswith("done") and len(msg_lower) < 25):
            return self._handle_task_completion(user_message, user_id, active_goal_id, db)

        # -------------------------------------------------------------
        # 3. INTENT: RESEARCH / RESOURCES
        # -------------------------------------------------------------
        resource_keywords = ["resource", "resources", "course", "courses", "learn", "video", "tutorial",
                             "roadmap", "recommend", "books", "practice", "codewars", "leetcode"]
        if any(kw in msg_lower for kw in resource_keywords) and not ("want to" in msg_lower and "goal" in msg_lower):
            return self._handle_resource_search(user_message)

        # -------------------------------------------------------------
        # 4. INTENT: NEW GOAL CREATION & CLARIFICATION
        # -------------------------------------------------------------
        new_goal_keywords = ["i want to", "new goal", "target is", "plan to", "aiming to", "become"]
        if any(kw in msg_lower for kw in new_goal_keywords) and len(user_message) > 15:
            return self._handle_new_goal_initiation(user_message, user_id, db)

        # -------------------------------------------------------------
        # 5. INTENT: PROGRESS / STATUS INQUIRY
        # -------------------------------------------------------------
        status_keywords = ["status", "progress", "how am i doing", "health", "streak", "overview", "report"]
        if any(kw in msg_lower for kw in status_keywords):
            return self._handle_progress_inquiry(user_id, active_goal_id, db)

        # -------------------------------------------------------------
        # 6. GENERAL CONVERSATION / COACHING
        # -------------------------------------------------------------
        return self._handle_general_coaching(user_message, user_id, active_goal_id, db)

    # -----------------------------------------------------------------
    # Handler Implementations
    # -----------------------------------------------------------------

    def _handle_replanning(
        self,
        user_message: str,
        user_id: int,
        goal_id: Optional[int],
        db: Session
    ) -> Dict[str, Any]:
        """Performs adaptive replanning with psychological smoothing."""
        if not goal_id:
            return {
                "reply": "I'd love to help you replan, but you don't have an active goal yet! Tell me what goal you'd like to work towards.",
                "chips": ["Create Python Goal", "Learn Web Development", "Prepare Placements"],
                "action": None
            }

        replan_result = AdaptiveReplanner.replan_goal(
            user_id=user_id,
            goal_id=goal_id,
            user_reason=user_message,
            db=db
        )

        reply_lines = [
            replan_result["coaching_message"],
            "",
            "### 🔄 Recalibrated Schedule:",
        ]
        for item in replan_result.get("schedule", []):
            reply_lines.append(f"- **{item['day_label']}**: {item['title']} *({item['estimated_minutes']} mins)*")

        reply_lines.append("")
        reply_lines.append("⚡ *No penalty, no guilt. Tomorrow is all about rebuilding your streak with one easy win!*")

        return {
            "reply": "\n".join(reply_lines),
            "chips": ["I'm ready for tomorrow! 🚀", "Show Today's Tasks", "View Updated Roadmap"],
            "action": {"type": "replan", "data": replan_result}
        }

    def _handle_task_completion(
        self,
        user_message: str,
        user_id: int,
        goal_id: Optional[int],
        db: Session
    ) -> Dict[str, Any]:
        """Finds the best matching task and completes it."""
        today_tasks = task_service.get_today_tasks(user_id, goal_id=goal_id, db=db)
        if not today_tasks:
            return {
                "reply": "Awesome job! However, you don't have any pending tasks for today right now. Want to check upcoming tasks or take a well-deserved rest?",
                "chips": ["View Tomorrow's Tasks", "Check Progress", "Explore Resources"],
                "action": None
            }

        # Match task
        target_task = today_tasks[0]
        for t in today_tasks:
            if t.title.lower() in user_message.lower():
                target_task = t
                break

        res = tool_complete_task(user_id, target_task.id, db=db)
        new_streak = res["new_streak"]
        pct = res["completion_percentage"]

        reply = (
            f"🎉 **Great work completing:** *{target_task.title}*!\n\n"
            f"- **Active Streak:** 🔥 {new_streak} day{'s' if new_streak > 1 else ''}\n"
            f"- **Overall Progress:** 📈 {pct}%\n\n"
            "Keep this rhythm alive! What's next on your agenda?"
        )
        return {
            "reply": reply,
            "chips": ["Show Next Task", "How's My Health Score?", "Suggest Free Resources"],
            "action": {"type": "task_completed", "task_id": target_task.id}
        }

    def _handle_resource_search(self, user_message: str) -> Dict[str, Any]:
        """Conducts Tavily web research or curated fallback for study material."""
        results = tool_search_resources(user_message, num_results=3)
        reply_lines = [
            "Here are high-yield, curated learning resources for your goal:",
            ""
        ]
        for idx, item in enumerate(results, start=1):
            reply_lines.append(f"**{idx}. [{item['title']}]({item['url']})**")
            reply_lines.append(f"> {item['snippet']}")
            reply_lines.append("")

        reply_lines.append("💡 *Tip: Dedicate 20 minutes to active practice for every 10 minutes of watching tutorials.*")

        return {
            "reply": "\n".join(reply_lines),
            "chips": ["Add Practice Task", "Check My Progress", "I Have a Question"],
            "action": {"type": "research", "results": results}
        }

    def _handle_new_goal_initiation(
        self,
        user_message: str,
        user_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Provides clarification questions or automatically breaks down goal."""
        # Check if Gemini is available for dynamic plan generation
        if self.llm.is_available():
            try:
                plan_json = self.llm.generate_json(
                    PLAN_GOAL_PROMPT.format(
                        title=user_message,
                        description="Created via GoalMate conversational AI coach",
                        daily_minutes=60,
                        target_weeks=10
                    ),
                    system_instruction=COACH_SYSTEM_INSTRUCTION
                )

                # Persist goal
                g_res = tool_create_goal(
                    user_id=user_id,
                    title=user_message,
                    description=plan_json.get("summary", ""),
                    category=plan_json.get("category", "Education"),
                    target_date=(date.today() + timedelta(days=70)).isoformat(),
                    daily_time_minutes=60,
                    db=db
                )
                goal_id = g_res["goal_id"]

                # Persist milestones
                m_list = []
                for m in plan_json.get("milestones", []):
                    target_d = (date.today() + timedelta(days=m.get("days_from_start", 14))).isoformat()
                    m_list.append({
                        "title": m.get("title"),
                        "description": m.get("description", ""),
                        "order_index": m.get("order_index", 1),
                        "target_date": target_d
                    })
                created_m = tool_create_milestones(user_id, goal_id, m_list, db=db)

                # Persist initial tasks
                t_list = []
                for t in plan_json.get("tasks", []):
                    due_d = (date.today() + timedelta(days=t.get("day_offset", 0))).isoformat()
                    t_list.append({
                        "title": t.get("title"),
                        "description": t.get("description", ""),
                        "due_date": due_d,
                        "estimated_minutes": t.get("estimated_minutes", 45),
                        "priority": t.get("priority", "High")
                    })
                tool_create_tasks(user_id, goal_id, t_list, db=db)

                reply = (
                    f"🎯 **Goal Created & Structured!**\n\n"
                    f"**{user_message}**\n\n"
                    f"*{plan_json.get('summary', '')}*\n\n"
                    f"- ✅ Created **{len(created_m)}** sequential milestones\n"
                    f"- 📅 Generated **{len(t_list)}** initial daily tasks\n\n"
                    f"Your first task is scheduled for today in your dashboard!"
                )
                return {
                    "reply": reply,
                    "chips": ["Show Today's Tasks", "View Milestones", "Find Study Material"],
                    "action": {"type": "goal_created", "goal_id": goal_id}
                }
            except Exception:
                pass

        # Offline / Heuristic Goal Decomposition
        today = date.today()
        g_res = tool_create_goal(
            user_id=user_id,
            title=user_message,
            description="Autonomous goal roadmap generated by GoalMate",
            category="Career",
            target_date=(today + timedelta(days=60)).isoformat(),
            daily_time_minutes=60,
            db=db
        )
        goal_id = g_res["goal_id"]

        default_milestones = [
            {"title": "Core Foundations & Theory", "description": "Mastering essential syntax and concepts", "order_index": 1, "target_date": (today + timedelta(days=14)).isoformat()},
            {"title": "Practical Application & Mini-Builds", "description": "Hands-on projects and exercises", "order_index": 2, "target_date": (today + timedelta(days=35)).isoformat()},
            {"title": "Capstone & Real-World Integration", "description": "Polished project deployment and portfolio review", "order_index": 3, "target_date": (today + timedelta(days=60)).isoformat()}
        ]
        tool_create_milestones(user_id, goal_id, default_milestones, db=db)

        default_tasks = [
            {"title": f"Review roadmap & setup workspace for '{user_message}'", "due_date": today.isoformat(), "estimated_minutes": 30, "priority": "High"},
            {"title": "Complete introductory chapter & write initial code", "due_date": (today + timedelta(days=1)).isoformat(), "estimated_minutes": 45, "priority": "High"},
            {"title": "Solve 3 foundational exercises", "due_date": (today + timedelta(days=2)).isoformat(), "estimated_minutes": 45, "priority": "Medium"}
        ]
        tool_create_tasks(user_id, goal_id, default_tasks, db=db)

        reply = (
            f"🎯 **Roadmap Initialized for '{user_message}'!**\n\n"
            "I've configured 3 progressive milestones and added your initial tasks to the dashboard.\n\n"
            f"Ready to conquer your first session today?"
        )
        return {
            "reply": reply,
            "chips": ["Show Today's Task", "How long will this take?", "Recommend Resources"],
            "action": {"type": "goal_created", "goal_id": goal_id}
        }

    def _handle_progress_inquiry(
        self,
        user_id: int,
        goal_id: Optional[int],
        db: Session
    ) -> Dict[str, Any]:
        """Provides grounded analysis of health and consistency."""
        if not goal_id:
            return {
                "reply": "You don't have any active goals yet! Tell me what you'd like to achieve.",
                "chips": ["Create Goal", "Explore Python Path"],
                "action": None
            }

        health = tool_get_goal_health(user_id, goal_id, db=db)
        metrics = health["metrics"]
        insights = progress_service.get_goal_insights(user_id, goal_id, db=db)

        reply_lines = [
            f"### 📊 Goal Health: **{health['health_status']}**",
            f"- **Completion:** {metrics['completion_percentage']}% ({metrics['completed_tasks']}/{metrics['total_tasks']} tasks)",
            f"- **Streak:** 🔥 {metrics['current_streak']} days",
            f"- **Weekly Consistency:** {metrics['weekly_consistency_pct']}% ({metrics['active_days_this_week']}/7 days active)",
            f"- **Overdue Tasks:** {metrics['overdue_tasks']}",
            "",
            f"💡 **Coach Recommendation:** {health['recommendation']}",
            "",
            "**Key Insights:**"
        ]
        for ins in insights[:2]:
            reply_lines.append(f"- **{ins['title']}**: {ins['message']}")

        return {
            "reply": "\n".join(reply_lines),
            "chips": ["Show Today's Tasks", "Replan Schedule", "Recommend Resources"],
            "action": {"type": "progress_report", "health": health}
        }

    def _handle_general_coaching(
        self,
        user_message: str,
        user_id: int,
        goal_id: Optional[int],
        db: Session
    ) -> Dict[str, Any]:
        """Generates friendly conversational response."""
        if self.llm.is_available():
            try:
                goal_ctx = ""
                if goal_id:
                    g = goal_service.get_goal(goal_id, user_id, db)
                    if g:
                        goal_ctx = f"Active Goal: '{g.title}'."
                prompt = f"{goal_ctx}\nUser message: '{user_message}'\nProvide an encouraging, concise response with 1 actionable tip."
                text = self.llm.generate_text(prompt, system_instruction=COACH_SYSTEM_INSTRUCTION)
                return {
                    "reply": text,
                    "chips": ["Show Today's Tasks", "What's My Streak?", "Replan Schedule"],
                    "action": None
                }
            except Exception:
                pass

        return {
            "reply": (
                f"I'm right here with you! Small, consistent daily steps compound into massive achievements. "
                f"Focus on finishing just one 30-minute block today, and protect your streak! 🔥"
            ),
            "chips": ["Show Today's Tasks", "Check Progress Health", "Suggest Free Resources"],
            "action": None
        }


# Global singleton agent
goal_coach = GoalMateAgent()
