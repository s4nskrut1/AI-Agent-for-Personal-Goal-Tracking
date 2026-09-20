"""
GoalMate — Backend Database Models and Setup.
SQLite + SQLAlchemy with full relational schema.
"""
import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, Text, Date
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "goalmate.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    goals = relationship("Goal", back_populates="user")


class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    category = Column(String(100), default="General")
    start_date = Column(Date, default=lambda: datetime.now().date())
    deadline = Column(Date, nullable=True)
    duration_days = Column(Integer, default=30)
    status = Column(String(50), default="active")  # active, completed, paused
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="goals")
    milestones = relationship("Milestone", back_populates="goal", cascade="all, delete-orphan", order_by="Milestone.order_index")
    tasks = relationship("Task", back_populates="goal", cascade="all, delete-orphan")
    activities = relationship("ActivityLog", back_populates="goal", cascade="all, delete-orphan")

    @property
    def total_tasks(self):
        return len(self.tasks)

    @property
    def completed_tasks(self):
        return sum(1 for t in self.tasks if t.status == "completed")

    @property
    def progress_pct(self):
        if self.total_tasks == 0:
            return 0
        return round((self.completed_tasks / self.total_tasks) * 100)

    @property
    def days_remaining(self):
        if not self.deadline:
            return 0
        delta = self.deadline - datetime.now().date()
        return max(0, delta.days)


class Milestone(Base):
    __tablename__ = "milestones"
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    order_index = Column(Integer, default=0)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.now)

    goal = relationship("Goal", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone")

    @property
    def total_tasks(self):
        return len(self.tasks)

    @property
    def completed_tasks(self):
        return sum(1 for t in self.tasks if t.status == "completed")

    @property
    def progress_pct(self):
        if self.total_tasks == 0:
            return 0
        return round((self.completed_tasks / self.total_tasks) * 100)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    scheduled_date = Column(Date, nullable=True)
    estimated_duration = Column(String(50), default="30 min")
    status = Column(String(50), default="pending")  # pending, completed, skipped
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    goal = relationship("Goal", back_populates="tasks")
    milestone = relationship("Milestone", back_populates="tasks")


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True)
    event_type = Column(String(100), nullable=False)  # task_completed, goal_created, milestone_done, etc.
    description = Column(Text, nullable=False)
    icon = Column(String(50), default="✓")
    created_at = Column(DateTime, default=datetime.now)

    goal = relationship("Goal", back_populates="activities")


def init_db():
    Base.metadata.create_all(bind=engine)
    try:
        import sqlite3
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("PRAGMA table_info(goals)")
            cols = [r[1] for r in c.fetchall()]
            if "user_id" not in cols:
                c.execute("ALTER TABLE goals ADD COLUMN user_id INTEGER")
                conn.commit()
    except Exception:
        pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
