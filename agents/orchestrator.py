"""
Agent Orchestrator for GoalMate.
Coordinates user requests through the autonomous agentic loop:
Observe -> Reason -> Route -> Act -> Learn -> Adapt
"""
import re
import json
import logging
from typing import Dict, Any, List, Tuple, Optional

from tools.goal_tools import get_goals, get_goal
from tools.task_tools import get_tasks, complete_task
from tools.progress_tools import calculate_progress, analyze_goal_health
from memory.memory import detect_and_save_preferences, get_memory_context_string
from agents.llm_client import llm_client
from agents.goal_agent import GoalAgent
from agents.planner_agent import PlannerAgent
from agents.progress_agent import ProgressAgent

logger = logging.getLogger("GoalMate.Orchestrator")


class AgentOrchestrator:
    """Master orchestrator for intent reasoning, agent delegation, and state synchronization."""

    def __init__(self):
        self.goal_agent = GoalAgent()
        self.planner_agent = PlannerAgent()
        self.progress_agent = ProgressAgent()

    def classify_intent(self, user_message: str, history: List[Dict[str, str]]) -> str:
        """
        Determines the user intent among the standard GoalMate capabilities.
        Uses LLM classification with robust heuristic fallback.
        """
        text = user_message.lower().strip()
        
        # 1. High-confidence heuristic matches (instant routing)
        if any(p in text for p in ["couldn't study", "could not study", "haven't studied", "haven't done", "missed", "falling behind", "reschedule", "replan", "adjust my plan", "only have 30 min", "only have 15 min", "catch up", "college got hectic", "got hectic", "behind"]):
            return "REPLAN"
            
        if any(p in text for p in ["weekly review", "weekly summary", "how did this week go", "week report"]):
            return "WEEKLY_REVIEW"

        if any(p in text for p in ["today's tasks", "todays tasks", "today tasks", "what should i do today", "tasks for today", "plan for today", "see your plan for today"]):
            return "VIEW_TODAY_TASKS"
            
        if any(p in text for p in ["daily check-in", "daily check in", "check in", "check-in", "how did today go", "today was", "didn't do much"]):
            return "DAILY_CHECK_IN"
            
        if any(p in text for p in ["completed task", "marked done", "finished task", "mark as completed", "done with task", "mark python", "finished today"]):
            return "COMPLETE_TASK"
            
        if any(p in text for p in ["my progress", "show progress", "how am i doing", "view stats", "progress report", "am i on track", "how close am i"]):
            return "VIEW_PROGRESS"
            
        if any(p in text for p in ["my goals", "view goals", "list goals", "all goals"]):
            return "VIEW_GOALS"
            
        # Check if conversation history is currently asking for clarification on a goal
        if history:
            last_assistant_msg = next((m["content"] for m in reversed(history) if m.get("role") == "assistant"), "")
            if any(q in last_assistant_msg.lower() for q in [
                "how much time", "what would success look like", "before i build your plan",
                "i'll need a few details", "what's your current level", "specific areas you want to focus"
            ]):
                return "CREATE_GOAL"

        if any(p in text for p in ["i want to", "i plan to", "my goal is", "learn", "start", "prepare for", "get better at", "become internship-ready", "internship"]):
            return "CREATE_GOAL"


        # 2. LLM Classification
        prompt = f"""
        Classify the intent of the user message into exactly ONE of the following categories:
        - CREATE_GOAL
        - PLAN_GOAL
        - VIEW_GOALS
        - VIEW_PROGRESS
        - COMPLETE_TASK
        - REPLAN
        - DAILY_CHECK_IN
        - WEEKLY_REVIEW
        - GENERAL_COACHING

        User message: "{user_message}"

        Return ONLY the intent category string.
        """
        try:
            res = llm_client.generate_response(prompt).strip().upper()
            valid_intents = {
                "CREATE_GOAL", "PLAN_GOAL", "VIEW_GOALS", "VIEW_PROGRESS",
                "COMPLETE_TASK", "REPLAN", "DAILY_CHECK_IN", "WEEKLY_REVIEW", "GENERAL_COACHING"
            }
            for vi in valid_intents:
                if vi in res:
                    return vi
        except Exception:
            pass

        return "GENERAL_COACHING"

    def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        active_goal_id: Optional[int] = None
    ) -> Tuple[str, Optional[int]]:
        """
        Full Agentic Execution Cycle:
        1. Observe & Learn: Extract user habits/preferences to memory.
        2. Reason: Classify intent.
        3. Act: Route to specialized agent or tool.
        4. Feedback & Adapt: Return structured response and updated active_goal_id.
        """
        # Step 1: Observe & Learn
        detect_and_save_preferences(user_message)
        
        # Determine active goal if not passed
        if not active_goal_id:
            active_goals = get_goals(status="active")
            if active_goals:
                active_goal_id = active_goals[0]["id"]
                
        # Step 2: Reason
        intent = self.classify_intent(user_message, conversation_history)
        logger.info(f"Classified intent: {intent} for user query: '{user_message}'")
        
        # Step 3: Act
        if intent == "CREATE_GOAL":
            clarification_or_confirm, new_goal_id = self.goal_agent.process(user_message, conversation_history)
            if new_goal_id:
                # Build plan immediately
                plan_result = self.planner_agent.build_plan_for_goal(new_goal_id)
                response = f"{clarification_or_confirm}\n\n{plan_result['summary_text']}"
                return response, new_goal_id
            else:
                return clarification_or_confirm, active_goal_id

        elif intent == "REPLAN":
            if not active_goal_id:
                return "You don't have an active goal yet! Tell me what you'd like to achieve (e.g. 'I want to learn Python in 2 months').", None
            response = self.progress_agent.perform_adaptive_replan(active_goal_id, user_message)
            return response, active_goal_id

        elif intent == "DAILY_CHECK_IN":
            if not active_goal_id:
                return "Ready for your daily check-in! Once you create a goal, we can log daily reflections and adapt tasks.", None
            response = self.progress_agent.handle_daily_checkin(active_goal_id, user_message)
            return response, active_goal_id

        elif intent == "VIEW_TODAY_TASKS":
            if not active_goal_id:
                return "You don't have an active goal yet. Start by setting an objective!", None
            from tools.task_tools import get_today_tasks
            today_tasks = get_today_tasks(active_goal_id)
            goal = get_goal(active_goal_id)
            if not today_tasks:
                return f"No pending tasks scheduled for today on **{goal['title'] if goal else 'your goal'}**! You are fully caught up. 🎉", active_goal_id
            lines = [f"### 📋 Today's Planned Tasks — {goal['title'] if goal else ''}\n"]
            for t in today_tasks:
                stat_icon = "✅" if t.get("status") == "completed" else "⏳"
                lines.append(f"- {stat_icon} **{t['title']}** ({t.get('estimated_minutes', 45)} min) — *Priority: {t.get('priority', 'Medium')}*")
            lines.append("\n💡 *Tip: Check tasks off directly in the Today's Tasks card on the right!*")
            return "\n".join(lines), active_goal_id

        elif intent == "WEEKLY_REVIEW":
            if not active_goal_id:
                return "No active goal found to generate a weekly review. Let's create one first!", None
            response = self.progress_agent.generate_weekly_review(active_goal_id)
            return response, active_goal_id

        elif intent == "VIEW_PROGRESS":
            if not active_goal_id:
                return "You don't have an active goal yet. Start by telling me a goal you want to achieve!", None
            stats = calculate_progress(active_goal_id)
            health = analyze_goal_health(active_goal_id)
            goal = get_goal(active_goal_id)
            
            response = (
                f"### 📈 Progress Report: {goal['title']}\n\n"
                f"- **Completion**: {stats['completion_percentage']}% ({stats['completed_tasks']}/{stats['total_tasks']} tasks)\n"
                f"- **Pending Tasks**: {stats['pending_tasks']}\n"
                f"- **Overdue Tasks**: {stats['overdue_tasks']}\n"
                f"- **Active Streak**: 🔥 {stats['current_streak']} days\n"
                f"- **Weekly Consistency**: {stats['weekly_consistency_pct']}%\n"
                f"- **Trajectory**: **{health['health_status']}**\n\n"
                f"💬 *{health['recommendation']}*"
            )
            return response, active_goal_id

        elif intent == "VIEW_GOALS":
            goals = get_goals()
            if not goals:
                return "You have no goals recorded yet. Tell me a goal you'd like to work on!", None
            lines = ["### 🎯 Your Registered Goals:"]
            for g in goals:
                lines.append(f"- **#{g['id']} {g['title']}** ({g['category']}) — Status: `{g['status']}` | Target: `{g.get('target_date', 'N/A')}`")
            return "\n".join(lines), active_goal_id

        elif intent == "COMPLETE_TASK":
            # Extract task id if mentioned (e.g. "complete task 3")
            id_match = re.search(r'task\s*#?(\d+)', user_message.lower())
            if id_match:
                task_id = int(id_match.group(1))
                task = complete_task(task_id)
                if task:
                    stats = calculate_progress(task["goal_id"])
                    return (
                        f"Awesome work! ✅ Marked **{task['title']}** as completed!\n"
                        f"Your updated completion is now **{stats['completion_percentage']}%** "
                        f"with a streak of 🔥 **{stats['current_streak']} days**.",
                        task["goal_id"]
                    )
                else:
                    return f"Task #{task_id} could not be found.", active_goal_id
            else:
                # Find the first pending task due today or earlier
                pending = get_tasks(goal_id=active_goal_id, status="pending")
                if pending:
                    task = complete_task(pending[0]["id"])
                    stats = calculate_progress(task["goal_id"])
                    return (
                        f"Great job! ✅ Marked **{task['title']}** as completed!\n"
                        f"Goal completion is now **{stats['completion_percentage']}%** (Streak: 🔥 {stats['current_streak']} days).",
                        task["goal_id"]
                    )
                return "No pending tasks found to mark as completed!", active_goal_id

        else: # GENERAL_COACHING
            mem_ctx = get_memory_context_string()
            goal_ctx = ""
            if active_goal_id:
                goal = get_goal(active_goal_id)
                if goal:
                    stats = calculate_progress(active_goal_id)
                    goal_ctx = f"Active Goal: {goal['title']}, Progress: {stats['completion_percentage']}%, Streak: {stats['current_streak']} days."
                    
            prompt = f"""
            You are GoalMate, an intelligent, empathetic, and highly actionable AI personal goal coach.
            Context:
            {goal_ctx}
            User Memory:
            {mem_ctx}

            User message: "{user_message}"

            Provide a concise, practical, supportive response (2-3 short paragraphs max).
            Avoid overly cheesy or cliché motivational quotes. Focus on practical execution and realistic planning.
            """
            try:
                response = llm_client.generate_response(prompt)
                return response, active_goal_id
            except Exception:
                return (
                    "I'm here to support your goals! Whether you need to structure a new objective, "
                    "adapt your tasks because life got busy, or do a weekly review, just let me know what you need.",
                    active_goal_id
                )
