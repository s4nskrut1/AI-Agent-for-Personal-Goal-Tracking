"""
GoalMate — Main Gradio Application.
Unified with FastAPI for instant interactive clicks, live task checkboxes,
visual momentum graphs, milestone stepper roadmaps, and agentic AI coaching.
"""
import os
import sys
import json
import logging
from datetime import datetime, date
import gradio as gr

from backend.models import init_db, Goal
from backend.services import (
    get_all_goals, get_goal, get_dashboard_stats, get_today_tasks,
    get_past_missed_tasks, get_upcoming_tasks, get_weekly_data,
    get_goal_daily_progress, get_recent_activity, get_milestones, get_tasks_for_goal,
    complete_task as svc_complete_task, delete_goal as svc_delete_goal, get_session,
    get_system_progress_overview, reschedule_single_task
)
from agent.llm import agent_chat
from ui.styles import GOALMATE_CSS
from ui.components import (
    render_hero_banner, render_current_goal_card, render_quick_stats_card,
    render_today_tasks_card, render_weekly_chart_card, render_milestones_card,
    render_daily_progress_curve_card, render_sidebar_html, render_goal_detail_view,
    render_progress_analytics_view
)

logger = logging.getLogger("goalmate-dashboard")
USER_NAME = "Sanskriti"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
ASSET_DIR = f"{BASE_DIR}/assets"
FRONTEND_ASSET_DIR = f"{BASE_DIR}/frontend/assets/images"
AVATAR_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "assets", "images", "hinata_avatar.jpg")
AVATAR_URL = f"/gradio_api/file={FRONTEND_ASSET_DIR}/hinata_avatar.jpg"


def load_dashboard_state(db=None, user_id=None):
    """Fetch all dynamic state from SQLite database."""
    close_db = False
    if db is None:
        db = get_session()
        close_db = True
    try:
        goals = get_all_goals(db, user_id=user_id)
        primary_goal = goals[0] if goals else None
        stats = get_dashboard_stats(db, user_id=user_id)
        today_tasks = get_today_tasks(db, user_id=user_id)
        past_tasks = get_past_missed_tasks(db, user_id=user_id)
        upcoming_tasks = get_upcoming_tasks(db, user_id=user_id)
        weekly = get_weekly_data(db=db, user_id=user_id)
        recent_activity = get_recent_activity(db=db, user_id=user_id)
        return goals, primary_goal, stats, today_tasks, past_tasks, upcoming_tasks, weekly, recent_activity
    finally:
        if close_db:
            db.close()


def render_full_dashboard(selected_goal_id=None, current_view="dashboard", user_id=None, user_name=None):
    """Render all HTML components for the main dashboard, progress view, or a selected goal detail."""
    db = get_session()
    try:
        if user_id is None:
            user_id = 1
        if not user_name:
            from backend.models import User
            u = db.query(User).filter(User.id == user_id).first()
            user_name = u.name if u else "Sanskriti"

        goals, primary_goal, stats, today_tasks, past_tasks, upcoming_tasks, weekly, recent_activity = load_dashboard_state(db, user_id=user_id)
        sidebar_html = render_sidebar_html(goals, selected_goal_id, current_view=current_view, user_name=user_name)

        if current_view == "progress":
            overview = get_system_progress_overview(db, user_id=user_id)
            main_html = render_progress_analytics_view(overview)
            return sidebar_html, main_html

        if selected_goal_id:
            goal = get_goal(selected_goal_id, db)
            if goal:
                milestones = get_milestones(selected_goal_id, db)
                tasks = get_tasks_for_goal(selected_goal_id, db)
                goal_weekly = get_goal_daily_progress(selected_goal_id, db)
                main_html = render_goal_detail_view(goal, milestones, tasks, goal_weekly)
                return sidebar_html, main_html

        # Standard 3-row layout matching reference
        hero = render_hero_banner(user_name)
        curr_goal = render_current_goal_card(goals)
        quick_stats = render_quick_stats_card(stats)
        tasks_card = render_today_tasks_card(today_tasks)
        weekly_card = render_weekly_chart_card(weekly)
        milestones_card = render_milestones_card(primary_goal)
        progress_card = render_daily_progress_curve_card(weekly)

        main_html = f"""
        {hero}
        <div class="dash-grid-row">
            {curr_goal}
            {quick_stats}
        </div>
        <div class="dash-grid-row">
            {tasks_card}
            {weekly_card}
        </div>
        <div class="dash-grid-row">
            {milestones_card}
            {progress_card}
        </div>
        """
        return sidebar_html, main_html
    finally:
        db.close()


JS_HEAD = """
<script>
window.gmCurrentGoalId = null;
window.gmCurrentView = 'dashboard';

function gmGetUserInfo() {
    try {
        const raw = localStorage.getItem('gm_user');
        if (raw) {
            const parsed = JSON.parse(raw);
            if (parsed && parsed.id) return parsed;
        }
    } catch(e) {}
    return { id: 1, name: 'Sanskriti' };
}

window.gmHandleLogout = function() {
    localStorage.removeItem('gm_user');
    localStorage.removeItem('gm_token');
    window.location.href = '/login';
};

window.gmToggleTask = async function(taskId, markDone) {
    const chk = document.getElementById('task-check-' + taskId);
    const ttl = document.getElementById('task-title-' + taskId);
    if (chk) {
        if (markDone) {
            chk.classList.add('completed');
            chk.innerText = '✓';
        } else {
            chk.classList.remove('completed');
            chk.innerText = '';
        }
    }
    if (ttl) {
        if (markDone) ttl.classList.add('completed');
        else ttl.classList.remove('completed');
    }

    try {
        await fetch('/api/task/toggle', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({task_id: taskId, completed: markDone})
        });
        await window.gmRefreshView();
    } catch (err) {
        console.error('Error toggling task:', err);
    }
};

window.gmRescheduleTask = async function(taskId, target) {
    try {
        await fetch('/api/task/reschedule', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({task_id: taskId, target: target})
        });
        await window.gmRefreshView();
    } catch (err) {
        console.error('Error rescheduling task:', err);
    }
};

window.gmViewGoal = async function(goalId) {
    window.gmCurrentGoalId = goalId;
    window.gmCurrentView = 'goal';
    await window.gmRefreshView();
};

window.gmShowDashboard = async function() {
    window.gmCurrentGoalId = null;
    window.gmCurrentView = 'dashboard';
    await window.gmRefreshView();
};

window.gmShowProgress = async function() {
    window.gmCurrentGoalId = null;
    window.gmCurrentView = 'progress';
    await window.gmRefreshView();
};

window.gmDeleteGoal = async function(goalId, title) {
    if (!confirm(`Are you sure you want to delete the goal "${title}"?\\nAll associated milestones and tasks will be permanently removed.`)) {
        return;
    }
    try {
        await fetch('/api/goal/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({goal_id: goalId})
        });
        window.gmCurrentGoalId = null;
        window.gmCurrentView = 'dashboard';
        await window.gmRefreshView();
    } catch (err) {
        console.error('Error deleting goal:', err);
    }
};

window.gmGoalsExpanded = false;

window.gmToggleGoalsMenu = function() {
    const acc = document.getElementById('sidebar-goals-accordion');
    const chev = document.getElementById('sidebar-goals-chevron');
    if (!acc) return;
    const isHidden = (acc.style.display === 'none' || acc.style.display === '');
    window.gmGoalsExpanded = isHidden;
    acc.style.display = isHidden ? 'flex' : 'none';
    if (chev) {
        chev.innerText = isHidden ? '▼' : '▶';
    }
};

window.gmRefreshView = async function() {
    try {
        const u = gmGetUserInfo();
        const qParams = `?user_id=${u.id}&user_name=${encodeURIComponent(u.name)}`;
        let url = '/api/dashboard/html' + qParams;
        if (window.gmCurrentGoalId) {
            url = '/api/goal/' + window.gmCurrentGoalId + '/html' + qParams;
        } else if (window.gmCurrentView === 'progress') {
            url = '/api/progress/html' + qParams;
        }
        const res = await fetch(url);
        const data = await res.json();
        
        const sideBox = document.getElementById('gm-sidebar-container');
        if (sideBox && data.sidebar) {
            sideBox.innerHTML = data.sidebar;
            if (window.gmGoalsExpanded || window.gmCurrentGoalId) {
                const acc = document.getElementById('sidebar-goals-accordion');
                const chev = document.getElementById('sidebar-goals-chevron');
                if (acc) acc.style.display = 'flex';
                if (chev) chev.innerText = '▼';
            }
        }

        const mainBox = document.getElementById('gm-main-container');
        if (mainBox && data.main) {
            mainBox.innerHTML = data.main;
        }
    } catch (err) {
        console.error('Error refreshing view:', err);
    }
};

// Initial sync on client load
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(window.gmRefreshView, 150);
});
setTimeout(window.gmRefreshView, 300);

let lastStateHash = "";
setInterval(async () => {
    try {
        const u = gmGetUserInfo();
        const res = await fetch(`/api/db/state?user_id=${u.id}`);
        const data = await res.json();
        if (lastStateHash && lastStateHash !== data.hash) {
            window.gmRefreshView();
        }
        lastStateHash = data.hash;
    } catch (e) {}
}, 2500);
</script>
"""


def build_app():
    init_db()
    initial_sidebar, initial_main = render_full_dashboard()

    with gr.Blocks(title="GoalMate — Autonomous AI Goal Coach") as app:

        # ── STATE ──────────────────────────────────────────────────────────
        chat_state = gr.State([])

        with gr.Row(elem_id="gm-shell"):

            # ════════════════════════════════════════════════════════════════
            # 1. LEFT SIDEBAR (Vibrant Background with Hinata anime art)
            # ════════════════════════════════════════════════════════════════
            with gr.Column(elem_id="gm-sidebar", scale=0, min_width=230):
                sidebar_display = gr.HTML(f'<div id="gm-sidebar-container" style="height:100%; display:flex; flex-direction:column;">{initial_sidebar}</div>')

            # ════════════════════════════════════════════════════════════════
            # 2. CENTER MAIN DASHBOARD
            # ════════════════════════════════════════════════════════════════
            with gr.Column(elem_id="gm-main", scale=1):
                with gr.Column(elem_id="gm-center"):
                    main_display = gr.HTML(f'<div id="gm-main-container">{initial_main}</div>')

            # ════════════════════════════════════════════════════════════════
            # 3. RIGHT AI COACH PANEL (Clean, natural, no hardcoded prompt chips)
            # ════════════════════════════════════════════════════════════════
            with gr.Column(elem_id="gm-coach", scale=0, min_width=340):

                gr.HTML(f"""
                <div class="coach-header-bar">
                    <div class="coach-info-left">
                        <img src="{AVATAR_URL}"
                             onerror="this.src='/gradio_api/file={ASSET_DIR}/volleyball_logo.jpg'"
                             class="coach-avatar-img" alt="Coach" />
                        <div>
                            <div class="coach-name-title">AI Coach</div>
                            <div class="coach-status-green"><span class="status-dot-pulse"></span>Online</div>
                        </div>
                    </div>
                    <span style="color:#A0AEC0; font-size:1.1rem; cursor:pointer;" title="Settings">&#9881;</span>
                </div>
                """)

                chatbot = gr.Chatbot(
                    value=[
                        {"role": "assistant", "content": "Hey Sanskriti! 👋 I'm your GoalMate AI Coach. What would you like to work on or achieve today?"}
                    ],
                    show_label=False,
                    elem_id="coach-chatbot",
                    height=520,
                    avatar_images=(None, AVATAR_FILE if os.path.exists(AVATAR_FILE) else None),
                )

                # Chat Input Row
                with gr.Row(elem_classes="coach-input-container"):
                    chat_input = gr.Textbox(
                        placeholder="Type your message here...",
                        show_label=False,
                        elem_id="coach-input",
                        scale=6,
                        container=False,
                        lines=1
                    )
                    send_btn = gr.Button("➤", elem_id="coach-send-btn", scale=1, min_width=40)

        # ════════════════════════════════════════════════════════════════════
        # EVENT CALLBACKS
        # ════════════════════════════════════════════════════════════════════

        def handle_user_message(user_msg, history):
            if not user_msg or not user_msg.strip():
                s_bar, m_dash = render_full_dashboard()
                return history, history, "", f'<div id="gm-sidebar-container" style="height:100%; display:flex; flex-direction:column;">{s_bar}</div>', f'<div id="gm-main-container">{m_dash}</div>'

            history = history + [{"role": "user", "content": user_msg}]
            yield history, history, "", gr.update(), gr.update()

            reply, updated_history, actions = agent_chat(user_msg, [
                {"role": m["role"], "content": m["content"]} for m in history[:-1]
            ])

            final_history = updated_history if updated_history else history + [{"role": "assistant", "content": reply}]

            s_bar, m_dash = render_full_dashboard()
            yield final_history, final_history, "", f'<div id="gm-sidebar-container" style="height:100%; display:flex; flex-direction:column;">{s_bar}</div>', f'<div id="gm-main-container">{m_dash}</div>'

        send_btn.click(
            handle_user_message,
            inputs=[chat_input, chat_state],
            outputs=[chatbot, chat_state, chat_input, sidebar_display, main_display]
        )
        chat_input.submit(
            handle_user_message,
            inputs=[chat_input, chat_state],
            outputs=[chatbot, chat_state, chat_input, sidebar_display, main_display]
        )

    return app
