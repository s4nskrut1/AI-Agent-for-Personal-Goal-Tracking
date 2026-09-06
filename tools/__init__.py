"""Tools package for GoalMate agents."""
from .goal_tools import (
    create_goal,
    get_goals,
    get_goal,
    update_goal,
    delete_goal,
    create_milestone,
    get_milestones
)
from .task_tools import (
    create_task,
    get_tasks,
    get_pending_tasks,
    get_overdue_tasks,
    complete_task,
    update_task,
    reschedule_task,
    batch_reschedule_tasks
)
from .progress_tools import (
    calculate_progress,
    analyze_goal_health,
    generate_recovery_plan,
    replan_goal
)

__all__ = [
    "create_goal",
    "get_goals",
    "get_goal",
    "update_goal",
    "delete_goal",
    "create_milestone",
    "get_milestones",
    "create_task",
    "get_tasks",
    "get_pending_tasks",
    "get_overdue_tasks",
    "complete_task",
    "update_task",
    "reschedule_task",
    "batch_reschedule_tasks",
    "calculate_progress",
    "analyze_goal_health",
    "generate_recovery_plan",
    "replan_goal"
]
