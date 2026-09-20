"""
Planner Agent for GoalMate.
Decomposes goals into sequential milestones and scheduled daily tasks.
Stores all generated milestones and tasks directly in the SQLite database.
"""
import re
import json
import datetime
from typing import Dict, Any, List, Optional

from tools.goal_tools import get_goal, create_milestone
from tools.task_tools import create_task
from memory.memory import get_memory_context_string
from agents.llm_client import llm_client


class PlannerAgent:
    """Agent that generates structured milestones and tasks, scheduling them realistically."""

    def __init__(self):
        pass

    def build_plan_for_goal(self, goal_id: int) -> Dict[str, Any]:
        """
        Decomposes the specified goal into milestones and tasks, commits them to SQLite,
        and returns the plan breakdown.
        """
        goal = get_goal(goal_id)
        if not goal:
            return {"error": f"Goal {goal_id} not found."}

        # Try LLM-based decomposition first
        plan_data = self._generate_plan_llm(goal)
        if not plan_data:
            # Fallback to intelligent deterministic templates
            plan_data = self._generate_plan_heuristic(goal)

        # Commit to SQLite
        created_milestones = []
        created_tasks = []
        
        today = datetime.date.today()
        task_cursor_date = today
        
        for m_idx, m_info in enumerate(plan_data.get("milestones", []), 1):
            m_target = (today + datetime.timedelta(days=m_idx * 14)).isoformat()
            milestone = create_milestone(
                goal_id=goal_id,
                title=m_info["title"],
                description=m_info.get("description", ""),
                order_index=m_idx,
                target_date=m_target
            )
            created_milestones.append(milestone)
            
            for t_info in m_info.get("tasks", []):
                est_mins = t_info.get("estimated_minutes", goal.get("daily_time_minutes", 60)) or 60
                task = create_task(
                    goal_id=goal_id,
                    milestone_id=milestone["id"],
                    title=t_info["title"],
                    description=t_info.get("description", ""),
                    due_date=task_cursor_date.isoformat(),
                    estimated_minutes=est_mins,
                    priority=t_info.get("priority", "Medium")
                )
                created_tasks.append(task)
                # Increment date by 1-2 days based on frequency
                task_cursor_date += datetime.timedelta(days=1)

        return {
            "goal": goal,
            "milestones": created_milestones,
            "tasks": created_tasks,
            "summary_text": self._format_plan_summary(goal, created_milestones, created_tasks)
        }

    def _generate_plan_llm(self, goal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generates milestones and tasks via LLM."""
        memory_ctx = get_memory_context_string()
        prompt = f"""
        Break down the following goal into 4 to 6 milestones, and 2 to 3 concrete tasks per milestone.
        
        Goal: {goal['title']}
        Description: {goal['description']}
        Daily Available Time: {goal['daily_time_minutes']} minutes/day
        User Memory / Context:
        {memory_ctx}

        Requirements:
        Return ONLY valid JSON with this structure:
        {{
            "milestones": [
                {{
                    "title": "Milestone Title",
                    "description": "Brief description",
                    "tasks": [
                        {{
                            "title": "Actionable task name",
                            "description": "Short instruction",
                            "estimated_minutes": {goal['daily_time_minutes']},
                            "priority": "High"
                        }}
                    ]
                }}
            ]
        }}
        """
        try:
            raw_json = llm_client.generate_response(prompt, json_mode=True)
            clean_str = re.sub(r'```(?:json)?\s*|\s*```', '', raw_json).strip()
            parsed = json.loads(clean_str)
            from database.models import LLMGoalPlan
            validated = LLMGoalPlan.model_validate(parsed)
            return validated.model_dump()
        except Exception:
            return None

    def _generate_plan_heuristic(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """Provides expert structured curricula for standard domains when offline."""
        title_lower = goal["title"].lower()
        daily_mins = goal.get("daily_time_minutes", 60) or 60
        
        # 1. Python Programming Domain
        if "python" in title_lower or "code" in title_lower or "programming" in title_lower:
            return {
                "milestones": [
                    {
                        "title": "Python Fundamentals",
                        "description": "Syntax, variables, conditionals, loops, and basic data types",
                        "tasks": [
                            {"title": "Setup Python environment and write first script", "description": "Verify python installation and IDE setup", "estimated_minutes": daily_mins, "priority": "High"},
                            {"title": "Master Variables, Data Types & Conditionals", "description": "Solve 5 conditional logic problems", "estimated_minutes": daily_mins, "priority": "High"},
                            {"title": "Loops and Iterations Practice", "description": "Work with for/while loops and nested iterations", "estimated_minutes": daily_mins, "priority": "Medium"}
                        ]
                    },
                    {
                        "title": "Functions & Modules",
                        "description": "Defining functions, arguments, return types, and built-in modules",
                        "tasks": [
                            {"title": "Define Functions, Parameters, and Return Values", "description": "Write modular helper utilities", "estimated_minutes": daily_mins, "priority": "High"},
                            {"title": "Explore Standard Library & Math/Random modules", "description": "Import and use datetime, os, and random", "estimated_minutes": daily_mins, "priority": "Medium"}
                        ]
                    },
                    {
                        "title": "Object-Oriented Programming (OOP)",
                        "description": "Classes, objects, methods, inheritance, and encapsulation",
                        "tasks": [
                            {"title": "Design Classes, __init__, and Instance Methods", "description": "Model real-world entities in Python classes", "estimated_minutes": daily_mins, "priority": "High"},
                            {"title": "Inheritance and Polymorphism", "description": "Build class hierarchies and method overrides", "estimated_minutes": daily_mins, "priority": "Medium"}
                        ]
                    },
                    {
                        "title": "Files & APIs",
                        "description": "File I/O, JSON handling, and making HTTP requests",
                        "tasks": [
                            {"title": "Read/Write text and JSON files", "description": "Implement persistent file operations", "estimated_minutes": daily_mins, "priority": "High"},
                            {"title": "Fetch and parse REST API data with requests", "description": "Consume external JSON endpoints", "estimated_minutes": daily_mins, "priority": "High"}
                        ]
                    },
                    {
                        "title": "Mini-Projects",
                        "description": "Hands-on application development combining core concepts",
                        "tasks": [
                            {"title": "Build a CLI Task Tracker with SQLite", "description": "Implement full CRUD operations in Python", "estimated_minutes": daily_mins, "priority": "High"},
                            {"title": "Add Unit Tests with pytest", "description": "Write automated test coverage", "estimated_minutes": daily_mins, "priority": "Medium"}
                        ]
                    },
                    {
                        "title": "Final Capstone Project",
                        "description": "End-to-end full featured application and portfolio showcase",
                        "tasks": [
                            {"title": "Architect and build Final Python Application", "description": "Complete core modules and error handling", "estimated_minutes": daily_mins, "priority": "Critical"},
                            {"title": "Write Documentation and publish to GitHub", "description": "Prepare README, license, and requirements.txt", "estimated_minutes": daily_mins, "priority": "High"}
                        ]
                    }
                ]
            }

        # 2. Fitness / Health Domain
        if "fitness" in title_lower or "run" in title_lower or "health" in title_lower or "workout" in title_lower:
            return {
                "milestones": [
                    {
                        "title": "Foundation & Baseline Conditioning",
                        "description": "Establish baseline endurance, mobility, and movement form",
                        "tasks": [
                            {"title": "Baseline Assessment: 1-mile walk/run and bodyweight test", "description": "Log initial benchmark metrics", "estimated_minutes": daily_mins, "priority": "High"},
                            {"title": "Full body mobility & core activation routine", "description": "Dynamic stretching and plank variations", "estimated_minutes": daily_mins, "priority": "Medium"}
                        ]
                    },
                    {
                        "title": "Endurance & Habit Consistency",
                        "description": "Build consistent cardiovascular and aerobic base",
                        "tasks": [
                            {"title": "Zone 2 Steady-State Cardio Session", "description": "Maintain conversational pace for 35 mins", "estimated_minutes": daily_mins, "priority": "High"},
                            {"title": "Lower Body Strength and Stability drills", "description": "Squats, lunges, and calf raises", "estimated_minutes": daily_mins, "priority": "Medium"}
                        ]
                    },
                    {
                        "title": "Strength & Performance Progression",
                        "description": "Increase resistance and workout intensity",
                        "tasks": [
                            {"title": "Upper Body & Core hypertrophy circuit", "description": "Push-ups, rows, and shoulder stability", "estimated_minutes": daily_mins, "priority": "High"},
                            {"title": "Interval Sprint & Tempo session", "description": "Alternate high intensity and active rest", "estimated_minutes": daily_mins, "priority": "High"}
                        ]
                    },
                    {
                        "title": "Target Benchmark & Milestone Review",
                        "description": "Test target endurance or weight goals",
                        "tasks": [
                            {"title": "Perform Target Distance / Reps Benchmark Test", "description": "Measure improvement against Day 1 benchmark", "estimated_minutes": daily_mins, "priority": "Critical"}
                        ]
                    }
                ]
            }

        # 3. Generic Academic / Skill Domain
        return {
            "milestones": [
                {
                    "title": "Phase 1: Foundations & Setup",
                    "description": "Core concepts, initial setup, and fundamentals",
                    "tasks": [
                        {"title": f"Gather learning materials and setup workspace for {goal['title']}", "description": "Assemble primary guides and tools", "estimated_minutes": daily_mins, "priority": "High"},
                        {"title": "Review fundamentals and key terminology", "description": "Complete introductory exercises", "estimated_minutes": daily_mins, "priority": "High"}
                    ]
                },
                {
                    "title": "Phase 2: Deep Practice & Core Modules",
                    "description": "Systematic skill acquisition and structured exercises",
                    "tasks": [
                        {"title": "Complete Module 1 exercises and take notes", "description": "Practice primary techniques", "estimated_minutes": daily_mins, "priority": "High"},
                        {"title": "Complete Module 2 applied practice session", "description": "Reinforce concepts with practical problems", "estimated_minutes": daily_mins, "priority": "Medium"}
                    ]
                },
                {
                    "title": "Phase 3: Practical Application & Project",
                    "description": "Apply skills to real-world synthesis project",
                    "tasks": [
                        {"title": "Design and execute practical application project", "description": "Produce demonstrable output", "estimated_minutes": daily_mins, "priority": "High"},
                        {"title": "Review output and address weak areas", "description": "Iterative refinement and testing", "estimated_minutes": daily_mins, "priority": "Medium"}
                    ]
                },
                {
                    "title": "Phase 4: Capstone & Mastery Verification",
                    "description": "Demonstration, assessment, and long-term maintenance",
                    "tasks": [
                        {"title": "Final project review and reflection log", "description": "Evaluate results and set maintenance cadence", "estimated_minutes": daily_mins, "priority": "Critical"}
                    ]
                }
            ]
        }

    def _format_plan_summary(self, goal: Dict[str, Any], milestones: List[Dict[str, Any]], tasks: List[Dict[str, Any]]) -> str:
        """Formats the created plan into a readable markdown response."""
        lines = [
            f"### 🎯 Goal Plan: {goal['title']}",
            f"**Constraint**: {goal['daily_time_minutes']} min/day | **Target**: {goal.get('target_date', 'Ongoing')}\n",
            "**Milestones & Initial Tasks Generated:**"
        ]
        for m in milestones:
            m_tasks = [t for t in tasks if t.get("milestone_id") == m["id"]]
            lines.append(f"\n📌 **{m['order_index']}. {m['title']}**")
            if m.get("description"):
                lines.append(f"   *{m['description']}*")
            for t in m_tasks:
                lines.append(f"   - [ ] `{t['due_date']}` {t['title']} ({t['estimated_minutes']}m)")
                
        lines.append(f"\n✨ *All {len(tasks)} tasks have been saved to your plan. You can view them on your dashboard.*")
        return "\n".join(lines)
