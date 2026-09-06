"""UI Package for GoalMate."""
from .components import (
    render_kpi_cards_html,
    render_goals_sidebar_html,
    render_tasks_list_html,
    render_memory_badges_html,
    create_progress_charts
)

__all__ = [
    "render_kpi_cards_html",
    "render_goals_sidebar_html",
    "render_tasks_list_html",
    "render_memory_badges_html",
    "create_progress_charts"
]
