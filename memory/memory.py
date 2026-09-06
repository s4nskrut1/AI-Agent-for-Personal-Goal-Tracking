"""
Persistent Memory Manager for GoalMate.
Stores and retrieves user habits, constraints, preferred study times, and goals context.
Persists across sessions via SQLite.
"""
import re
import datetime
from typing import Optional, List, Dict, Any
from database.db import get_db_connection


def save_user_memory(key: str, value: str, category: str = "general", db_path: Optional[str] = None) -> bool:
    """Saves or updates a memory key-value pair in SQLite."""
    now_str = datetime.datetime.now().isoformat()
    clean_key = key.strip().lower().replace(" ", "_")
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO user_memories (key, value, category, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    category = excluded.category,
                    updated_at = excluded.updated_at
                """,
                (clean_key, value.strip(), category, now_str, now_str)
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"[Memory Error] Could not save memory {key}: {e}")
        return False


def get_user_memory(key: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves a single memory record by key."""
    clean_key = key.strip().lower().replace(" ", "_")
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_memories WHERE key = ?", (clean_key,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_memories(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all stored user memories ordered by update time."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_memories ORDER BY updated_at DESC")
        return [dict(row) for row in cursor.fetchall()]


def delete_user_memory(key: str, db_path: Optional[str] = None) -> bool:
    """Deletes a memory record by key."""
    clean_key = key.strip().lower().replace(" ", "_")
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_memories WHERE key = ?", (clean_key,))
        conn.commit()
        return cursor.rowcount > 0


def get_memory_context_string(db_path: Optional[str] = None) -> str:
    """
    Formats all user memories into a compact markdown summary for LLM prompt context.
    """
    memories = get_all_memories(db_path)
    if not memories:
        return "No specific user preferences or past constraints recorded yet."
    
    lines = ["Stored User Preferences & Constraints:"]
    for mem in memories:
        lines.append(f"- **{mem['key']}** ({mem['category']}): {mem['value']}")
    return "\n".join(lines)


def detect_and_save_preferences(user_message: str, db_path: Optional[str] = None) -> List[str]:
    """
    Scans user input for explicit preferences or constraints and persists them.
    Returns list of discovered memory keys.
    """
    text = user_message.lower()
    discovered = []
    
    # 1. Preferred study / work time
    if any(phrase in text for phrase in ["study better at night", "study at night", "prefer night", "work at night", "night owl"]):
        save_user_memory("preferred_study_time", "Prefers studying at night (night owl)", category="preference", db_path=db_path)
        discovered.append("preferred_study_time")
    elif any(phrase in text for phrase in ["study in morning", "early morning", "prefer morning", "morning person"]):
        save_user_memory("preferred_study_time", "Prefers early morning sessions", category="preference", db_path=db_path)
        discovered.append("preferred_study_time")
    elif "evening" in text:
        save_user_memory("preferred_study_time", "Prefers evening study sessions", category="preference", db_path=db_path)
        discovered.append("preferred_study_time")

    # 2. Available daily time constraint
    # Matches patterns like "1 hour a day", "30 mins per day", "2 hours each day", "45 minutes"
    time_match = re.search(r'(\d+)\s*(hour|hr|minute|min|m)s?(\s*(a|per|each)?\s*day)?', text)
    if time_match:
        qty = int(time_match.group(1))
        unit = time_match.group(2)
        total_mins = qty * 60 if "h" in unit else qty
        if 10 <= total_mins <= 600:
            save_user_memory("daily_available_time", f"{total_mins} minutes per day ({qty} {unit}s)", category="constraint", db_path=db_path)
            discovered.append("daily_available_time")

    # 3. Learning style or pace
    if "beginner" in text or "start from scratch" in text:
        save_user_memory("experience_level", "Beginner / Starting from scratch", category="profile", db_path=db_path)
        discovered.append("experience_level")
    elif "intermediate" in text or "already know basics" in text:
        save_user_memory("experience_level", "Intermediate with basic background", category="profile", db_path=db_path)
        discovered.append("experience_level")
        
    return discovered
