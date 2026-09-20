"""
Comprehensive End-to-End System Test for GoalMate.
Verifies Registration, Bcrypt Hashing, JWT Auth, Multi-Tenant Isolation,
Goal Decompositions, Task Completions, Telemetry, Adaptive Replanning, and REST Endpoints.
"""
import sys
import io
import datetime
from fastapi.testclient import TestClient

# Ensure UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from app import app
from backend.database import init_db, SessionLocal
from backend.models import User, Goal, Milestone, Task, ProgressLog
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    register_user,
    authenticate_user
)
from backend.schemas import GoalCreate, MilestoneCreate, TaskCreate
from services import goal_service, task_service, progress_service, research_service
from agent import GoalMateAgent, AdaptiveReplanner

client = TestClient(app)


def test_suite():
    print("==================================================")
    print("🚀 GOALMATE COMPREHENSIVE SYSTEM VERIFICATION")
    print("==================================================")

    # 1. Database Init
    print("\n[TEST 1] Initializing Database Schema...")
    init_db()
    db = SessionLocal()
    print("✅ Database schema initialized successfully.")

    # 2. Authentication & Bcrypt Verification
    print("\n[TEST 2] Testing Password Hashing & JWT Authentication...")
    raw_pass = "SecurePass2026!"
    hashed = hash_password(raw_pass)
    assert verify_password(raw_pass, hashed), "Password verification failed"
    assert not verify_password("WrongPassword", hashed), "Invalid password incorrectly verified"
    print("✅ Bcrypt hashing and verification confirmed.")

    token = create_access_token({"sub": "99", "email": "test@domain.com", "name": "Test User"})
    payload = decode_access_token(token)
    assert payload["sub"] == "99"
    assert payload["email"] == "test@domain.com"
    print("✅ JWT creation and decoding confirmed.")

    # 3. User Registration & Multi-Tenant Isolation
    print("\n[TEST 3] Testing User Registration & Data Isolation...")
    # Unique emails for test run
    ts = int(datetime.datetime.now().timestamp())
    u1_email = f"alex_{ts}@example.com"
    u2_email = f"sam_{ts}@example.com"

    user1, token1 = register_user(db, "Alex Rivera", u1_email, "password123")
    user2, token2 = register_user(db, "Sam Smith", u2_email, "password123")
    print(f"✅ User 1 (ID: {user1.id}, Email: {user1.email}) and User 2 (ID: {user2.id}, Email: {user2.email}) registered.")

    # Each user gets a default demo goal seeded
    u1_goals = goal_service.get_goals(user1.id, db=db)
    u2_goals = goal_service.get_goals(user2.id, db=db)
    assert len(u1_goals) >= 1, "User 1 should have seeded demo goal"
    assert len(u2_goals) >= 1, "User 2 should have seeded demo goal"
    assert u1_goals[0].id != u2_goals[0].id, "Users must not share goal IDs"

    # Verify User 2 cannot access User 1 goal
    u2_access_u1_goal = goal_service.get_goal(u1_goals[0].id, user_id=user2.id, db=db)
    assert u2_access_u1_goal is None, "Multi-tenant violation: User 2 accessed User 1 goal"
    print("✅ Multi-tenant data isolation strictly enforced.")

    # 4. Task Completion & Telemetry Tracking
    print("\n[TEST 4] Testing Task Completion and Telemetry Updates...")
    u1_today_tasks = task_service.get_today_tasks(user1.id, goal_id=u1_goals[0].id, db=db)
    assert len(u1_today_tasks) > 0, "User 1 should have today's tasks"
    target_task = u1_today_tasks[0]
    
    completed_task = task_service.complete_task(target_task.id, user1.id, db=db)
    assert completed_task.status == "completed"
    assert completed_task.completed_at is not None

    stats = progress_service.calculate_progress(user1.id, u1_goals[0].id, db=db)
    assert stats["completed_tasks"] >= 1
    assert stats["current_streak"] >= 1
    print(f"✅ Task completion confirmed. Current streak: {stats['current_streak']} days, Completion: {stats['completion_percentage']}%.")

    # 5. Adaptive Replanning Engine (2-Day Slip Simulation)
    print("\n[TEST 5] Testing Adaptive Replanning (Smoothing Backlog without Cramming)...")
    today = datetime.date.today()
    # Simulate 2 overdue tasks from 2 days ago and 1 day ago
    t_slip1 = task_service.create_task(
        u1_goals[0].id, user1.id,
        TaskCreate(title="Slipped Assignment A", due_date=(today - datetime.timedelta(days=2)).isoformat(), estimated_minutes=60, priority="High"),
        db=db
    )
    t_slip2 = task_service.create_task(
        u1_goals[0].id, user1.id,
        TaskCreate(title="Slipped Assignment B", due_date=(today - datetime.timedelta(days=1)).isoformat(), estimated_minutes=50, priority="Medium"),
        db=db
    )

    replan_result = AdaptiveReplanner.replan_goal(
        user_id=user1.id,
        goal_id=u1_goals[0].id,
        user_reason="College crunch and exam preparation",
        db=db
    )
    assert replan_result["success"] is True
    assert replan_result["tasks_rescheduled"] >= 2
    assert replan_result["restart_task"]["minutes"] <= 45, "Tomorrow's workload must be capped at <= 45 minutes"

    # Verify SQLite persistence of new schedule
    db.refresh(t_slip1)
    tomorrow_str = (today + datetime.timedelta(days=1)).isoformat()
    assert t_slip1.status == "rescheduled"
    assert t_slip1.due_date == tomorrow_str
    print(f"✅ Adaptive replanning confirmed. Tomorrow restart task '{t_slip1.title}' capped at {t_slip1.estimated_minutes}m.")

    # 6. Web Research Service (Tavily or Curated Fallback)
    print("\n[TEST 6] Testing Web Research Service...")
    research_out = research_service.search_resources("Python OOP clean architecture", max_results=2)
    assert "results" in research_out
    assert len(research_out["results"]) > 0
    print(f"✅ Research service verified (Source: {research_out.get('source')}, Found {len(research_out['results'])} items).")

    # 7. AI Goal Coach Orchestrator
    print("\n[TEST 7] Testing GoalMateAgent Cognitive Flow...")
    agent = GoalMateAgent()
    replan_chat = agent.process_message(
        "I couldn't study for the last two days because college got hectic",
        user1.id,
        db=db,
        active_goal_id=u1_goals[0].id
    )
    assert "Recalibrated" in replan_chat["reply"] or "Tomorrow" in replan_chat["reply"] or "schedule" in replan_chat["reply"].lower()
    assert len(replan_chat["chips"]) >= 2
    print(f"✅ Agent conversation pipeline verified. Suggested chips: {replan_chat['chips']}")

    # 8. FastAPI REST Endpoints via TestClient
    print("\n[TEST 8] Testing FastAPI REST Endpoints...")
    # Login endpoint
    login_resp = client.post("/api/auth/login", json={"email": u1_email, "password": "password123"})
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    api_token = login_resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {api_token}"}
    
    # List goals endpoint
    goals_resp = client.get("/api/goals", headers=headers)
    assert goals_resp.status_code == 200
    assert len(goals_resp.json()) >= 1

    # Progress endpoint
    prog_resp = client.get("/api/progress", headers=headers)
    assert prog_resp.status_code == 200
    assert "completion_percentage" in prog_resp.json()
    print("✅ FastAPI REST endpoints (/api/auth/login, /api/goals, /api/progress) working cleanly.")

    db.close()
    print("\n==================================================")
    print("🎉 ALL 8 SYSTEM TEST MODULES PASSED WITH 100% SUCCESS!")
    print("==================================================")


if __name__ == "__main__":
    test_suite()
