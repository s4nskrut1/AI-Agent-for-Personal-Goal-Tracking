"""
Goal Agent for GoalMate.
Understands user goals, asks targeted clarification questions for vague objectives,
extracts realistic constraints, and creates structured goal entities.
"""
import re
import json
import datetime
from typing import Dict, Any, Tuple, Optional

from tools.goal_tools import create_goal, get_goals
from memory.memory import get_all_memories, save_user_memory
from agents.llm_client import llm_client


class GoalAgent:
    """Specialized agent responsible for goal clarification, structuring, and persistence."""

    def __init__(self):
        pass

    def evaluate_goal_completeness(self, user_message: str, conversation_history: list) -> Tuple[bool, str]:
        """
        Determines if the goal statement is specific enough to plan, or needs clarification.
        Returns: (is_complete, clarification_question_or_empty)
        """
        text = user_message.lower().strip()
        
        # Check if conversation history already asked for daily time or specifics and this is the answer
        has_time_in_message = bool(re.search(r'(\d+)\s*(hour|hr|min|minute)s?', text))
        has_time_in_history = False
        for msg in conversation_history[-3:]:
            if "how much time" in msg.get("content", "").lower():
                has_time_in_history = True
                break

        # Check if user says "just create a plan" or "skip"
        if any(term in text for term in ["just create a plan", "skip", "default", "go ahead"]):
            return True, ""

        # Case 1: Extremely vague goal (e.g. "I want to get better at fitness", "get healthy", "learn coding")
        if any(term in text for term in ["get better at fitness", "get fit", "get healthy", "improve health"]):
            return False, (
                "That's an awesome commitment! 🎯 To tailor the right plan for you, what would success look like "
                "— improving strength, losing weight, running a 5K, or simply exercising consistently?"
            )
            
        if text in ["i want to code", "learn programming", "get into tech"]:
            return False, (
                "Fantastic! Which programming language or domain would you like to start with "
                "(e.g., Python for AI/Data, JavaScript for Web Development), and do you have any prior coding experience?"
            )

        # Case 2: Goal statement has goal & duration (e.g. "I want to become internship-ready in Python in 3 months") but missing daily time constraint
        has_duration = bool(re.search(r'(\d+)\s*(month|week|day)s?', text))
        has_python_or_study = any(k in text for k in ["python", "internship", "ai", "machine learning", "guitar", "read", "study", "exam", "course"])
        
        if (has_duration or has_python_or_study) and not has_time_in_message and not has_time_in_history:
            # Check user memories if daily_available_time is already remembered
            memories = {m["key"]: m["value"] for m in get_all_memories()}
            if "daily_available_time" not in memories:
                return False, (
                    "That's an amazing goal! 🚀\n\n"
                    "To create the best plan for you, I'll need a few details:\n"
                    "1. **What's your current level?** (Beginner / Some knowledge / Intermediate)\n"
                    "2. **How much time can you dedicate per day or per week?**\n"
                    "3. **Do you have any specific areas you want to focus on?** (e.g., Data Science, Web Dev, Projects)\n\n"
                    "Once I have this, I'll create a personalized roadmap for you!"
                )

        return True, ""


    def extract_goal_parameters(self, user_message: str, conversation_history: list) -> Dict[str, Any]:
        """
        Extracts structured goal parameters from user message and prior context using LLM or heuristic.
        """
        # Combine last turns for context
        full_context = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in conversation_history[-4:]])
        full_context += f"\nCurrent user message: {user_message}"
        
        # Try LLM first
        prompt = f"""
        Extract the personal goal details from the following conversation context into structured JSON:
        Context:
        {full_context}

        Requirements:
        Return JSON with these exact keys:
        - "title": Concise goal name (e.g., "Learn Python Fundamentals", "5K Running Routine")
        - "description": 1-2 sentence description including motivation
        - "category": One of "Education", "Fitness", "Career", "Personal", "Creative"
        - "duration_weeks": integer number of weeks (default 8 if not specified)
        - "daily_time_minutes": integer minutes available per day (default 60 if not specified)
        - "priority": "High", "Medium", or "Low"
        - "preferred_schedule": "morning", "evening", or "flexible"
        """
        
        try:
            raw_json = llm_client.generate_response(prompt, json_mode=True)
            # Clean markdown fences if any
            clean_str = re.sub(r'```(?:json)?\s*|\s*```', '', raw_json).strip()
            data = json.loads(clean_str)
            return data
        except Exception:
            # Deterministic Heuristic Extraction
            return self._heuristic_extract(user_message, conversation_history)

    def _heuristic_extract(self, user_message: str, conversation_history: list) -> Dict[str, Any]:
        """Robust offline regex-based parameter extraction."""
        combined_text = " ".join([m.get("content", "") for m in conversation_history[-3:]] + [user_message]).lower()
        
        # Title extraction
        title = "Personal Growth Goal"
        category = "General"
        
        if "python" in combined_text:
            title = "Learn Python Programming"
            category = "Education"
        elif "fitness" in combined_text or "workout" in combined_text or "exercise" in combined_text:
            title = "Fitness & Health Routine"
            category = "Fitness"
        elif "guitar" in combined_text or "music" in combined_text:
            title = "Learn Acoustic Guitar"
            category = "Creative"
        elif "read" in combined_text or "book" in combined_text:
            title = "Consistent Reading Habit"
            category = "Personal"
            
        # Duration extraction
        duration_weeks = 8 # default 2 months
        weeks_match = re.search(r'(\d+)\s*(week|wk)s?', combined_text)
        months_match = re.search(r'(\d+)\s*(month|mo)s?', combined_text)
        days_match = re.search(r'(\d+)\s*(day)s?', combined_text)
        
        if weeks_match:
            duration_weeks = int(weeks_match.group(1))
        elif months_match:
            duration_weeks = int(months_match.group(1)) * 4
        elif days_match:
            duration_weeks = max(1, int(days_match.group(1)) // 7)

        # Daily time extraction (e.g., "1 hour", "30 mins", "45 minutes")
        daily_time_minutes = 60
        hour_match = re.search(r'(\d+)\s*(hour|hr)s?', combined_text)
        min_match = re.search(r'(\d+)\s*(minute|min)s?', combined_text)
        if hour_match:
            daily_time_minutes = int(hour_match.group(1)) * 60
        elif min_match:
            daily_time_minutes = int(min_match.group(1))
            
        # Preferred schedule
        pref_schedule = "flexible"
        if "night" in combined_text or "evening" in combined_text:
            pref_schedule = "evening"
        elif "morning" in combined_text:
            pref_schedule = "morning"

        return {
            "title": title,
            "description": f"Structured plan for {title} spanning {duration_weeks} weeks with {daily_time_minutes} min/day sessions.",
            "category": category,
            "duration_weeks": duration_weeks,
            "daily_time_minutes": daily_time_minutes,
            "priority": "High",
            "preferred_schedule": pref_schedule
        }

    def process(self, user_message: str, conversation_history: list) -> Tuple[str, Optional[int]]:
        """
        Executes the goal agent loop:
        1. Checks completeness / clarification.
        2. If clarified, creates goal in SQLite and saves user constraints to memory.
        Returns: (response_text, created_goal_id_or_none)
        """
        is_complete, clarification = self.evaluate_goal_completeness(user_message, conversation_history)
        if not is_complete:
            return clarification, None
            
        params = self.extract_goal_parameters(user_message, conversation_history)
        
        # Compute target date
        weeks = params.get("duration_weeks", 8)
        target_date = (datetime.date.today() + datetime.timedelta(weeks=weeks)).isoformat()
        
        # Create in SQLite via tool
        goal = create_goal(
            title=params["title"],
            description=params["description"],
            category=params["category"],
            target_date=target_date,
            priority=params.get("priority", "High"),
            daily_time_minutes=params.get("daily_time_minutes", 60),
            preferred_schedule=params.get("preferred_schedule", "flexible")
        )
        
        # Save memory
        daily_time_str = f"{params['daily_time_minutes']} minutes/day"
        save_user_memory("daily_available_time", daily_time_str, category="constraint")
        
        return (
            f"Perfect. I've created an {weeks}-week plan with **{params['daily_time_minutes']} min/day** as your constraint.",
            goal["id"]
        )
