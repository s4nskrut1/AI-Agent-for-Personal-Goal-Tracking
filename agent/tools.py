"""
GoalMate — Agentic AI Tools Layer.
These are the real functions the AI agent executes against the database.
The Gemini model uses function-calling to invoke these tools.
"""
import json
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

from backend.services import (
    get_all_goals, get_goal, create_goal_record, update_goal, delete_goal,
    create_milestone, get_milestones,
    create_task, complete_task, get_tasks_for_goal, get_today_tasks,
    get_tasks_by_date, replan_goal, reschedule_tasks,
    get_weekly_data, get_streak, get_recent_activity, get_dashboard_stats,
    get_session, log_activity
)
from backend.models import Goal, Task, SessionLocal

logger = logging.getLogger("goalmate-agent")


# ─────────────────────────── TOOL DEFINITIONS ───────────────────────────────
# These are passed to Gemini as the function declarations for function calling.

TOOL_DECLARATIONS = [
    {
        "name": "get_user_progress_summary",
        "description": "Retrieve a complete summary of the user's current goals, tasks, and progress from the database. Call this when the user asks 'how am I doing', 'what's my progress', or similar.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_today_tasks_list",
        "description": "Get all tasks scheduled for today across all goals. Use this when user asks 'what should I do today', 'what's on my list', 'I only have 30 minutes today', etc.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "create_goal_with_plan",
        "description": "Create a new goal in the database, generate appropriate milestones and daily tasks with scheduled dates, and save everything. Use this when a user says they want to learn or achieve something with a timeline.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "The goal title, e.g. 'Learn Angular'"},
                "description": {"type": "string", "description": "Brief description of the goal"},
                "category": {"type": "string", "description": "Category e.g. 'Programming', 'Health', 'Learning'"},
                "duration_days": {"type": "integer", "description": "Duration in days, e.g. 30"},
                "milestones": {
                    "type": "array",
                    "description": "List of milestone titles to create, in order",
                    "items": {"type": "string"}
                },
                "tasks": {
                    "type": "array",
                    "description": "List of daily task objects with title, day_number (1-indexed), duration",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "day_number": {"type": "integer"},
                            "duration": {"type": "string"},
                            "milestone_index": {"type": "integer", "description": "0-based index into milestones list"}
                        }
                    }
                }
            },
            "required": ["title", "duration_days", "milestones", "tasks"]
        }
    },
    {
        "name": "complete_task_by_id",
        "description": "Mark a specific task as completed or uncompleted. Use this when a user says they finished a task or want to unmark one.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "The task ID to complete"},
                "completed": {"type": "boolean", "description": "True to mark complete, False to unmark"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "replan_goal_duration",
        "description": "Change a goal's duration and reschedule all pending tasks. Use when user says 'make my X plan Y days instead of Z', or 'shorten/extend my goal'.",
        "parameters": {
            "type": "object",
            "properties": {
                "goal_id": {"type": "integer", "description": "The goal ID to replan"},
                "new_duration_days": {"type": "integer", "description": "The new total duration in days"},
                "reason": {"type": "string", "description": "Brief reason for replanning"}
            },
            "required": ["goal_id", "new_duration_days"]
        }
    },
    {
        "name": "analyze_missed_tasks",
        "description": "Identify missed tasks for a goal or all goals (tasks with past scheduled dates that are still pending). Use when user says they missed a day or couldn't study.",
        "parameters": {
            "type": "object",
            "properties": {
                "goal_id": {"type": "integer", "description": "Optional specific goal ID, or omit for all goals"}
            },
            "required": []
        }
    },
    {
        "name": "get_goal_details",
        "description": "Get detailed info about a specific goal including milestones and tasks. Use when user asks about a specific goal.",
        "parameters": {
            "type": "object",
            "properties": {
                "goal_id": {"type": "integer", "description": "The goal ID"}
            },
            "required": ["goal_id"]
        }
    },
    {
        "name": "delete_goal_by_id",
        "description": "Delete a goal and all its milestones and tasks. Only call after explicit user confirmation.",
        "parameters": {
            "type": "object",
            "properties": {
                "goal_id": {"type": "integer", "description": "The goal ID to delete"}
            },
            "required": ["goal_id"]
        }
    },
    {
        "name": "search_learning_resources",
        "description": "Search the web for high-quality tutorials, official documentation, GitHub repositories, and learning resources for a specific topic, skill, or task. Use when user asks for tutorials, practice resources, or when planning detailed study materials.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query, e.g. 'Angular Directives tutorial for beginners'"},
                "topic": {"type": "string", "description": "The broader topic or goal title"}
            },
            "required": ["query"]
        }
    }
]


# ─────────────────────────── TOOL EXECUTORS ─────────────────────────────────

def execute_tool(tool_name: str, args: Dict[str, Any], user_id: Optional[int] = 1) -> Dict[str, Any]:
    """Route tool calls to appropriate functions and return results."""
    try:
        if tool_name == "get_user_progress_summary":
            return tool_get_progress_summary(user_id=user_id)
        elif tool_name == "get_today_tasks_list":
            return tool_get_today_tasks(user_id=user_id)
        elif tool_name == "create_goal_with_plan":
            return tool_create_goal_with_plan(**args, user_id=user_id)
        elif tool_name == "complete_task_by_id":
            return tool_complete_task(args["task_id"], args.get("completed", True))
        elif tool_name == "replan_goal_duration":
            return tool_replan_goal(args["goal_id"], args["new_duration_days"], args.get("reason", ""))
        elif tool_name == "analyze_missed_tasks":
            return tool_analyze_missed(args.get("goal_id"))
        elif tool_name == "get_goal_details":
            return tool_get_goal_details(args["goal_id"])
        elif tool_name == "delete_goal_by_id":
            return tool_delete_goal(args["goal_id"])
        elif tool_name == "search_learning_resources":
            return tool_search_learning_resources(args.get("query", ""), args.get("topic", ""))
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        logger.error(f"Tool execution error [{tool_name}]: {e}", exc_info=True)
        return {"error": str(e)}


def tool_get_progress_summary(user_id: Optional[int] = 1) -> Dict:
    db = get_session()
    try:
        goals = get_all_goals(db, user_id=user_id)
        streak = get_streak(db, user_id=user_id)
        today_tasks = get_today_tasks(db, user_id=user_id)
        
        goal_summaries = []
        for g in goals:
            milestones = get_milestones(g.id, db)
            goal_summaries.append({
                "id": g.id,
                "title": g.title,
                "progress_pct": g.progress_pct,
                "completed_tasks": g.completed_tasks,
                "total_tasks": g.total_tasks,
                "days_remaining": g.days_remaining,
                "deadline": str(g.deadline) if g.deadline else None,
                "milestones": [{
                    "title": m.title,
                    "progress_pct": m.progress_pct,
                    "completed": m.completed_tasks,
                    "total": m.total_tasks
                } for m in milestones]
            })
        
        today_pending = [t for t in today_tasks if t["status"] == "pending"]
        today_done = [t for t in today_tasks if t["status"] == "completed"]
        
        return {
            "success": True,
            "total_goals": len(goals),
            "streak_days": streak,
            "today_pending": today_pending,
            "today_completed": today_done,
            "goals": goal_summaries
        }
    finally:
        db.close()


def tool_get_today_tasks(user_id: Optional[int] = 1) -> Dict:
    db = get_session()
    try:
        tasks = get_today_tasks(db, user_id=user_id)
        pending = [t for t in tasks if t["status"] == "pending"]
        completed = [t for t in tasks if t["status"] == "completed"]
        return {
            "success": True,
            "today": str(datetime.now().date()),
            "pending": pending,
            "completed": completed,
            "total": len(tasks)
        }
    finally:
        db.close()


def tool_create_goal_with_plan(
    title: str,
    duration_days: int,
    milestones: List[str],
    tasks: List[Dict],
    description: str = "",
    category: str = "Learning",
    user_id: Optional[int] = 1
) -> Dict:
    db = get_session()
    try:
        # Create goal
        start_date = datetime.now().date()
        goal = create_goal_record(title, description, category, duration_days, start_date, db=db, user_id=user_id)
        
        # Create milestones
        milestone_objects = []
        for i, m_title in enumerate(milestones):
            m = create_milestone(goal.id, m_title, order_index=i, db=db)
            milestone_objects.append(m)
        
        # Create tasks with scheduled dates
        created_tasks = 0
        for task_data in tasks:
            day_num = task_data.get("day_number", 1)
            scheduled = start_date + timedelta(days=day_num - 1)
            m_idx = task_data.get("milestone_index", 0)
            m_id = milestone_objects[m_idx].id if m_idx < len(milestone_objects) else None
            create_task(
                goal_id=goal.id,
                title=task_data["title"],
                scheduled_date=scheduled,
                milestone_id=m_id,
                estimated_duration=task_data.get("duration", "30 min"),
                db=db
            )
            created_tasks += 1
        
        log_activity(db, goal.id, "goal_created",
                     f"Created goal '{title}' with {len(milestones)} milestones and {created_tasks} tasks", "🎯")
        
        return {
            "success": True,
            "goal_id": goal.id,
            "goal_title": title,
            "milestones_created": len(milestone_objects),
            "tasks_created": created_tasks,
            "deadline": str(goal.deadline),
            "message": f"Created goal '{title}' with {len(milestone_objects)} milestones and {created_tasks} tasks scheduled from today."
        }
    finally:
        db.close()


def tool_complete_task(task_id: int, completed: bool = True) -> Dict:
    db = get_session()
    try:
        task = complete_task(task_id, completed, db)
        if not task:
            return {"success": False, "error": f"Task {task_id} not found"}
        goal = get_goal(task.goal_id, db)
        return {
            "success": True,
            "task_id": task_id,
            "task_title": task.title,
            "status": task.status,
            "goal_title": goal.title if goal else "Unknown",
            "goal_progress": goal.progress_pct if goal else 0,
            "message": f"Task '{task.title}' marked as {'completed' if completed else 'pending'}."
        }
    finally:
        db.close()


def tool_replan_goal(goal_id: int, new_duration_days: int, reason: str = "") -> Dict:
    db = get_session()
    try:
        goal = replan_goal(goal_id, new_duration_days, db)
        if not goal:
            return {"success": False, "error": f"Goal {goal_id} not found"}
        return {
            "success": True,
            "goal_id": goal_id,
            "goal_title": goal.title,
            "new_duration_days": new_duration_days,
            "new_deadline": str(goal.deadline),
            "message": f"Goal '{goal.title}' replanned to {new_duration_days} days. New deadline: {goal.deadline}."
        }
    finally:
        db.close()


def tool_analyze_missed(goal_id: Optional[int] = None) -> Dict:
    db = get_session()
    try:
        today = datetime.now().date()
        q = db.query(Task).filter(Task.status == "pending", Task.scheduled_date < today)
        if goal_id:
            q = q.filter(Task.goal_id == goal_id)
        missed = q.order_by(Task.scheduled_date).all()
        
        result = []
        for t in missed[:20]:
            goal = db.query(Goal).filter(Goal.id == t.goal_id).first()
            result.append({
                "task_id": t.id,
                "title": t.title,
                "scheduled_date": str(t.scheduled_date),
                "goal_title": goal.title if goal else "Unknown",
                "goal_id": t.goal_id
            })
        return {
            "success": True,
            "missed_count": len(missed),
            "missed_tasks": result
        }
    finally:
        db.close()


def tool_get_goal_details(goal_id: int) -> Dict:
    db = get_session()
    try:
        goal = get_goal(goal_id, db)
        if not goal:
            return {"success": False, "error": f"Goal {goal_id} not found"}
        milestones = get_milestones(goal_id, db)
        tasks = get_tasks_for_goal(goal_id, db)
        today = datetime.now().date()
        
        return {
            "success": True,
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "description": goal.description,
                "progress_pct": goal.progress_pct,
                "completed_tasks": goal.completed_tasks,
                "total_tasks": goal.total_tasks,
                "start_date": str(goal.start_date),
                "deadline": str(goal.deadline),
                "days_remaining": goal.days_remaining
            },
            "milestones": [{"id": m.id, "title": m.title, "progress": m.progress_pct, "done": m.completed_tasks, "total": m.total_tasks} for m in milestones],
            "today_tasks": [{"id": t.id, "title": t.title, "status": t.status, "duration": t.estimated_duration} for t in tasks if t.scheduled_date == today],
            "upcoming_tasks": [{"id": t.id, "title": t.title, "scheduled_date": str(t.scheduled_date), "duration": t.estimated_duration} for t in tasks if t.scheduled_date and t.scheduled_date > today and t.status == "pending"][:5]
        }
    finally:
        db.close()


def tool_delete_goal(goal_id: int) -> Dict:
    db = get_session()
    try:
        goal = get_goal(goal_id, db)
        if not goal:
            return {"success": False, "error": f"Goal {goal_id} not found"}
        title = goal.title
        success = delete_goal(goal_id, db)
        return {"success": success, "message": f"Goal '{title}' deleted." if success else "Delete failed"}
    finally:
        db.close()


def tool_search_learning_resources(query: str, topic: str = "") -> Dict:
    import os
    api_key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not api_key:
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    if line.startswith("TAVILY_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip("'\"")
                        break

    if api_key:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=api_key)
            resp = client.search(query=query, max_results=3, search_depth="basic")
            results = []
            for r in resp.get("results", []):
                results.append({
                    "title": r.get("title", "Resource"),
                    "url": r.get("url", ""),
                    "snippet": (r.get("content", "")[:180] + "...").strip()
                })
            return {
                "success": True,
                "source": "tavily_live_search",
                "query": query,
                "count": len(results),
                "resources": results
            }
        except Exception as e:
            logger.warning(f"Tavily API call error: {e}")

    # Fallback curated links when Tavily key is not yet set
    clean_q = query.replace(" ", "+")
    return {
        "success": True,
        "source": "curated_learning_index",
        "query": query,
        "resources": [
            {
                "title": f"{query} — Official Documentation & Tutorial",
                "url": f"https://www.google.com/search?q={clean_q}+official+documentation",
                "snippet": f"High-quality reference guide, conceptual walkthroughs, and official documentation for {query}."
            },
            {
                "title": f"{query} — Practical GitHub Projects & Code Examples",
                "url": f"https://github.com/search?q={clean_q}&type=repositories",
                "snippet": f"Open-source starter kits, architecture patterns, and hands-on code repositories for {query}."
            },
            {
                "title": f"{query} — Interactive Dev.to & FreeCodeCamp Deep-Dives",
                "url": f"https://dev.to/search?q={clean_q}",
                "snippet": f"Community-tested explanations, common pitfall analysis, and guided exercises."
            }
        ]
    }

