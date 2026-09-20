import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from backend.database import SessionLocal, init_db
from backend.models import User, Goal, Task
from agent import GoalMateAgent, AdaptiveReplanner, LLMClient
from services import goal_service, task_service, progress_service
from datetime import date, timedelta

print("1. Initializing DB for Module 3 Verification...")
init_db()
db = SessionLocal()

user = db.query(User).first()
if not user:
    from backend.auth import register_user
    user, _ = register_user(db, "Test User", "agent_test@example.com", "secretPass123")

goals = goal_service.get_goals(user.id, db=db)
goal = goals[0]
print(f"Using User {user.id} ({user.name}) and Goal {goal.id} ({goal.title})")

print("\n2. Testing AdaptiveReplanner directly...")
# Create 2 overdue tasks
t_overdue1 = task_service.create_task(goal.id, user.id, type('obj', (), {'milestone_id': None, 'title': 'Overdue Math Assignment', 'description': '', 'due_date': (date.today() - timedelta(days=2)).isoformat(), 'estimated_minutes': 60, 'priority': 'High'})(), db)
t_overdue2 = task_service.create_task(goal.id, user.id, type('obj', (), {'milestone_id': None, 'title': 'Overdue Lecture Notes', 'description': '', 'due_date': (date.today() - timedelta(days=1)).isoformat(), 'estimated_minutes': 50, 'priority': 'Medium'})(), db)

print(f"Created overdue tasks: {t_overdue1.id} ({t_overdue1.due_date}) and {t_overdue2.id} ({t_overdue2.due_date})")

replan_res = AdaptiveReplanner.replan_goal(user.id, goal.id, "College exams were hectic", db=db)
print("Replanning succeeded:", replan_res["success"])
print("Tasks rescheduled count:", replan_res["tasks_rescheduled"])
print("Tomorrow restart task:", replan_res["restart_task"])
assert replan_res["restart_task"]["minutes"] <= 45, "Tomorrow must be capped at <= 45 mins"

# Refresh DB objects
db.refresh(t_overdue1)
print(f"Updated task 1 due_date: {t_overdue1.due_date}, status: {t_overdue1.status}")
assert t_overdue1.status == "rescheduled"

print("\n3. Testing GoalMateAgent Cognitive Pipeline...")
agent = GoalMateAgent()

# Test 3a: Replan message
msg1 = "I couldn't study for the last two days because college got hectic"
resp1 = agent.process_message(msg1, user.id, db, active_goal_id=goal.id)
print("\nAgent Replan Response:\n", resp1["reply"][:200], "...")
print("Chips:", resp1["chips"])
assert "Recalibrated" in resp1["reply"] or "Tomorrow" in resp1["reply"]

# Test 3b: Resource search
msg2 = "Can you suggest some Python exercises and codewars tutorials?"
resp2 = agent.process_message(msg2, user.id, db, active_goal_id=goal.id)
print("\nAgent Resource Response:\n", resp2["reply"][:200], "...")
print("Chips:", resp2["chips"])
assert "http" in resp2["reply"] or "resource" in resp2["reply"].lower()

# Test 3c: Progress inquiry
msg3 = "How am I doing on my goals?"
resp3 = agent.process_message(msg3, user.id, db, active_goal_id=goal.id)
print("\nAgent Progress Response:\n", resp3["reply"][:200], "...")
print("Chips:", resp3["chips"])
assert "Goal Health" in resp3["reply"]

db.close()
print("\n=== ALL MODULE 3 AGENT TESTS PASSED WITH 100% SUCCESS! ===")
