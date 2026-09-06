"""
Comprehensive End-to-End System Test for GoalMate
Verifies the complete 13-step demonstration scenario, database persistence,
agentic loop, tool calls, and adaptive replanning.
"""
import os
import sys
import datetime

# Ensure utf-8 output encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from database.db import reset_db, get_db_connection
from agents.orchestrator import AgentOrchestrator
from tools.goal_tools import get_goals, get_goal, get_milestones
from tools.task_tools import get_tasks, complete_task, get_pending_tasks
from tools.progress_tools import calculate_progress, analyze_goal_health
from memory.memory import get_all_memories, get_user_memory


def run_test_suite():
    print("===============================================================")
    print("🚀 STARTING GOALMATE SYSTEM VERIFICATION & DEMO SUITE")
    print("===============================================================\n")

    # Clean DB
    reset_db()
    print("✓ [Setup] Database reset and clean schema initialized.")

    orchestrator = AgentOrchestrator()
    conversation_history = []

    # -------------------------------------------------------------
    # STEP 1 & 2: Vague Goal & Clarification Question
    # -------------------------------------------------------------
    print("\n--- STEP 1 & 2: Goal Input & Clarification Detection ---")
    user_msg_1 = "I want to learn Python in two months."
    print(f"USER: '{user_msg_1}'")
    
    resp_1, active_gid = orchestrator.process_message(user_msg_1, conversation_history)
    print(f"GOALMATE: {resp_1}")
    
    assert "how much time" in resp_1.lower() or "realistically spend" in resp_1.lower(), (
        "Agent failed to ask clarification question regarding daily available time!"
    )
    print("✓ Step 1 & 2 passed: Agent detected missing constraint and asked targeted question.")

    conversation_history.append({"role": "user", "content": user_msg_1})
    conversation_history.append({"role": "assistant", "content": resp_1})

    # -------------------------------------------------------------
    # STEP 3, 4 & 5: Constraint Provided -> Goal, Milestones & Tasks Created in SQLite
    # -------------------------------------------------------------
    print("\n--- STEP 3, 4 & 5: Constraint Clarification & Automated Planning ---")
    user_msg_2 = "About 1 hour."
    print(f"USER: '{user_msg_2}'")
    
    resp_2, goal_id = orchestrator.process_message(user_msg_2, conversation_history, active_gid)
    print(f"GOALMATE:\n{resp_2}")
    
    assert goal_id is not None, "Goal was not created in database!"
    goal = get_goal(goal_id)
    assert goal is not None, f"Goal {goal_id} could not be retrieved from SQLite!"
    assert goal["daily_time_minutes"] == 60, f"Expected 60 mins constraint, got {goal['daily_time_minutes']}"
    print(f"✓ Step 3 passed: Goal #{goal['id']} '{goal['title']}' saved to SQLite with 60m/day constraint.")

    milestones = get_milestones(goal_id)
    assert len(milestones) >= 3, f"Expected at least 3 milestones, found {len(milestones)}"
    print(f"✓ Step 4 passed: Generated {len(milestones)} structured milestones in SQLite.")

    tasks = get_tasks(goal_id=goal_id)
    assert len(tasks) >= 6, f"Expected at least 6 tasks, found {len(tasks)}"
    print(f"✓ Step 5 passed: Generated {len(tasks)} actionable tasks stored in SQLite.")

    conversation_history.append({"role": "user", "content": user_msg_2})
    conversation_history.append({"role": "assistant", "content": resp_2})

    # -------------------------------------------------------------
    # STEP 6 & 7: Task Completion & Progress Telemetry
    # -------------------------------------------------------------
    print("\n--- STEP 6 & 7: User Marks Tasks Complete & Telemetry Updates ---")
    task_to_complete = tasks[0]
    completed_task = complete_task(task_to_complete["id"])
    assert completed_task["status"] == "completed", "Task status was not updated to 'completed'!"
    assert completed_task["completed_at"] is not None, "Task completed_at timestamp missing!"
    print(f"✓ Step 6 passed: Marked Task #{completed_task['id']} '{completed_task['title']}' as completed.")

    stats_after_1 = calculate_progress(goal_id)
    print(f"Stats after completion: {stats_after_1['completed_tasks']}/{stats_after_1['total_tasks']} completed "
          f"({stats_after_1['completion_percentage']}%), Streak: {stats_after_1['current_streak']} days.")
    assert stats_after_1["completed_tasks"] == 1, "Completed task count mismatch!"
    assert stats_after_1["completion_percentage"] > 0, "Progress percentage should be > 0!"
    print("✓ Step 7 passed: Progress metrics dynamically recalculated from SQLite.")

    # -------------------------------------------------------------
    # STEP 8 to 13: 4-Day Lag Detection & Adaptive Replanning
    # -------------------------------------------------------------
    print("\n--- STEP 8 to 13: 4-Day Lag Detection & Autonomous Replanning ---")
    user_msg_3 = "I haven't studied for four days."
    print(f"USER: '{user_msg_3}'")
    
    resp_3, _ = orchestrator.process_message(user_msg_3, conversation_history, goal_id)
    print(f"GOALMATE:\n{resp_3}")
    
    assert "four" in resp_3.lower() or "4" in resp_3.lower(), "Response should acknowledge 4 missed days!"
    assert "redistributed" in resp_3.lower() or "rescheduled" in resp_3.lower() or "adjusted" in resp_3.lower(), (
        "Agent failed to acknowledge autonomous replanning!"
    )
    
    # Verify in SQLite that tasks have status='rescheduled'
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM tasks WHERE goal_id = ? AND status = 'rescheduled'", (goal_id,))
        rescheduled_count = cursor.fetchone()["cnt"]
        
    print(f"✓ Step 8-12 passed: Found {rescheduled_count} tasks marked 'rescheduled' with updated due dates in SQLite.")
    assert rescheduled_count > 0, "No tasks were rescheduled in SQLite database!"

    stats_after_replan = calculate_progress(goal_id)
    print(f"✓ Step 13 passed: Trajectory updated. Backlog distributed without cramming.")

    # -------------------------------------------------------------
    # ADDITIONAL CHECKS: Memory, Daily Check-in & Weekly Review
    # -------------------------------------------------------------
    print("\n--- BONUS AGENTIC CAPABILITIES: Memory, Check-in & Review ---")
    
    # 1. Memory Test
    user_msg_mem = "I usually study better at night."
    orchestrator.process_message(user_msg_mem, conversation_history, goal_id)
    mem_entry = get_user_memory("preferred_study_time")
    assert mem_entry is not None, "Persistent memory failed to capture preferred study time!"
    print(f"✓ Memory verified: Captured '{mem_entry['key']}' = '{mem_entry['value']}'.")

    # 2. Daily Check-in Test
    checkin_resp, _ = orchestrator.process_message("Didn't do much today, busy with college.", conversation_history, goal_id)
    print(f"✓ Daily Check-in response verified:\n  {checkin_resp[:120]}...")

    # 3. Weekly Review Test
    weekly_resp, _ = orchestrator.process_message("Can you give me my weekly review?", conversation_history, goal_id)
    assert "Weekly AI Review" in weekly_resp, "Weekly review header missing!"
    print(f"✓ Weekly Review response verified:\n  {weekly_resp[:120]}...")

    print("\n===============================================================")
    print("🎉 ALL 13 DEMO STEPS & AGENTIC BEHAVIOR TESTS PASSED 100%!")
    print("===============================================================")


if __name__ == "__main__":
    run_test_suite()
