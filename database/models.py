"""
Pydantic Data Models and Validation Schemas for GoalMate.
Ensures strict validation of LLM outputs and database records before persistence.
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


# --- Enums / Literal Types ---
GoalStatus = Literal["active", "completed", "paused", "abandoned"]
MilestoneStatus = Literal["pending", "in_progress", "completed"]
TaskStatus = Literal["pending", "completed", "rescheduled", "missed"]
PriorityLevel = Literal["Low", "Medium", "High", "Critical"]
GoalCategory = Literal["Education", "Career", "Fitness", "Personal", "Creative", "General"]
GoalHealthStatus = Literal["On Track (Excellent Pace)", "On Track", "At Risk", "Needs Recovery / Behind Schedule"]


# --- Goal Models ---
class GoalBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=150, description="Clear, concise goal title")
    description: Optional[str] = Field(default="", max_length=1000, description="Summary of the objective and motivations")
    category: GoalCategory = Field(default="Education", description="Domain of the goal")
    target_date: Optional[str] = Field(default=None, description="Target completion date in YYYY-MM-DD format")
    priority: PriorityLevel = Field(default="Medium", description="Goal priority level")
    daily_time_minutes: int = Field(default=60, ge=10, le=480, description="Available daily capacity in minutes")
    preferred_schedule: Literal["morning", "afternoon", "evening", "flexible"] = Field(default="flexible", description="Preferred study/work window")


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=150)
    description: Optional[str] = None
    category: Optional[GoalCategory] = None
    target_date: Optional[str] = None
    priority: Optional[PriorityLevel] = None
    daily_time_minutes: Optional[int] = Field(default=None, ge=10, le=480)
    preferred_schedule: Optional[str] = None
    status: Optional[GoalStatus] = None


class GoalOut(GoalBase):
    id: int
    status: GoalStatus
    created_at: str
    updated_at: str


# --- Milestone Models ---
class MilestoneBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = Field(default="", max_length=500)
    order_index: int = Field(default=1, ge=1)
    target_date: Optional[str] = None


class MilestoneCreate(MilestoneBase):
    goal_id: int


class MilestoneOut(MilestoneBase):
    id: int
    goal_id: int
    status: MilestoneStatus
    created_at: str


# --- Task Models ---
class TaskBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(default="", max_length=500)
    due_date: str = Field(..., description="Scheduled date in YYYY-MM-DD")
    estimated_minutes: int = Field(default=45, ge=5, le=360)
    priority: PriorityLevel = Field(default="Medium")


class TaskCreate(TaskBase):
    goal_id: int
    milestone_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    estimated_minutes: Optional[int] = None
    priority: Optional[PriorityLevel] = None
    status: Optional[TaskStatus] = None
    completed_at: Optional[str] = None


class TaskOut(TaskBase):
    id: int
    goal_id: int
    milestone_id: Optional[int] = None
    status: TaskStatus
    completed_at: Optional[str] = None
    created_at: str
    updated_at: str


# --- Progress & Telemetry Models ---
class ProgressLogCreate(BaseModel):
    goal_id: Optional[int] = None
    date: str
    tasks_completed: int = 0
    total_minutes_spent: int = 0
    streak_count: int = 0
    notes: Optional[str] = None


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
    health_status: GoalHealthStatus
    health_color: str
    overdue_count: int
    completion_percentage: float
    recommendation: str
    metrics: ProgressStats


# --- Adaptive Replanning Models ---
class RescheduledTaskItem(BaseModel):
    id: int
    title: str
    previous_date: str
    new_date: str
    reason: str


class ReplanResult(BaseModel):
    success: bool
    goal_id: int
    rescheduled_count: int
    rescheduled_tasks: List[RescheduledTaskItem]
    daily_time_constraint: str
    adaptation_summary: str
    reason: Optional[str] = None


# --- LLM Structured Output Schema for Decomposed Plans ---
class LLMTaskDecomposition(BaseModel):
    title: str
    description: Optional[str] = ""
    estimated_minutes: int = 45
    priority: PriorityLevel = "Medium"


class LLMMilestoneDecomposition(BaseModel):
    title: str
    description: Optional[str] = ""
    tasks: List[LLMTaskDecomposition]


class LLMGoalPlan(BaseModel):
    milestones: List[LLMMilestoneDecomposition]
