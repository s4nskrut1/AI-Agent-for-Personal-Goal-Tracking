"""
UI Components and Visualizations for GoalMate.
Produces clean HTML layouts, KPI cards, goal lists, task items, and Plotly charts.
"""
import datetime
from typing import Optional, List, Dict, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from tools.goal_tools import get_goals, get_goal
from tools.task_tools import get_tasks, get_overdue_tasks, get_pending_tasks
from tools.progress_tools import calculate_progress, analyze_goal_health
from memory.memory import get_all_memories


def render_kpi_cards_html(goal_id: Optional[int] = None) -> str:
    """Generates the 4 top KPI statistic cards in clean HTML."""
    stats = calculate_progress(goal_id)
    pct = stats["completion_percentage"]
    completed = stats["completed_tasks"]
    total = stats["total_tasks"]
    streak = stats["current_streak"]
    overdue = stats["overdue_tasks"]
    
    overdue_class = "color: #ef4444;" if overdue > 0 else "color: #10b981;"
    
    return f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-title">Overall Progress</div>
            <div class="kpi-value">{pct}%</div>
            <div class="kpi-sub">{completed} of {total} tasks completed</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Current Streak</div>
            <div class="kpi-value">🔥 {streak} <span style="font-size:16px; font-weight:500; color:#9ca3af;">days</span></div>
            <div class="kpi-sub">Active consistency</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Tasks Overdue</div>
            <div class="kpi-value" style="{overdue_class}">⚠️ {overdue}</div>
            <div class="kpi-sub">{'Requires replanning' if overdue > 0 else 'All caught up!'}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Weekly Consistency</div>
            <div class="kpi-value">⚡ {stats['weekly_consistency_pct']}%</div>
            <div class="kpi-sub">{stats['active_days_this_week']} of 7 days active</div>
        </div>
    </div>
    """


def render_goals_sidebar_html(active_goal_id: Optional[int] = None) -> str:
    """Renders the goals sidebar cards with progress bars."""
    goals = get_goals()
    if not goals:
        return """
        <div style="padding: 20px; text-align: center; color: #9ca3af; font-size: 13px;">
            No goals created yet.<br>Start chatting to set your first goal!
        </div>
        """
        
    cards_html = []
    for g in goals:
        is_active = (g["id"] == active_goal_id)
        active_class = "active-goal" if is_active else ""
        g_stats = calculate_progress(g["id"])
        pct = g_stats["completion_percentage"]
        
        cards_html.append(f"""
        <div class="goal-card-item {active_class}">
            <div class="goal-card-title">
                <span>{g['title']}</span>
                <span class="goal-badge">{g.get('category', 'General')}</span>
            </div>
            <div style="font-size: 11px; color: #9ca3af; margin-bottom: 4px;">
                ⏱️ {g.get('daily_time_minutes', 60)}m/day | Target: {g.get('target_date', 'Ongoing')}
            </div>
            <div class="progress-track">
                <div class="progress-fill" style="width: {pct}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #9ca3af;">
                <span>{g_stats['completed_tasks']}/{g_stats['total_tasks']} tasks</span>
                <span style="font-weight: 700; color: #e5e7eb;">{pct}%</span>
            </div>
        </div>
        """)
        
    return "\n".join(cards_html)


def render_tasks_list_html(goal_id: Optional[int] = None) -> str:
    """Renders the detailed list of tasks with due dates and priority tags."""
    tasks = get_tasks(goal_id=goal_id)
    if not tasks:
        return """
        <div style="padding: 24px; text-align: center; color: #9ca3af; font-size: 14px;">
            No tasks found for this goal.
        </div>
        """
        
    today_str = datetime.date.today().isoformat()
    lines = []
    
    for t in tasks:
        is_completed = (t["status"] == "completed")
        is_overdue = (not is_completed and t["due_date"] < today_str)
        status_icon = "✅" if is_completed else ("⚠️" if is_overdue else "⏳")
        
        due_class = "task-due-tag overdue" if is_overdue else "task-due-tag"
        comp_class = "task-item-card completed" if is_completed else "task-item-card"
        
        prio_color = "#ef4444" if t["priority"] == "High" else ("#f59e0b" if t["priority"] == "Medium" else "#6b7280")
        
        lines.append(f"""
        <div class="{comp_class}">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 16px;">{status_icon}</span>
                <div>
                    <div style="font-size: 14px; font-weight: 600; color: #ffffff;">
                        #{t['id']} {t['title']}
                    </div>
                    <div style="font-size: 12px; color: #9ca3af; margin-top: 2px;">
                        Est: {t.get('estimated_minutes', 45)} mins &bull; 
                        <span style="color: {prio_color}; font-weight: 600;">{t['priority']}</span>
                    </div>
                </div>
            </div>
            <div>
                <span class="{due_class}">{t['due_date']}</span>
            </div>
        </div>
        """)
        
    return "\n".join(lines)


def render_memory_badges_html() -> str:
    """Renders stored user preferences and constraints as interactive chips."""
    memories = get_all_memories()
    if not memories:
        return "<span style='color:#6b7280; font-size:12px;'>No preferences recorded yet.</span>"
        
    chips = []
    for m in memories:
        chips.append(f"""
        <div class="memory-chip" title="{m['value']}">
            🧠 <strong>{m['key']}</strong>: {m['value']}
        </div>
        """)
    return f"<div class='memory-chip-list'>{''.join(chips)}</div>"


def create_progress_charts(goal_id: Optional[int] = None) -> go.Figure:
    """
    Creates an interactive Plotly visualization showing:
    1. Task distribution (Completed vs Pending vs Overdue)
    2. 7-Day completion consistency trend
    """
    stats = calculate_progress(goal_id)
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "domain"}, {"type": "xy"}]],
        subplot_titles=("Task Status Distribution", "Weekly Productivity Pace")
    )
    
    # 1. Donut Chart: Status
    labels = ['Completed', 'Pending', 'Overdue']
    values = [stats['completed_tasks'], max(0, stats['pending_tasks'] - stats['overdue_tasks']), stats['overdue_tasks']]
    colors = ['#10b981', '#6366f1', '#ef4444']
    
    if sum(values) == 0:
        values = [1]
        labels = ['No tasks']
        colors = ['#374151']
        
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            marker=dict(colors=colors),
            textinfo='percent+label',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # 2. Bar Chart: 7-Day window
    today = datetime.date.today()
    days = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
    day_labels = [d.strftime("%a (%m/%d)") for d in days]
    
    # Dummy/actual completed counts per day
    from tools.task_tools import get_tasks
    all_completed = get_tasks(goal_id=goal_id, status="completed")
    day_counts = []
    for d in days:
        d_str = d.isoformat()
        cnt = sum(1 for t in all_completed if t.get("completed_at") and t["completed_at"].startswith(d_str))
        day_counts.append(cnt)
        
    fig.add_trace(
        go.Bar(
            x=day_labels,
            y=day_counts,
            marker_color='#8b5cf6',
            opacity=0.85,
            name="Tasks Finished"
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Plus Jakarta Sans', color='#9ca3af', size=11),
        margin=dict(l=20, r=20, t=40, b=20),
        height=260,
        showlegend=False
    )
    
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)', row=1, col=2)
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)', row=1, col=2)
    
    return fig
