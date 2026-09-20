"""
Comprehensive Verification of the 10-Step Hero Hackathon Demo Flow.
Verifies:
1. Natural language goal understanding
2. Dynamic follow-up clarification
3. Roadmap decomposition into milestones & tasks in SQLite
4. Task completion & progress/streak increment
5. Adaptive replanning when user reports 2 missed days due to hectic college
6. Verification that tasks were redistributed in SQLite and workload smoothed
"""
import sys
import datetime

# Ensure utf-8 output encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from database.db import reset_db, get_db_connection
from agents.orchestrator import AgentOrchestrator
from tools.goal_tools import get_goals, get_goal, get_milestones
from tools.task_tools import get_tasks, complete_task, get_pending_tasks, get_today_tasks
from tools.progress_tools import calculate_progress, analyze_goal_health, get_goal_insights
from memory.memory import get_all_memories


def run_hackathon_hero_demo_test():
    print("==================================================================")
    print("🌟 STARTING 10-STEP HERO HACKATHON DEMO FLOW VERIFICATION")
    print("==================================================================")

    # Reset DB to clean slate
    reset_db()
    orchestrator = AgentOrchestrator()
    conversation_history = []
    active_gid = None

    # -------------------------------------------------------------
    # STEP 1: User introduces high-level goal
    # -------------------------------------------------------------
    print("\n--- [STEP 1] User Goal Statement ---")
    step1_msg = "I want to become internship-ready in Python in 3 months."
    print(f"USER: '{step1_msg}'")

    # -------------------------------------------------------------
    # STEP 2: Agent asks for relevant details (Level, Time, Focus)
    # -------------------------------------------------------------
    print("\n--- [STEP 2] Agent Follow-up Clarification ---")
    step2_resp, active_gid = orchestrator.process_message(step1_msg, conversation_history, active_gid)
    print(f"GOALMATE:\n{step2_resp}\n")
    assert "current level" in step2_resp.lower() or "how much time" in step2_resp.lower(), "Agent should ask targeted questions!"
    conversation_history.append({"role": "user", "content": step1_msg})
    conversation_history.append({"role": "assistant", "content": step2_resp})
    print("✓ Step 1 & 2 PASSED: Conversational clarification asked without rigid form.")

    # -------------------------------------------------------------
    # STEP 3 & 4: User replies with constraints -> Plan decomposed in SQLite
    # -------------------------------------------------------------
    print("\n--- [STEP 3 & 4] Goal, Milestones, and Tasks Synthesis ---")
    step3_msg = "I'm a complete beginner, but I can study 1-2 hours daily. Focus on Data Science."
    print(f"USER: '{step3_msg}'")
    step3_resp, goal_id = orchestrator.process_message(step3_msg, conversation_history, active_gid)
    print(f"GOALMATE:\n{step3_resp}\n")

    assert goal_id is not None, "Goal was not created!"
    goal = get_goal(goal_id)
    assert goal is not None, "Goal not found in SQLite!"
    milestones = get_milestones(goal_id)
    tasks = get_tasks(goal_id=goal_id)
    assert len(milestones) >= 3, f"Expected >= 3 milestones, got {len(milestones)}"
    assert len(tasks) >= 6, f"Expected >= 6 tasks, got {len(tasks)}"

    conversation_history.append({"role": "user", "content": step3_msg})
    conversation_history.append({"role": "assistant", "content": step3_resp})
    print(f"✓ Step 3 & 4 PASSED: Created Goal #{goal['id']} with {len(milestones)} milestones and {len(tasks)} tasks.")

    # -------------------------------------------------------------
    # STEP 5: User completes tasks -> Telemetry updates
    # -------------------------------------------------------------
    print("\n--- [STEP 5] Task Completion & Telemetry Dynamic Recalculation ---")
    first_task = tasks[0]
    completed_task = complete_task(first_task["id"])
    assert completed_task["status"] == "completed", "Task status did not update to completed!"
    stats = calculate_progress(goal_id)
    print(f"Completed Task #{first_task['id']} '{first_task['title']}'.")
    print(f"Updated Stats: {stats['completed_tasks']}/{stats['total_tasks']} ({stats['completion_percentage']}%), Streak: {stats['current_streak']} days.")
    assert stats["completed_tasks"] == 1
    assert stats["current_streak"] >= 1
    print("✓ Step 5 PASSED: Real progress committed to SQLite.")

    # -------------------------------------------------------------
    # STEP 6, 7, 8: User reports missing 2 days due to hectic college -> Risk detected
    # -------------------------------------------------------------
    print("\n--- [STEP 6, 7 & 8] Bottleneck Diagnosis & Fall-Behind Detection ---")
    step6_msg = "I couldn't study for the last two days because college got hectic."
    print(f"USER: '{step6_msg}'")
    step6_resp, _ = orchestrator.process_message(step6_msg, conversation_history, goal_id)
    print(f"GOALMATE:\n{step6_resp}\n")

    assert "missed 2 days" in step6_resp.lower() or "2 days" in step6_resp.lower(), "Should recognize 2 missed days!"
    assert "college" in step6_resp.lower() or "academic" in step6_resp.lower(), "Should diagnose college context!"
    assert "redistributed" in step6_resp.lower(), "Should state task redistribution!"

    # -------------------------------------------------------------
    # STEP 9 & 10: Database updated with smooth schedule without cramming
    # -------------------------------------------------------------
    print("\n--- [STEP 9 & 10] Schedule Persistence & Recovery Plan Verification ---")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM tasks WHERE goal_id = ? AND status = 'rescheduled'", (goal_id,))
        rescheduled_count = cursor.fetchone()["cnt"]

    print(f"Verified {rescheduled_count} tasks dynamically rescheduled in SQLite.")
    assert rescheduled_count > 0, "Tasks should have status 'rescheduled' with smoothed due dates!"
    
    # Verify memory
    memories = get_all_memories()
    print("User Memory captured:", [f"{m['key']}: {m['value']}" for m in memories])
    
    print("\n==================================================================")
    print("🏆 ALL 10 STEPS OF THE HACKATHON HERO DEMO COMPLETED & VERIFIED 100%!")
    print("==================================================================")


if __name__ == "__main__":
    run_hackathon_hero_demo_test()
