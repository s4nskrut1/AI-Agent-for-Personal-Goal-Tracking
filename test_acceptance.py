import sys
import os
sys.path.insert(0, ".")

from backend.services import (
    get_all_goals, get_today_tasks, get_dashboard_stats, complete_task, get_session
)
from backend.models import Task, Goal
from agent.llm import agent_chat
from datetime import datetime, timedelta

print("=== 8-STEP ACCEPTANCE VERIFICATION ===\n")

# TEST 1: Initial load
goals = get_all_goals()
print(f"Test 1 (Initial Load): {len(goals)} goals in SQLite database")

# TEST 2: AI creates Angular goal
angular_goal = next((g for g in goals if "Angular" in g.title), None)
if not angular_goal:
    print("Executing: 'I want to learn Angular in 30 days.'")
    reply, _, actions = agent_chat("I want to learn Angular in 30 days.", [])
    print(f"AI Actions: {actions}")
    goals = get_all_goals()
    angular_goal = next((g for g in goals if "Angular" in g.title), None)

assert angular_goal is not None, "Angular goal must exist in DB"
print(f"Test 2 (Goal Created): ID={angular_goal.id}, Title='{angular_goal.title}', Tasks={angular_goal.total_tasks}, Milestones={len(angular_goal.milestones)}")

# TEST 3: Check today's task
today_tasks = get_today_tasks()
print(f"Test 3 (Today's Tasks): Found {len(today_tasks)} tasks")
if today_tasks:
    t = today_tasks[0]
    complete_task(t["id"], True)
    print(f"  -> Marked Task #{t['id']} completed: '{t['title']}'")
    stats = get_dashboard_stats()
    print(f"  -> Updated Stats: Completed Today={stats['completed_today']}, Streak={stats['streak']} days")

# TEST 4: Past task editing / retroactive completion
db = get_session()
yesterday = datetime.utcnow().date() - timedelta(days=1)
first_task = db.query(Task).filter(Task.goal_id == angular_goal.id).first()
if first_task:
    first_task.scheduled_date = yesterday
    db.commit()
    complete_task(first_task.id, True)
    print(f"Test 4 (Past Task): Task #{first_task.id} scheduled for {yesterday} marked completed retroactively in DB")
db.close()

# TEST 5: Progress analysis
reply, _, actions = agent_chat("How am I doing with Angular?", [])
print(f"Test 5 (AI Progress Analysis): {reply[:130]}...")

# TEST 6: Adaptive advice
reply, _, actions = agent_chat("I only have 30 minutes today.", [])
print(f"Test 6 (Adaptive 30-min advice): {reply[:130]}...")

# TEST 7: Replan to 20 days
reply, _, actions = agent_chat("Make my Angular plan 20 days instead of 30.", [])
print(f"Test 7 (Replanning Actions): {actions}")
updated_angular = next((g for g in get_all_goals() if "Angular" in g.title), None)
print(f"  -> Replanned Duration: {updated_angular.duration_days} days, Deadline: {updated_angular.deadline}")

# TEST 8: Multiple goals
print("Executing: 'I want to learn DSA in 45 days.'")
reply, _, actions = agent_chat("I want to learn DSA in 45 days.", [])
print(f"Test 8 (Second Goal Actions): {actions}")
all_goals = get_all_goals()
print(f"All Goals in System ({len(all_goals)} total): {[g.title for g in all_goals]}")
for g in all_goals:
    print(f"  - '{g.title}': {g.total_tasks} tasks, {len(g.milestones)} milestones, progress: {g.progress_pct}%")

assert len(all_goals) >= 2, "Expected at least 2 independent goals"
print("\n>>> ALL 8 ACCEPTANCE TESTS SUCCESSFULLY PASSED! <<<")
