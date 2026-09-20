"""
Typed CRUD Operations for GoalMate with Pydantic Validation.
Ensures all data crossing the database boundary conforms to strict schemas.
"""
from typing import Optional, List, Dict, Any
from database.models import (
    GoalCreate, GoalUpdate, GoalOut,
    MilestoneCreate, MilestoneOut,
    TaskCreate, TaskUpdate, TaskOut,
    ProgressLogCreate, ProgressStats, GoalHealth
)
from tools.goal_tools import create_goal, get_goals, get_goal, update_goal, delete_goal, create_milestone, get_milestones
from tools.task_tools import create_task, get_tasks, complete_task, update_task, reschedule_task


def crud_create_goal(data: GoalCreate, db_path: Optional[str] = None) -> GoalOut:
    raw = create_goal(
        title=data.title,
        description=data.description or "",
        category=data.category,
        target_date=data.target_date,
        priority=data.priority,
        daily_time_minutes=data.daily_time_minutes,
        preferred_schedule=data.preferred_schedule,
        db_path=db_path
    )
    return GoalOut.model_validate(raw)


def crud_get_goals(status: Optional[str] = None, db_path: Optional[str] = None) -> List[GoalOut]:
    raw_list = get_goals(status=status, db_path=db_path)
    return [GoalOut.model_validate(r) for r in raw_list]


def crud_get_goal(goal_id: int, db_path: Optional[str] = None) -> Optional[GoalOut]:
    raw = get_goal(goal_id, db_path=db_path)
    return GoalOut.model_validate(raw) if raw else None


def crud_create_milestone(data: MilestoneCreate, db_path: Optional[str] = None) -> MilestoneOut:
    raw = create_milestone(
        goal_id=data.goal_id,
        title=data.title,
        description=data.description or "",
        order_index=data.order_index,
        target_date=data.target_date,
        db_path=db_path
    )
    return MilestoneOut.model_validate(raw)


def crud_get_milestones(goal_id: int, db_path: Optional[str] = None) -> List[MilestoneOut]:
    raw_list = get_milestones(goal_id=goal_id, db_path=db_path)
    return [MilestoneOut.model_validate(r) for r in raw_list]


def crud_create_task(data: TaskCreate, db_path: Optional[str] = None) -> TaskOut:
    raw = create_task(
        goal_id=data.goal_id,
        title=data.title,
        milestone_id=data.milestone_id,
        description=data.description or "",
        due_date=data.due_date,
        estimated_minutes=data.estimated_minutes,
        priority=data.priority,
        db_path=db_path
    )
    return TaskOut.model_validate(raw)


def crud_get_tasks(
    goal_id: Optional[int] = None,
    status: Optional[str] = None,
    date: Optional[str] = None,
    db_path: Optional[str] = None
) -> List[TaskOut]:
    raw_list = get_tasks(goal_id=goal_id, status=status, date=date, db_path=db_path)
    return [TaskOut.model_validate(r) for r in raw_list]


def crud_complete_task(task_id: int, db_path: Optional[str] = None) -> Optional[TaskOut]:
    raw = complete_task(task_id=task_id, db_path=db_path)
    return TaskOut.model_validate(raw) if raw else None
