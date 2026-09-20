"""
Pydantic v2 Schemas for GoalMate API validation and serialization.
"""
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# --- Auth Schemas ---
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    agree_terms: bool = Field(default=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class PasswordResetRequest(BaseModel):
    email: EmailStr
    new_password: str = Field(..., min_length=8)


# --- Goal Schemas ---
GoalCategory = Literal["Education", "Career", "Fitness", "Personal", "Creative", "General"]
GoalStatus = Literal["active", "completed", "paused", "abandoned"]
PriorityLevel = Literal["Low", "Medium", "High", "Critical"]


class GoalBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = ""
    category: GoalCategory = "Education"
    target_date: Optional[str] = None
    priority: PriorityLevel = "Medium"
    daily_time_minutes: int = Field(default=60, ge=10, le=480)
    preferred_schedule: str = "flexible"


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[GoalCategory] = None
    target_date: Optional[str] = None
    priority: Optional[PriorityLevel] = None
    daily_time_minutes: Optional[int] = None
    preferred_schedule: Optional[str] = None
    status: Optional[GoalStatus] = None


class GoalOut(GoalBase):
    id: int
    user_id: int
    status: GoalStatus
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# --- Milestone Schemas ---
class MilestoneCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = ""
    order_index: int = 1
    target_date: Optional[str] = None


class MilestoneOut(BaseModel):
    id: int
    goal_id: int
    title: str
    description: Optional[str] = ""
    order_index: int
    target_date: Optional[str] = None
    status: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# --- Task Schemas ---
TaskStatus = Literal["pending", "completed", "rescheduled", "missed"]


class TaskCreate(BaseModel):
    milestone_id: Optional[int] = None
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = ""
    due_date: str
    estimated_minutes: int = 45
    priority: PriorityLevel = "Medium"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    estimated_minutes: Optional[int] = None
    priority: Optional[PriorityLevel] = None
    status: Optional[TaskStatus] = None


class TaskOut(BaseModel):
    id: int
    goal_id: int
    milestone_id: Optional[int] = None
    title: str
    description: Optional[str] = ""
    due_date: str
    estimated_minutes: int
    priority: str
    status: str
    completed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# --- Progress & Telemetry Schemas ---
class ProgressStats(BaseModel):
    goal_id: Optional[int] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    overdue_tasks: int = 0
    completion_percentage: float = 0.0
    current_streak: int = 0
    weekly_consistency_pct: float = 0.0
    active_days_this_week: int = 0


class GoalHealth(BaseModel):
    goal_id: int
    health_status: str
    health_color: str
    overdue_count: int
    completion_percentage: float
    recommendation: str
    metrics: ProgressStats
