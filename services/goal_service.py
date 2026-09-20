"""
Goal and Milestone Service for GoalMate.
Encapsulates CRUD operations with strict user_id isolation.
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.models import Goal, Milestone, Task, User, ProgressLog
from backend.schemas import GoalCreate, GoalUpdate, MilestoneCreate


def create_goal(user_id: int, data: GoalCreate, db: Session) -> Goal:
    """Creates a new goal isolated to the authenticated user."""
    target_d = data.target_date
    if not target_d:
        target_d = (date.today() + timedelta(days=60)).isoformat()

    goal = Goal(
        user_id=user_id,
        title=data.title.strip(),
        description=(data.description or "").strip(),
        category=data.category,
        target_date=target_d,
        priority=data.priority,
        daily_time_minutes=data.daily_time_minutes,
        preferred_schedule=data.preferred_schedule,
        status="active"
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def get_goals(user_id: int, status: Optional[str] = None, db: Session = None) -> List[Goal]:
    """Retrieves all goals belonging strictly to user_id."""
    query = db.query(Goal).filter(Goal.user_id == user_id)
    if status:
        query = query.filter(Goal.status == status)
    return query.order_by(Goal.id.desc()).all()


def get_goal(goal_id: int, user_id: int, db: Session) -> Optional[Goal]:
    """Retrieves a specific goal ensuring user ownership."""
    return db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()


def update_goal(goal_id: int, user_id: int, updates: Dict[str, Any], db: Session) -> Optional[Goal]:
    """Updates goal fields if owned by user."""
    goal = get_goal(goal_id, user_id, db)
    if not goal:
        return None
    for key, value in updates.items():
        if hasattr(goal, key) and value is not None and key not in ["id", "user_id"]:
            setattr(goal, key, value)
    db.commit()
    db.refresh(goal)
    return goal


def delete_goal(goal_id: int, user_id: int, db: Session) -> bool:
    """Deletes a goal cascading to child milestones and tasks."""
    goal = get_goal(goal_id, user_id, db)
    if not goal:
        return False
    db.delete(goal)
    db.commit()
    return True


def create_milestone(goal_id: int, user_id: int, data: MilestoneCreate, db: Session) -> Optional[Milestone]:
    """Creates a milestone under a user-owned goal."""
    goal = get_goal(goal_id, user_id, db)
    if not goal:
        return None
    milestone = Milestone(
        goal_id=goal_id,
        title=data.title.strip(),
        description=(data.description or "").strip(),
        order_index=data.order_index,
        target_date=data.target_date,
        status="pending"
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


def get_milestones(goal_id: int, user_id: int, db: Session) -> List[Milestone]:
    """Retrieves all milestones for a user's goal ordered by sequence index."""
    goal = get_goal(goal_id, user_id, db)
    if not goal:
        return []
    return db.query(Milestone).filter(Milestone.goal_id == goal_id).order_by(Milestone.order_index.asc()).all()


def seed_default_demo_goal(user_id: int, db: Session) -> Goal:
    """Seeds the demo Python goal if the user has no existing goals."""
    existing = get_goals(user_id, db=db)
    if existing:
        return existing[0]

    today = date.today()
    target_d = (today + timedelta(days=68)).isoformat()
    goal = Goal(
        user_id=user_id,
        title="Become internship-ready in Python",
        description="Master Python fundamentals, OOP, APIs, and data structures for technical interviews.",
        category="Education",
        target_date=target_d,
        priority="High",
        daily_time_minutes=60,
        preferred_schedule="evening",
        status="active"
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)

    milestones_data = [
        ("Python Fundamentals", "Syntax, variables, conditionals, and loops", 1, (today + timedelta(days=14)).isoformat(), "completed"),
        ("Functions & Modules", "Writing clean functions and standard library", 2, (today + timedelta(days=28)).isoformat(), "completed"),
        ("Object-Oriented Programming", "Classes, inheritance, and clean architecture", 3, (today + timedelta(days=42)).isoformat(), "completed"),
        ("Data Handling & NumPy", "Arrays, pandas, and data manipulation", 4, (today + timedelta(days=56)).isoformat(), "completed"),
        ("Mini-Projects & APIs", "Building CLI applications and REST integrations", 5, (today + timedelta(days=62)).isoformat(), "pending"),
        ("Technical Interview Prep", "Algorithms, testing, and mock interviews", 6, target_d, "pending")
    ]
    m_objs = []
    for title, desc, idx, m_date, stat in milestones_data:
        m = Milestone(goal_id=goal.id, title=title, description=desc, order_index=idx, target_date=m_date, status=stat)
        db.add(m)
        m_objs.append(m)
    db.commit()

    # Add sample tasks: 4 completed, 1 today, 3 upcoming
    tasks_data = [
        (m_objs[0].id, "Setup Python environment and verify installation", (today - timedelta(days=4)).isoformat(), 30, "High", "completed", (today - timedelta(days=4))),
        (m_objs[0].id, "Practice Conditionals and Loops logic", (today - timedelta(days=3)).isoformat(), 45, "High", "completed", (today - timedelta(days=3))),
        (m_objs[1].id, "Complete Functions exercises on Codewars", (today - timedelta(days=2)).isoformat(), 45, "Medium", "completed", (today - timedelta(days=2))),
        (m_objs[2].id, "Design OOP Class hierarchy for a library system", (today - timedelta(days=1)).isoformat(), 60, "High", "completed", (today - timedelta(days=1))),
        (m_objs[3].id, "Watch: Python Functions & Lambda refresher", today.isoformat(), 30, "High", "pending", None),
        (m_objs[3].id, "Solve 5 coding problems on LeetCode", (today + timedelta(days=1)).isoformat(), 45, "Medium", "pending", None),
        (m_objs[3].id, "Revise notes on NumPy arrays and slicing", (today + timedelta(days=2)).isoformat(), 15, "Low", "pending", None),
        (m_objs[3].id, "Read about NumPy basics and vectorization", (today + timedelta(days=3)).isoformat(), 30, "Medium", "pending", None)
    ]
    for m_id, title, due_d, est_m, prio, stat, comp_at in tasks_data:
        comp_dt = datetime.combine(comp_at, datetime.min.time()) if comp_at else None
        t = Task(
            goal_id=goal.id,
            milestone_id=m_id,
            title=title,
            due_date=due_d,
            estimated_minutes=est_m,
            priority=prio,
            status=stat,
            completed_at=comp_dt
        )
        db.add(t)

    # Add progress logs for streak
    for i in range(4, 0, -1):
        log_d = (today - timedelta(days=i)).isoformat()
        db.add(ProgressLog(
            user_id=user_id,
            goal_id=goal.id,
            date=log_d,
            tasks_completed=1,
            total_minutes_spent=45,
            streak_count=6 - i + 1,
            notes="Demo seeded activity"
        ))

    db.commit()
    return goal
