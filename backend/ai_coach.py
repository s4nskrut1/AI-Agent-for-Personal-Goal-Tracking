import os
import json
import logging
import requests
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("goalmate-coach")

def load_env_file():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and not os.environ.get(k):
                            os.environ[k] = v
        except Exception as e:
            logger.warning(f"Error reading .env file: {e}")

load_env_file()

def build_coach_system_instruction(user_name: str, context: Dict[str, Any]) -> str:
    goals = context.get("goals", [])
    tasks = context.get("tasks", [])
    streaks = context.get("streaks", {})

    goals_summary = []
    for g in goals:
        progress = g.get("progress", 0)
        milestones = g.get("milestones", [])
        completed_m = sum(1 for m in milestones if m.get("completed"))
        goals_summary.append(f"- '{g.get('title')}' ({g.get('category', 'General')}): {progress}% done, {completed_m}/{len(milestones)} milestones completed.")

    tasks_today = [t for t in tasks if t.get("isToday", True)]
    completed_tasks = [t for t in tasks_today if t.get("completed")]
    pending_tasks = [t for t in tasks_today if not t.get("completed")]

    return f"""You are the GoalMate AI Coach — inspired by the energetic, disciplined, and passionate spirit of Shoyo Hinata (Haikyuu).
Your motto is: "Small steps. Big dreams." and "Progress isn't about being perfect, it's about showing up."

You are coaching {user_name}.
Current GoalMate State:
- Current Streak: {streaks.get('currentStreak', 0)} days
- Weekly Progress: {streaks.get('weeklyProgress', 0)}%
- Active Goals:
{chr(10).join(goals_summary) if goals_summary else "No active goals yet."}

- Today's Tasks ({len(tasks_today)} total):
  * Completed ({len(completed_tasks)}): {', '.join([t.get('title') for t in completed_tasks]) if completed_tasks else 'None yet'}
  * Remaining ({len(pending_tasks)}): {', '.join([f"{t.get('title')} ({t.get('category')}, {t.get('duration', '30m')})" for t in pending_tasks]) if pending_tasks else 'All done!'}

Your Coaching Persona:
1. Warm, encouraging, high-energy, actionable, and grounded in anime sports discipline.
2. Directly reference their actual goals and tasks! Celebrate what they've already checked off today, and suggest practical small next steps for what is pending.
3. Keep answers concise, punchy, and structured with bullet points or emoji callouts. Avoid lengthy corporate essays.
4. Give concrete study/work techniques (e.g., Pomodoro 45m focus, break big tasks into 15m chunks, morning momentum).
5. If they ask for a plan, schedule, or tips, craft it tailored to their actual goals and remaining tasks!
"""

def generate_coach_response(message: str, user_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
    load_env_file()
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    # Fast direct Google Gemini API call with high-reliability models
    if api_key:
        system_instruction = build_coach_system_instruction(user_name, context)
        full_prompt = f"{system_instruction}\n\nUser Message: {message}"

        # Try gemini-3.5-flash-lite first (fastest, high quota, <1s response time), then gemini-3.5-flash, then gemini-flash-latest
        models_to_try = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-latest"]
        
        for model_name in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                payload = {
                    "contents": [{
                        "parts": [{"text": full_prompt}]
                    }]
                }
                resp = requests.post(url, json=payload, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            return {
                                "reply": parts[0]["text"].strip(),
                                "provider": "gemini",
                                "model": model_name,
                                "has_api_key": True,
                                "success": True
                            }
                else:
                    logger.warning(f"Model {model_name} returned {resp.status_code}: {resp.text[:120]}")
            except Exception as e:
                logger.warning(f"Model {model_name} call error: {e}")

    # Smart local contextual fallback coach
    return generate_smart_fallback(message, user_name, context)

def generate_smart_fallback(message: str, user_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
    msg_lower = message.lower()
    goals = context.get("goals", [])
    tasks = context.get("tasks", [])
    streaks = context.get("streaks", {})
    curr_streak = streaks.get("currentStreak", 0)

    completed_tasks = [t for t in tasks if t.get("completed")]
    pending_tasks = [t for t in tasks if not t.get("completed")]
    first_pending = pending_tasks[0].get("title") if pending_tasks else None
    first_goal = goals[0].get("title") if goals else None

    if "unmotivated" in msg_lower or "tired" in msg_lower or "lazy" in msg_lower:
        reply = (
            f"Hey {user_name}! 👋\n\n"
            f"That's completely normal. Remember: *\"Progress isn't about being perfect, it's about showing up.\"*\n\n"
        )
        if first_pending:
            reply += f"You don't have to conquer the whole mountain today. Just tackle **'{first_pending}'** for 15 minutes. Once you start, momentum takes over! 🏐✨"
        else:
            reply += f"Take a deep breath! Pick one small thing, write it down as a task, and let's conquer it together!"

    elif "plan" in msg_lower or "schedule" in msg_lower or "day" in msg_lower:
        reply = (
            f"Here is your high-energy battle plan for today, {user_name}! 📋⚡\n\n"
        )
        if pending_tasks:
            reply += "**Recommended Action Order:**\n"
            for i, t in enumerate(pending_tasks[:3], 1):
                reply += f"{i}. **{t.get('title')}** `[{t.get('category', 'Task')}]` — *{t.get('duration', '30 min')}*\n"
            reply += "\n💡 *Pro-Tip:* Start right now with 25 minutes of zero-distraction focus!"
        elif first_goal:
            reply += f"You have no tasks logged today for **{first_goal}**! Let's add 2 quick 30-minute tasks to build momentum."
        else:
            reply += "You don't have any active goals or tasks yet! Click **'+ Add Goal'** on the left or tell me what you want to achieve, and I'll build a roadmap for you!"

    elif "tips" in msg_lower or "advice" in msg_lower:
        reply = (
            f"Here are 3 champion habits to kickstart your momentum, {user_name}:\n\n"
            f"1. **The 2-Minute Warmup**: Never think 'I have to study for 4 hours'. Just promise yourself 2 minutes of opening the work.\n"
            f"2. **Retroactive Consistency**: If you forget to log a day, edit it in your GoalMate history so your streak stays true and honest.\n"
            f"3. **Volleyball Spike Mentality**: Hit one task cleanly before thinking about the next set! 🏐"
        )
    else:
        reply = (
            f"Hey {user_name}! 🌟\n\n"
            f"I'm right here in your corner. What are we tackling next — want me to plan your day, break down a goal, or provide study tips?"
        )

    has_api_key = bool(os.environ.get("GEMINI_API_KEY"))
    return {
        "reply": reply,
        "provider": "gemini" if has_api_key else "simulated_coach",
        "model": "goalmate-coach-v1",
        "has_api_key": has_api_key,
        "success": True
    }
