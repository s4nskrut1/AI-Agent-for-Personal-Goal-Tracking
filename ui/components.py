"""
GoalMate — HTML Component Renderers.
100% faithful to the reference dashboard (media_1789749154473.jpg).
Enhanced with SVG graphs, vibrant images without quote overlays, delete option,
and retroactive past-task editing.
"""
import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
ASSET_DIR = f"{BASE_DIR}/assets"
FRONTEND_ASSET_DIR = f"{BASE_DIR}/frontend/assets/images"


def render_hero_banner(user_name: str = "Sanskriti") -> str:
    now = datetime.now()
    hour = now.hour
    if hour < 12:
        greeting = "Good Morning"
    elif hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    # Uses local time so past midnight on Friday naturally becomes Saturday
    date_str = now.strftime("%A, %d %b %Y")
    
    return f"""
<div class="hero-card">
    <img src="/gradio_api/file={ASSET_DIR}/header_banner_hinata.png" class="hero-bg-img" alt="" onerror="this.style.display='none'" />
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <div class="hero-date-badge">{date_str}</div>
        <div class="hero-greeting-title">{greeting}, {user_name} ☀️</div>
    </div>
</div>
"""


def render_current_goal_card(goals: Union[List[Any], Any]) -> str:
    if not isinstance(goals, list):
        goals = [goals] if goals else []
    goals = [g for g in goals if g is not None]

    if not goals:
        return """
<div class="gm-card">
    <div class="card-top-bar">
        <span class="card-title-wrap">🎯 Current Goals</span>
    </div>
    <div style="padding: 24px 0; text-align: center; color: #A0AEC0;">
        <p style="font-size: 0.9rem; font-weight: 600; color: #4A5568;">No active goals yet.</p>
        <p style="font-size: 0.78rem; margin-top: 4px;">Tell the AI Coach on the right what you want to achieve!</p>
    </div>
</div>
"""

    if len(goals) == 1:
        goal = goals[0]
        title = goal.title
        pct = goal.progress_pct
        total_t = goal.total_tasks
        done_t = goal.completed_tasks
        milestones = goal.milestones or []
        done_m = sum(1 for m in milestones if hasattr(m, 'progress_pct') and m.progress_pct == 100)
        total_m = len(milestones)
        days_left = goal.days_remaining
        start_str = goal.start_date.strftime("%d %b %Y") if goal.start_date else "Today"
        duration = goal.duration_days

        return f"""
<div class="gm-card clickable-card" onclick="window.gmViewGoal({goal.id})">
    <div class="card-top-bar">
        <span class="card-title-wrap">🎯 Current Goal</span>
        <div style="display: flex; align-items: center; gap: 10px;">
            <a class="card-header-link" onclick="event.stopPropagation(); window.gmViewGoal({goal.id});">View Details &gt;</a>
            <span class="sidebar-del-btn" title="Delete Goal" onclick="event.stopPropagation(); window.gmDeleteGoal({goal.id}, '{title}');">🗑️</span>
        </div>
    </div>

    <div class="goal-title-h">
        {title} <span style="font-size: 0.8rem; color: #A0AEC0;">✏️</span>
    </div>
    <div class="goal-meta-subtitle">
        Started on {start_str} • {duration} Days
    </div>

    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
        <span style="font-size: 0.75rem; color: #718096; font-weight: 600;">Overall Progress</span>
        <span style="font-size: 0.85rem; font-weight: 800; color: #F27B35;">{pct}%</span>
    </div>
    <div class="progress-track-outer">
        <div class="progress-bar-fill-orange" style="width: {pct}%;"></div>
    </div>

    <div class="goal-stats-pill-row">
        <div class="goal-stat-pill">
            <span>☑️</span> <span>{done_t} / {total_t} Tasks Completed</span>
        </div>
        <div class="goal-stat-pill">
            <span>🏁</span> <span>{done_m} / {total_m} Milestones Done</span>
        </div>
        <div class="goal-stat-pill">
            <span>📅</span> <span>{days_left} days Remaining</span>
        </div>
    </div>
</div>
"""

    # Multiple goals: show all goals in a clean, interactive stack!
    goal_items = []
    for g in goals:
        title = g.title
        pct = g.progress_pct
        total_t = g.total_tasks
        done_t = g.completed_tasks
        milestones = g.milestones or []
        done_m = sum(1 for m in milestones if hasattr(m, 'progress_pct') and m.progress_pct == 100)
        total_m = len(milestones)
        days_left = g.days_remaining
        duration = g.duration_days or 30

        goal_items.append(f"""
        <div class="dash-goal-item clickable-card" onclick="window.gmViewGoal({g.id})" style="background:#F8F9FA; border:1px solid #EAECEF; border-radius:12px; padding:10px 12px; margin-bottom:8px; transition:all 0.15s ease;">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:5px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:0.88rem; font-weight:800; color:#1A202C;">{title}</span>
                    <span style="font-size:0.7rem; color:#718096; background:#EDF2F7; padding:2px 6px; border-radius:6px; font-weight:600;">{duration}d</span>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:0.85rem; font-weight:800; color:#F27B35;">{pct}%</span>
                    <span class="sidebar-del-btn" title="Delete Goal" onclick="event.stopPropagation(); window.gmDeleteGoal({g.id}, '{title}');">🗑️</span>
                </div>
            </div>

            <div class="progress-track-outer" style="height:6px; margin-bottom:6px;">
                <div class="progress-bar-fill-orange" style="width:{pct}%;"></div>
            </div>

            <div style="display:flex; align-items:center; justify-content:space-between; font-size:0.72rem; color:#718096; font-weight:600;">
                <span>☑️ {done_t}/{total_t} Tasks</span>
                <span>🏁 {done_m}/{total_m} Milestones</span>
                <span>📅 {days_left}d left</span>
                <span style="color:#F27B35; font-weight:700;">View &rarr;</span>
            </div>
        </div>
        """)

    return f"""
<div class="gm-card">
    <div class="card-top-bar" style="margin-bottom:10px;">
        <div style="display:flex; align-items:center; gap:8px;">
            <span class="card-title-wrap">🎯 Current Goals</span>
            <span class="goals-count-badge" style="background:#FFF0E6; color:#F27B35; font-size:0.74rem; font-weight:800; padding:2px 8px; border-radius:999px;">{len(goals)} Active</span>
        </div>
        <span style="font-size:0.74rem; color:#A0AEC0; font-weight:600;">Click any goal to view details</span>
    </div>
    <div class="dash-goals-scroll-box" style="max-height:220px; overflow-y:auto; padding-right:2px;">
        {"".join(goal_items)}
    </div>
</div>
"""


def render_quick_stats_card(stats: Dict) -> str:
    return f"""
<div class="gm-card">
    <div class="card-top-bar">
        <span class="card-title-wrap">📊 Quick Stats</span>
    </div>
    <div class="quick-stats-2x2">
        <div class="qs-box">
            <div class="qs-icon-wrap" style="background: #FFF0E6; color: #F27B35;">🎯</div>
            <div>
                <div class="qs-val">{stats.get('total_goals', 0)}</div>
                <div class="qs-lbl">Total Goals</div>
            </div>
        </div>

        <div class="qs-box">
            <div class="qs-icon-wrap" style="background: #EBF8FF; color: #3182CE;">📋</div>
            <div>
                <div class="qs-val">{stats.get('active_tasks', 0)}</div>
                <div class="qs-lbl">Active Tasks</div>
            </div>
        </div>

        <div class="qs-box">
            <div class="qs-icon-wrap" style="background: #E6FFFA; color: #10B981;">✅</div>
            <div>
                <div class="qs-val">{stats.get('completed_today', 0)}</div>
                <div class="qs-lbl">Completed Today</div>
            </div>
        </div>

        <div class="qs-box">
            <div class="qs-icon-wrap" style="background: #FFF5F0; color: #DD6B20;">🔥</div>
            <div>
                <div class="qs-val">{stats.get('streak', 0)} days</div>
                <div class="qs-lbl">Current Streak</div>
            </div>
        </div>
    </div>
</div>
"""


def make_task_row(t: Dict) -> str:
    done = t.get("status") == "completed"
    cls_check = "completed" if done else ""
    cls_text = "completed" if done else ""
    check_mark = "✓" if done else ""
    toggle_target = "false" if done else "true"
    goal_tag = (t.get("goal_title") or "Goal")[:14]
    duration = t.get("duration") or "30 min"
    date_str = t.get("scheduled_date", "")

    return f"""
    <div class="task-row-item">
        <div class="task-check-circle {cls_check}" id="task-check-{t['id']}" onclick="window.gmToggleTask({t['id']}, {toggle_target})">
            {check_mark}
        </div>
        <span class="task-title-text {cls_text}" id="task-title-{t['id']}" onclick="window.gmToggleTask({t['id']}, {toggle_target})">
            {t['title']}
        </span>
        <span class="task-tag-badge">{date_str or goal_tag}</span>
        <span class="task-time-meta">{duration}</span>
        <div class="task-reorder-actions">
            <button class="btn-reschedule-quick" title="Postpone to Tomorrow" onclick="event.stopPropagation(); window.gmRescheduleTask({t['id']}, 'tomorrow')">➡️ Tomorrow</button>
        </div>
    </div>
    """


def render_today_tasks_card(today_tasks: List[Dict]) -> str:
    now = datetime.now()
    date_str = now.strftime("%a, %d %b %Y")

    if not today_tasks:
        items_html = """
        <div style="padding: 24px 0; text-align: center; color: #A0AEC0; font-size: 0.82rem;">
            No tasks scheduled for today. Ask your AI Coach to plan tasks!
        </div>
        """
    else:
        rows = [make_task_row(t) for t in today_tasks]
        items_html = "".join(rows)

    return f"""
<div class="gm-card">
    <div class="card-top-bar">
        <span class="card-title-wrap">📅 Today's Tasks <span style="font-size:0.75rem; font-weight:500; color:#A0AEC0; margin-left:4px;">{date_str}</span></span>
        <a class="card-header-link" onclick="window.gmShowDashboard()">View All &rarr;</a>
    </div>
    <div class="task-scroll-box" style="max-height: 220px;">
        {items_html}
    </div>
</div>
"""


def render_weekly_chart_card(weekly_data: List[Dict]) -> str:
    bars_html = []
    for d in weekly_data:
        pct = d.get("pct", 0)
        is_today = "today" if d.get("is_today") else ""
        is_start = "start" if d.get("is_start") else ""
        pct_label = f"{pct}%" if (d.get("total", 0) > 0 or pct > 0) else "0%"
        fill_height = max(6, pct) if (d.get("total", 0) > 0 or pct > 0) else 0

        bars_html.append(f"""
        <div class="w-col {is_today} {is_start}">
            <span class="w-pct-label">{pct_label}</span>
            <div class="w-track" title="{d.get('completed', 0)}/{d.get('total', 0)} tasks completed">
                <div class="w-fill" style="height: {fill_height}%;"></div>
            </div>
            <span class="w-day-label">{d.get('day', '')}</span>
        </div>
        """)

    return f"""
<div class="gm-card">
    <div class="card-top-bar">
        <span class="card-title-wrap">📊 Progress Timeline</span>
        <span class="graph-badge-chip">Adapts From Start Day</span>
    </div>
    <div class="weekly-bars-container">
        {"".join(bars_html)}
    </div>
</div>
"""


def render_milestones_card(goal: Optional[Any]) -> str:
    if not goal or not (goal.milestones or []):
        return """
<div class="gm-card">
    <div class="card-top-bar">
        <span class="card-title-wrap">🏁 Milestones</span>
    </div>
    <div style="padding: 24px 0; text-align: center; color: #A0AEC0; font-size: 0.82rem;">
        No milestones yet. Milestones appear automatically when you create a goal with AI!
    </div>
</div>
"""

    palette = [
        {"bg": "#10B981", "bar": "#10B981"},
        {"bg": "#3182CE", "bar": "#3182CE"},
        {"bg": "#805AD5", "bar": "#805AD5"},
        {"bg": "#F27B35", "bar": "#F27B35"},
        {"bg": "#A0AEC0", "bar": "#CBD5E0"},
    ]

    rows = []
    for i, m in enumerate(goal.milestones[:5]):
        c = palette[i % len(palette)]
        pct = m.progress_pct
        done = m.completed_tasks
        total = m.total_tasks

        rows.append(f"""
        <div class="milestone-row-item">
            <div class="ms-badge" style="background: {c['bg']};">{i + 1}</div>
            <span class="ms-title" title="{m.title}">{m.title}</span>
            <span class="ms-ratio">{done}/{total}</span>
            <div class="ms-track">
                <div class="ms-fill" style="width: {pct}%; background: {c['bar']};"></div>
            </div>
            <span class="ms-pct">{pct}%</span>
        </div>
        """)

    return f"""
<div class="gm-card">
    <div class="card-top-bar">
        <span class="card-title-wrap">🏁 Milestones</span>
        <a class="card-header-link" onclick="window.gmViewGoal({goal.id})">View All &rarr;</a>
    </div>
    <div class="milestones-list">
        {"".join(rows)}
    </div>
</div>
"""


def render_recent_activity_card(activities: List[Dict]) -> str:
    if not activities:
        return """
<div class="gm-card">
    <div class="card-top-bar">
        <span class="card-title-wrap">🕒 Recent Activity</span>
    </div>
    <div style="padding: 24px 0; text-align: center; color: #A0AEC0; font-size: 0.82rem;">
        No recent activity. Actions you or the AI Coach take will appear here!
    </div>
</div>
"""

    event_configs = {
        "task_completed": {"bg": "#E6FFFA", "color": "#10B981", "icon": "✓", "label": "Task completed"},
        "task_updated": {"bg": "#EBF8FF", "color": "#3182CE", "icon": "↩", "label": "Task updated"},
        "task_created": {"bg": "#EBF8FF", "color": "#3182CE", "icon": "+", "label": "Task created"},
        "goal_created": {"bg": "#FFF0E6", "color": "#F27B35", "icon": "🎯", "label": "Goal created"},
        "goal_updated": {"bg": "#FFF5F0", "color": "#DD6B20", "icon": "🔄", "label": "Goal updated"},
        "milestone_completed": {"bg": "#FAF5FF", "color": "#805AD5", "icon": "🏆", "label": "Milestone completed"},
    }

    rows = []
    for act in activities[:4]:
        etype = act.get("event_type", "task_completed")
        cfg = event_configs.get(etype, {"bg": "#F7FAFC", "color": "#718096", "icon": act.get("icon", "•"), "label": "Activity"})
        desc = act.get("description", "")
        sub = desc
        if ":" in desc:
            sub = desc.split(":", 1)[1].strip()

        rows.append(f"""
        <div class="activity-row-item">
            <div class="act-icon-box" style="background: {cfg['bg']}; color: {cfg['color']};">
                {cfg['icon']}
            </div>
            <div class="act-details">
                <div class="act-title">{cfg['label']}</div>
                <div class="act-desc" title="{sub}">{sub}</div>
            </div>
            <div class="act-time">{act.get('time', '')}</div>
        </div>
        """)

    return f"""
<div class="gm-card">
    <div class="card-top-bar">
        <span class="card-title-wrap">🕒 Recent Activity</span>
        <a class="card-header-link">View All &rarr;</a>
    </div>
    <div class="activity-list">
        {"".join(rows)}
    </div>
</div>
"""


def render_svg_progress_curve(points_data: List[Dict], height: int = 120) -> str:
    """Renders a smooth, rounded Day (X-axis) vs % Complete (Y-axis) SVG progress curve."""
    if not points_data:
        points_data = [
            {"day": "Day 1", "pct": 0}, {"day": "Day 2", "pct": 0},
            {"day": "Day 3", "pct": 0}, {"day": "Day 4", "pct": 0},
            {"day": "Day 5", "pct": 0}, {"day": "Day 6", "pct": 0},
            {"day": "Day 7", "pct": 0}
        ]

    left_pad = 34
    right_pad = 18
    top_pad = 14
    bottom_pad = 22
    chart_w = 320 - left_pad - right_pad
    chart_h = height - top_pad - bottom_pad
    n = max(1, len(points_data) - 1)
    step_x = chart_w / n

    coords = []
    for i, d in enumerate(points_data):
        pct = max(0, min(100, d.get("pct", 0)))
        x = round(left_pad + i * step_x, 1)
        y = round(top_pad + chart_h - (pct / 100.0 * chart_h), 1)
        coords.append((x, y, pct, d.get("day", ""), d.get("is_today", False)))

    # Smooth cubic Bezier spline (Catmull-Rom tangent formulation)
    if len(coords) == 1:
        path_d = f"M {coords[0][0]} {coords[0][1]}"
    else:
        path_d = f"M {coords[0][0]} {coords[0][1]}"
        tension = 0.28
        for i in range(len(coords) - 1):
            p0 = coords[i - 1] if i > 0 else coords[i]
            p1 = coords[i]
            p2 = coords[i + 1]
            p3 = coords[i + 2] if i + 2 < len(coords) else p2

            cp1x = round(p1[0] + (p2[0] - p0[0]) * tension, 1)
            cp1y = round(p1[1] + (p2[1] - p0[1]) * tension, 1)
            cp2x = round(p2[0] - (p3[0] - p1[0]) * tension, 1)
            cp2y = round(p2[1] - (p3[1] - p1[1]) * tension, 1)

            # Clamp control points so they stay within chart vertical limits
            cp1y = max(top_pad, min(top_pad + chart_h, cp1y))
            cp2y = max(top_pad, min(top_pad + chart_h, cp2y))

            path_d += f" C {cp1x} {cp1y}, {cp2x} {cp2y}, {p2[0]} {p2[1]}"

    baseline_y = top_pad + chart_h
    area_d = f"{path_d} L {coords[-1][0]} {baseline_y} L {coords[0][0]} {baseline_y} Z"

    dots_svg = []
    for x, y, pct, day, is_today in coords:
        fill_c = "#F27B35" if is_today else "#FFFFFF"
        r = 4.5 if is_today else 3.5
        halo = f'<circle cx="{x}" cy="{y}" r="8" fill="rgba(242, 123, 53, 0.22)"/>' if is_today else ''
        dots_svg.append(f"""
        {halo}
        <circle cx="{x}" cy="{y}" r="{r}" fill="{fill_c}" stroke="#F27B35" stroke-width="2.2"/>
        <text x="{x}" y="{max(10, y - 6)}" text-anchor="middle" font-size="8.5" font-weight="700" fill="#2D3748">{pct}%</text>
        <text x="{x}" y="{baseline_y + 15}" text-anchor="middle" font-size="9" font-weight="{'800' if is_today else '600'}" fill="{'#F27B35' if is_today else '#718096'}">{day}</text>
        """)

    y_100 = top_pad
    y_50 = top_pad + (chart_h / 2)
    y_0 = baseline_y
    grad_id = f"progGrad_{abs(hash(str(points_data))) % 100000}"

    return f"""
    <svg viewBox="0 0 320 {height}" style="width:100%; height:{height}px; overflow:visible;">
        <defs>
            <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#F27B35" stop-opacity="0.32"/>
                <stop offset="100%" stop-color="#F27B35" stop-opacity="0.01"/>
            </linearGradient>
        </defs>
        <!-- Y-Axis Gridlines & Labels -->
        <line x1="{left_pad}" y1="{y_100}" x2="{left_pad + chart_w}" y2="{y_100}" stroke="#EDF2F7" stroke-dasharray="3,3" stroke-width="1"/>
        <text x="{left_pad - 6}" y="{y_100 + 3}" text-anchor="end" font-size="8" font-weight="600" fill="#A0AEC0">100%</text>

        <line x1="{left_pad}" y1="{y_50}" x2="{left_pad + chart_w}" y2="{y_50}" stroke="#EDF2F7" stroke-dasharray="3,3" stroke-width="1"/>
        <text x="{left_pad - 6}" y="{y_50 + 3}" text-anchor="end" font-size="8" font-weight="600" fill="#A0AEC0">50%</text>

        <line x1="{left_pad}" y1="{y_0}" x2="{left_pad + chart_w}" y2="{y_0}" stroke="#E2E8F0" stroke-width="1.2"/>
        <text x="{left_pad - 6}" y="{y_0 + 3}" text-anchor="end" font-size="8" font-weight="600" fill="#A0AEC0">0%</text>

        <!-- Shaded Area & Smooth Rounded Bezier Trajectory Curve -->
        <path d="{area_d}" fill="url(#{grad_id})"/>
        <path d="{path_d}" fill="none" stroke="#F27B35" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>
        {"".join(dots_svg)}
    </svg>
    """


def render_daily_progress_curve_card(weekly_data: List[Dict]) -> str:
    points_data = weekly_data or []
    total_pct = sum(d.get("pct", 0) for d in points_data)
    avg_pct = round(total_pct / max(1, len(points_data)))
    peak = max(points_data, key=lambda d: d.get("pct", 0), default={"day": "—", "pct": 0})
    today_pt = next((d for d in points_data if d.get("is_today")), points_data[-1] if points_data else {"pct": 0})

    svg_content = render_svg_progress_curve(points_data, height=125)

    return f"""
<div class="gm-card progress-graph-card">
    <div class="card-top-bar">
        <span class="card-title-wrap">📈 Progress Graph</span>
        <span class="graph-badge-chip">Day vs % Complete</span>
    </div>

    <div class="graph-metric-strip">
        <div class="graph-metric-col">
            <div class="graph-metric-val" style="color:#F27B35;">{today_pt.get('pct', 0)}%</div>
            <div class="graph-metric-lbl">Today's %</div>
        </div>
        <div class="graph-metric-col">
            <div class="graph-metric-val">{avg_pct}%</div>
            <div class="graph-metric-lbl">Weekly Avg</div>
        </div>
        <div class="graph-metric-col">
            <div class="graph-metric-val" style="color:#10B981;">{peak.get('day', '—')} ({peak.get('pct', 0)}%)</div>
            <div class="graph-metric-lbl">Peak Day</div>
        </div>
    </div>

    <div class="svg-progress-wrap">
        {svg_content}
    </div>
</div>
"""

# Backwards compatibility alias
render_visual_velocity_card = render_daily_progress_curve_card


def render_sidebar_html(goals: List[Any], active_goal_id: Optional[int] = None, current_view: str = "dashboard", user_name: str = "Sanskriti") -> str:
    goals_html = []
    if goals:
        for g in goals:
            is_active = (active_goal_id == g.id)
            act_style = "background: #FFF0E6; color: #F27B35; font-weight: 700;" if is_active else ""
            goals_html.append(f"""
            <div class="sidebar-goal-row" style="{act_style}">
                <span class="sidebar-goal-link" onclick="window.gmViewGoal({g.id})">
                    • {g.title}
                </span>
                <button class="sidebar-del-btn" title="Delete Goal" onclick="window.gmDeleteGoal({g.id}, '{g.title}')">
                    ✕
                </button>
            </div>
            """)
    else:
        goals_html.append('<div style="padding: 6px 18px; font-size: 0.76rem; color: #718096; font-weight: 500;">No goals yet</div>')

    # Progressive accordion: stays open if active_goal_id is set
    is_open = bool(active_goal_id)
    chev = "▼" if is_open else "▶"
    disp = "flex" if is_open else "none"

    is_dash_active = (current_view == "dashboard" and not active_goal_id)
    is_prog_active = (current_view == "progress")

    return f"""
<div class="sidebar-brand">
    <img src="/gradio_api/file={ASSET_DIR}/volleyball_logo.jpg" class="sidebar-logo" alt="Logo" onerror="this.src='/gradio_api/file={FRONTEND_ASSET_DIR}/volleyball_logo.jpg'" />
    <div class="brand-text">
        <h2>GoalMate</h2>
        <span>Better Habits. Bigger Dreams.</span>
    </div>
</div>

<div class="sidebar-nav">
    <button class="nav-item {'active' if is_dash_active else ''}" onclick="window.gmShowDashboard()">
        <span>🏠</span> <span>Dashboard</span>
    </button>
    <button class="nav-item {'active' if is_prog_active else ''}" onclick="window.gmShowProgress()">
        <span>📈</span> <span>Progress</span>
    </button>
    <button class="nav-item {'active' if active_goal_id else ''}" id="sidebar-goals-toggle" onclick="window.gmToggleGoalsMenu()">
        <span style="display:flex; align-items:center; gap:8px;">
            <span>🎯</span> <span>Goals</span>
            <span class="goals-count-badge">{len(goals)}</span>
        </span>
        <span id="sidebar-goals-chevron" class="goals-chevron">{chev}</span>
    </button>
</div>

<div class="sidebar-goals-accordion" id="sidebar-goals-accordion" style="display: {disp};">
    {"".join(goals_html)}
</div>

<div class="sidebar-spacer"></div>

<div class="sidebar-user-footer" onclick="window.gmHandleLogout()" title="Click to Log Out / Switch Account">
    <div style="display:flex; align-items:center; justify-content:space-between;">
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:28px; height:28px; border-radius:50%; background:#FFF0E6; display:flex; align-items:center; justify-content:center; font-size:0.85rem;">🏐</div>
            <div>
                <div style="font-size:0.78rem; font-weight:800; color:#1A202C;">{user_name}</div>
                <div style="font-size:0.68rem; color:#718096;">Log out &rarr;</div>
            </div>
        </div>
        <span style="font-size:0.75rem; color:#A0AEC0;">🔒</span>
    </div>
</div>
"""


def render_goal_detail_view(goal, milestones: List, tasks: List, goal_weekly: List[Dict] = None) -> str:
    pct = goal.progress_pct
    done = goal.completed_tasks
    total = goal.total_tasks
    days = goal.days_remaining
    start = str(goal.start_date) if goal.start_date else "—"
    deadline = str(goal.deadline) if goal.deadline else "—"

    # Group tasks by date
    today_date = datetime.now().date()
    today_tasks = [t for t in tasks if t.scheduled_date == today_date]
    upcoming_tasks = [t for t in tasks if t.scheduled_date and t.scheduled_date > today_date and t.status == "pending"]
    past_tasks = [t for t in tasks if t.scheduled_date and t.scheduled_date < today_date]

    def make_task_html(t):
        is_done = t.status == "completed"
        cls_chk = "completed" if is_done else ""
        cls_txt = "completed" if is_done else ""
        check_mark = "✓" if is_done else ""
        date_str = str(t.scheduled_date) if t.scheduled_date else ""
        toggle_target = "false" if is_done else "true"

        if t.scheduled_date and t.scheduled_date > today_date:
            btn_quick = f'<button class="btn-reschedule-quick" title="Start Early (Move to Today)" onclick="event.stopPropagation(); window.gmRescheduleTask({t.id}, \'today\')">⚡ Today</button>'
        elif t.scheduled_date and t.scheduled_date < today_date and not is_done:
            btn_quick = f'<button class="btn-reschedule-quick" title="Catch Up (Move to Today)" onclick="event.stopPropagation(); window.gmRescheduleTask({t.id}, \'today\')">⚡ Today</button>'
        else:
            btn_quick = f'<button class="btn-reschedule-quick" title="Postpone to Tomorrow" onclick="event.stopPropagation(); window.gmRescheduleTask({t.id}, \'tomorrow\')">➡️ Tomorrow</button>'

        return f"""
        <div class="task-row-item">
            <div class="task-check-circle {cls_chk}" id="task-check-{t.id}" onclick="window.gmToggleTask({t.id}, {toggle_target})">
                {check_mark}
            </div>
            <span class="task-title-text {cls_txt}" id="task-title-{t.id}" onclick="window.gmToggleTask({t.id}, {toggle_target})">
                {t.title}
            </span>
            <span class="task-tag-badge">{date_str}</span>
            <span class="task-time-meta">{t.estimated_duration or '30 min'}</span>
            <div class="task-reorder-actions">
                {btn_quick}
            </div>
        </div>
        """

    tasks_html_list = []
    if today_tasks:
        tasks_html_list.append('<div class="task-sec-badge ongoing">● Ongoing</div>')
        tasks_html_list.extend([make_task_html(t) for t in today_tasks])
    if past_tasks:
        tasks_html_list.append('<div class="task-sec-badge past">● Past</div>')
        tasks_html_list.extend([make_task_html(t) for t in reversed(past_tasks[-12:])])
    if upcoming_tasks:
        tasks_html_list.append('<div class="task-sec-badge upcoming">● Upcoming</div>')
        tasks_html_list.extend([make_task_html(t) for t in upcoming_tasks[:12]])

    # Visual Milestone Stepper Roadmap
    stepper_nodes = []
    done_milestones_count = 0
    for i, m in enumerate(milestones[:5]):
        m_done = (m.progress_pct == 100)
        if m_done:
            done_milestones_count += 1
        m_active = (m.progress_pct > 0 and m.progress_pct < 100)
        circle_cls = "done" if m_done else ("active" if m_active else "pending")
        
        stepper_nodes.append(f"""
        <div class="step-node">
            <div class="step-circle {circle_cls}">{i+1}</div>
            <div class="step-label" title="{m.title}">{m.title}</div>
            <span style="font-size:0.68rem; font-weight:700; color:#718096; margin-top:2px;">{m.progress_pct}%</span>
        </div>
        """)
        if i < min(4, len(milestones) - 1):
            conn_cls = "done" if m_done else ""
            stepper_nodes.append(f'<div class="step-connector {conn_cls}"></div>')

    # Milestone distribution summary
    milestone_summary_rows = []
    palette = ["#10B981", "#3182CE", "#805AD5", "#F27B35", "#CBD5E0"]
    for i, m in enumerate(milestones[:5]):
        c = palette[i % len(palette)]
        milestone_summary_rows.append(f"""
        <div class="milestone-row-item">
            <div class="ms-badge" style="background:{c}; width:20px; height:20px; font-size:0.68rem;">{i+1}</div>
            <span class="ms-title" style="font-size:0.8rem;">{m.title}</span>
            <span class="ms-ratio" style="font-size:0.74rem;">{m.completed_tasks}/{m.total_tasks}</span>
            <div class="ms-track" style="width:70px;">
                <div class="ms-fill" style="width:{m.progress_pct}%; background:{c};"></div>
            </div>
            <span class="ms-pct" style="font-size:0.72rem;">{m.progress_pct}%</span>
        </div>
        """)

    daily_pace = round(total / max(1, goal.duration_days or 30), 1)
    goal_svg_curve = render_svg_progress_curve(goal_weekly or [], height=110)

    return f"""
<div style="padding: 16px 0;">
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:16px;">
        <button onclick="window.gmShowDashboard()" style="background:#FFFFFF; border:1px solid #CBD5E0; border-radius:10px; padding:8px 16px; font-size:0.82rem; font-weight:700; cursor:pointer; color:#4A5568; transition:all 0.15s; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            &larr; Back to Dashboard
        </button>
        <button class="btn-delete-goal" onclick="window.gmDeleteGoal({goal.id}, '{goal.title}')">
            🗑️ Delete Goal
        </button>
    </div>

    <!-- MAIN PROGRESS CARD -->
    <div class="gm-card" style="margin-bottom:16px;">
        <div style="font-size:1.35rem; font-weight:800; color:#1A202C;">{goal.title}</div>
        <p style="font-size:0.85rem; color:#718096; margin:6px 0 14px 0;">{goal.description or "Goal created by GoalMate AI Agent."}</p>
        
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;">
            <span style="font-size:0.8rem; font-weight:700; color:#4A5568;">Overall Completion</span>
            <span style="font-size:0.95rem; font-weight:800; color:#F27B35;">{pct}%</span>
        </div>
        <div class="progress-track-outer">
            <div class="progress-bar-fill-orange" style="width:{pct}%;"></div>
        </div>

        <div class="goal-stats-pill-row" style="margin-top:14px;">
            <div class="goal-stat-pill"><span>☑️</span> <span>{done} / {total} Tasks Completed</span></div>
            <div class="goal-stat-pill"><span>📅</span> <span>{days} days Remaining</span></div>
            <div class="goal-stat-pill"><span>🏁</span> <span>Deadline: {deadline}</span></div>
        </div>
    </div>

    <!-- VISUAL MILESTONE STEPPER ROADMAP -->
    <div class="gm-card" style="margin-bottom:16px;">
        <div class="card-top-bar">
            <span class="card-title-wrap">🗺️ Milestone Stepper Roadmap</span>
            <span style="font-size:0.75rem; font-weight:600; color:#718096;">Sequential Progress</span>
        </div>
        <div class="stepper-container">
            {"".join(stepper_nodes)}
        </div>
    </div>

    <!-- TASKS & PERFORMANCE BREAKDOWN GRID -->
    <div class="dash-grid-row">
        <!-- TASKS COLUMN -->
        <div class="gm-card">
            <div class="card-top-bar">
                <span class="card-title-wrap">📋 Scheduled Tasks ({total} Total)</span>
            </div>
            <div class="task-scroll-box" style="max-height: 410px;">
                {"".join(tasks_html_list) if tasks_html_list else "<div style='color:#A0AEC0; font-size:0.82rem; padding:16px 0; text-align:center;'>No tasks found.</div>"}
            </div>
        </div>

        <!-- PERFORMANCE & MILESTONES BREAKDOWN COLUMN -->
        <div class="gm-card">
            <div class="card-top-bar">
                <span class="card-title-wrap">📊 Milestones & Pace Tracking</span>
                <span class="graph-badge-chip">Day vs % Complete</span>
            </div>
            
            <div class="quick-stats-2x2" style="margin-bottom:12px;">
                <div class="qs-box">
                    <div class="qs-icon-wrap" style="background:#FFF0E6; color:#F27B35;">🏁</div>
                    <div>
                        <div class="qs-val">{done_milestones_count}/{len(milestones)}</div>
                        <div class="qs-lbl">Milestones Done</div>
                    </div>
                </div>
                <div class="qs-box">
                    <div class="qs-icon-wrap" style="background:#EBF8FF; color:#3182CE;">⚡</div>
                    <div>
                        <div class="qs-val">{daily_pace}</div>
                        <div class="qs-lbl">Tasks / Day Target</div>
                    </div>
                </div>
            </div>

            <div style="font-size:0.74rem; font-weight:800; color:#718096; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.04em;">Goal Day-Wise Progress Curve</div>
            <div class="svg-progress-wrap" style="margin-bottom:12px;">
                {goal_svg_curve}
            </div>

            <div style="font-size:0.74rem; font-weight:800; color:#718096; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.04em;">Milestone Breakdown</div>
            <div class="milestones-list" style="margin-bottom:12px;">
                {"".join(milestone_summary_rows)}
            </div>

            <div style="padding:8px 12px; background:#F8F9FA; border:1px solid #EDF2F7; border-radius:10px; font-size:0.76rem; color:#4A5568; line-height:1.4;">
                💡 <b>Coach Hinata's Tip:</b> Consistency builds champions! Work through today's tasks in the <b>Ongoing</b> section to stay ahead of schedule.
            </div>
        </div>
    </div>
</div>
"""


def render_one_month_heatmap(heatmap_data: List[Dict]) -> str:
    """Renders a clean, compact 1-month activity heatmap grid (4-5 weeks, strictly non-oversized)."""
    if not heatmap_data:
        return ""

    level_colors = {
        0: "#F1F5F9",  # light neutral
        1: "#FFE2CF",  # light peach
        2: "#FFAF7B",  # medium warm orange
        3: "#F27B35",  # vibrant Hinata orange
    }

    weeks = []
    curr_week = []
    for d in heatmap_data:
        curr_week.append(d)
        if len(curr_week) == 7:
            weeks.append(curr_week)
            curr_week = []
    if curr_week:
        weeks.append(curr_week)

    total_active_days = sum(1 for d in heatmap_data if d.get("completed", 0) > 0)
    total_completed = sum(d.get("completed", 0) for d in heatmap_data)

    cols_svg = []
    col_w = 20
    row_h = 18
    start_x = 24
    start_y = 14

    day_labels = ["M", "", "W", "", "F", "", "S"]
    labels_svg = []
    for idx, lbl in enumerate(day_labels):
        if lbl:
            labels_svg.append(f'<text x="14" y="{start_y + idx * row_h + 12}" font-size="8.5" font-weight="700" fill="#A0AEC0" text-anchor="end">{lbl}</text>')

    for w_idx, week in enumerate(weeks):
        x = start_x + w_idx * col_w
        for d_idx, day_info in enumerate(week):
            y = start_y + d_idx * row_h
            lvl = day_info.get("level", 0)
            fill = level_colors.get(lvl, "#F1F5F9")
            is_today = day_info.get("is_today", False)
            stroke = "#F27B35" if is_today else "none"
            stroke_w = "1.5" if is_today else "0"
            date_label = f"{day_info.get('day_name')}, {day_info.get('month_name')} {day_info.get('day_num')}"
            count_label = f"{day_info.get('completed', 0)} completed"

            cols_svg.append(f"""
            <rect x="{x}" y="{y}" width="14" height="14" rx="3.5" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}">
                <title>{date_label}: {count_label}</title>
            </rect>
            """)

    total_svg_w = start_x + len(weeks) * col_w + 10
    total_svg_h = start_y + 7 * row_h + 6

    return f"""
    <div class="compact-heatmap-wrap">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:0.92rem; font-weight:800; color:#1A202C;">📅 30-Day Activity Heatmap</span>
                <span class="graph-badge-chip">Past Month</span>
            </div>
            <div style="font-size:0.75rem; color:#718096; font-weight:600;">
                <span style="color:#F27B35; font-weight:800;">{total_active_days}</span> Active Days • <span style="color:#F27B35; font-weight:800;">{total_completed}</span> Tasks Completed
            </div>
        </div>

        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:16px;">
            <div style="overflow-x:auto;">
                <svg width="{total_svg_w}" height="{total_svg_h}" style="overflow:visible;">
                    {"".join(labels_svg)}
                    {"".join(cols_svg)}
                </svg>
            </div>

            <div style="display:flex; align-items:center; gap:6px; font-size:0.72rem; color:#A0AEC0; font-weight:600;">
                <span>Less</span>
                <span style="width:12px; height:12px; border-radius:3px; background:#F1F5F9; display:inline-block;"></span>
                <span style="width:12px; height:12px; border-radius:3px; background:#FFE2CF; display:inline-block;"></span>
                <span style="width:12px; height:12px; border-radius:3px; background:#FFAF7B; display:inline-block;"></span>
                <span style="width:12px; height:12px; border-radius:3px; background:#F27B35; display:inline-block;"></span>
                <span>More</span>
            </div>
        </div>
    </div>
    """


def render_progress_analytics_view(overview: Dict) -> str:
    """Renders a clean, spacious, uncluttered Progress & Analytics view with diverse graphs."""
    overall_pct = overview.get("overall_pct", 0)
    total_tasks = overview.get("total_tasks", 0)
    completed_tasks = overview.get("completed_tasks", 0)
    pending_tasks = overview.get("pending_tasks", 0)
    streak = overview.get("streak", 0)
    velocity = overview.get("velocity", 0.0)
    consistency = overview.get("consistency_rate", 0)
    total_week_done = overview.get("total_week_done", 0)
    goals = overview.get("goals", [])
    heatmap = overview.get("heatmap", [])

    # SVG Circular Donut Ring Calculation
    radius = 42
    circ = round(2 * 3.14159 * radius, 1)
    dash_offset = round(circ - (overall_pct / 100.0) * circ, 1)

    heatmap_html = render_one_month_heatmap(heatmap)

    goal_rows = []
    for g in goals:
        pct = g.get("progress_pct", 0)
        done = g.get("completed_tasks", 0)
        tot = g.get("total_tasks", 0)
        days = g.get("days_remaining", 0)
        cat = g.get("category", "General")

        goal_rows.append(f"""
        <div style="padding:10px 14px; background:#F8F9FA; border:1px solid #EDF2F7; border-radius:12px; margin-bottom:8px; cursor:pointer;" onclick="window.gmViewGoal({g.get('id')})">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:0.88rem; font-weight:800; color:#1A202C;">{g.get('title')}</span>
                    <span style="font-size:0.68rem; background:#EDF2F7; color:#718096; padding:2px 6px; border-radius:6px; font-weight:600;">{cat}</span>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:0.85rem; font-weight:800; color:#F27B35;">{pct}%</span>
                    <span style="font-size:0.72rem; color:#A0AEC0;">View &rarr;</span>
                </div>
            </div>
            <div class="progress-track-outer" style="height:6px; margin-bottom:6px;">
                <div class="progress-bar-fill-orange" style="width:{pct}%;"></div>
            </div>
            <div style="display:flex; align-items:center; justify-content:space-between; font-size:0.72rem; color:#718096; font-weight:600;">
                <span>☑️ {done}/{tot} Tasks Completed</span>
                <span>📅 {days} Days Left</span>
            </div>
        </div>
        """)

    return f"""
<div style="padding: 16px 0;">
    <!-- Top Action Bar -->
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:16px;">
        <button onclick="window.gmShowDashboard()" style="background:#FFFFFF; border:1px solid #CBD5E0; border-radius:10px; padding:8px 16px; font-size:0.82rem; font-weight:700; cursor:pointer; color:#4A5568; transition:all 0.15s; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            &larr; Back to Dashboard
        </button>
        <div style="display:flex; align-items:center; gap:8px;">
            <span class="graph-badge-chip" style="font-size:0.75rem; padding:4px 10px;">📊 System Telemetry</span>
        </div>
    </div>

    <!-- ROW 1: COMPLETION DONUT & VELOCITY METRICS -->
    <div class="dash-grid-row">
        <!-- DONUT GAUGE CARD -->
        <div class="gm-card">
            <div class="card-top-bar">
                <span class="card-title-wrap">🏆 Overall Completion</span>
                <span style="font-size:0.72rem; color:#718096; font-weight:600;">Across All Goals</span>
            </div>
            <div style="display:flex; align-items:center; justify-content:space-around; padding:6px 0 10px 0;">
                <!-- SVG Donut -->
                <div style="position:relative; width:110px; height:110px; display:flex; align-items:center; justify-content:center;">
                    <svg width="110" height="110" viewBox="0 0 100 100" style="transform:rotate(-90deg);">
                        <circle cx="50" cy="50" r="{radius}" fill="none" stroke="#F1F5F9" stroke-width="9"/>
                        <circle cx="50" cy="50" r="{radius}" fill="none" stroke="url(#donutGrad)" stroke-width="9"
                                stroke-dasharray="{circ}" stroke-dashoffset="{dash_offset}" stroke-linecap="round"/>
                        <defs>
                            <linearGradient id="donutGrad" x1="0" y1="0" x2="1" y2="1">
                                <stop offset="0%" stop-color="#FF9554"/>
                                <stop offset="100%" stop-color="#F27B35"/>
                            </linearGradient>
                        </defs>
                    </svg>
                    <div style="position:absolute; text-align:center;">
                        <div style="font-size:1.35rem; font-weight:900; color:#1A202C; line-height:1;">{overall_pct}%</div>
                        <div style="font-size:0.65rem; color:#A0AEC0; font-weight:700; margin-top:2px;">COMPLETED</div>
                    </div>
                </div>

                <!-- Stats Side List -->
                <div style="display:flex; flex-direction:column; gap:8px;">
                    <div class="analytics-metric-box" style="padding:6px 12px;">
                        <div style="font-size:1rem; font-weight:800; color:#1A202C;">{completed_tasks} / {total_tasks}</div>
                        <div style="font-size:0.68rem; color:#718096; font-weight:600;">Total Tasks Done</div>
                    </div>
                    <div class="analytics-metric-box" style="padding:6px 12px;">
                        <div style="font-size:1rem; font-weight:800; color:#DD6B20;">🔥 {streak} Days</div>
                        <div style="font-size:0.68rem; color:#718096; font-weight:600;">Active Daily Streak</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- HABIT VELOCITY CARD -->
        <div class="gm-card">
            <div class="card-top-bar">
                <span class="card-title-wrap">⚡ Habit Velocity & Consistency</span>
                <span class="graph-badge-chip">Telemetry</span>
            </div>
            <div class="quick-stats-2x2" style="margin-top:8px;">
                <div class="qs-box">
                    <div class="qs-icon-wrap" style="background:#FFF0E6; color:#F27B35;">🚀</div>
                    <div>
                        <div class="qs-val">{velocity}</div>
                        <div class="qs-lbl">Tasks / Day Velocity</div>
                    </div>
                </div>
                <div class="qs-box">
                    <div class="qs-icon-wrap" style="background:#E6FFFA; color:#10B981;">📈</div>
                    <div>
                        <div class="qs-val">{consistency}%</div>
                        <div class="qs-lbl">Weekly Consistency</div>
                    </div>
                </div>
                <div class="qs-box">
                    <div class="qs-icon-wrap" style="background:#EBF8FF; color:#3182CE;">🎯</div>
                    <div>
                        <div class="qs-val">{total_week_done}</div>
                        <div class="qs-lbl">7-Day Task Volume</div>
                    </div>
                </div>
                <div class="qs-box">
                    <div class="qs-icon-wrap" style="background:#FAF5FF; color:#805AD5;">🏅</div>
                    <div>
                        <div class="qs-val">{len(goals)}</div>
                        <div class="qs-lbl">Active Goal Tracks</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- ROW 2: GOAL BREAKDOWN MATRIX -->
    <div class="gm-card" style="margin-bottom:16px;">
        <div class="card-top-bar">
            <span class="card-title-wrap">🎯 Active Goals Progress Breakdown</span>
            <span style="font-size:0.75rem; color:#718096; font-weight:600;">Click any goal to view detail roadmap</span>
        </div>
        <div>
            {"".join(goal_rows) if goal_rows else "<div style='text-align:center; color:#A0AEC0; font-size:0.85rem; padding:20px 0;'>No active goals found.</div>"}
        </div>
    </div>

    <!-- ROW 3: COMPACT 1-MONTH HEATMAP -->
    <div class="gm-card">
        {heatmap_html}
    </div>
</div>
"""

