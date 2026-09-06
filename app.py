"""
GoalMate — Autonomous AI Personal Goal Coach
Main Application Entry Point (Gradio)
"""
import os
import datetime
from pathlib import Path
import gradio as gr

from database.db import init_db, seed_demo_data, reset_db
from tools.goal_tools import get_goals, get_goal
from tools.task_tools import get_tasks, get_pending_tasks, complete_task
from tools.progress_tools import calculate_progress
from agents.orchestrator import AgentOrchestrator
from ui.components import (
    render_kpi_cards_html,
    render_goals_sidebar_html,
    render_tasks_list_html,
    render_memory_badges_html,
    create_progress_charts
)

# Initialize database
init_db()
seed_demo_data()

# Instantiate Orchestrator
orchestrator = AgentOrchestrator()

# Read custom CSS
css_path = Path(__file__).resolve().parent / "ui" / "styles.css"
custom_css = ""
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        custom_css = f.read()

# Helper to get current goal options for dropdown
def get_goal_choices():
    goals = get_goals()
    if not goals:
        return [("No goals available", None)]
    return [(f"#{g['id']} {g['title']}", g["id"]) for g in goals]

def get_pending_task_choices(goal_id=None):
    pending = get_pending_tasks(goal_id=goal_id)
    if not pending:
        return [("No pending tasks", None)]
    return [(f"#{t['id']} [{t['due_date']}] {t['title']}", t["id"]) for t in pending]


# Gradio Application
with gr.Blocks(title="GoalMate — Autonomous AI Personal Goal Coach") as demo:
    
    # State tracking
    active_goal_state = gr.State(value=1)
    
    # --- Top Navigation Bar ---
    with gr.Row(elem_classes=["goalmate-header"]):
        with gr.Column(scale=8):
            gr.HTML("""
            <div class="brand-title">
                <span>✦ GoalMate</span>
                <span style="font-size: 14px; font-weight: 500; color: #9ca3af; margin-left: 8px;">
                    Autonomous AI Personal Goal Coach
                </span>
            </div>
            """)
        with gr.Column(scale=4, elem_id="header-right", min_width=200):
            gr.HTML("""
            <div style="display: flex; justify-content: flex-end; align-items: center;">
                <div class="agent-online-pill">
                    <span class="pulsing-dot"></span>
                    <span>Agent Online & Active</span>
                </div>
            </div>
            """)

    # --- KPI Cards Row ---
    kpi_html = gr.HTML(value=render_kpi_cards_html(1), elem_id="kpi-container")

    # --- Main Workspace (2 Columns) ---
    with gr.Row():
        
        # LEFT COLUMN: Goals & Analytics
        with gr.Column(scale=5):
            with gr.Group():
                gr.Markdown("### 🎯 Active Goals & Trajectory")
                goal_dropdown = gr.Dropdown(
                    label="Focus Goal",
                    choices=get_goal_choices(),
                    value=1 if get_goals() else None,
                    interactive=True
                )
                goals_sidebar_html = gr.HTML(value=render_goals_sidebar_html(1))
                
            with gr.Group():
                gr.Markdown("### 📊 Performance Analytics")
                progress_chart = gr.Plot(value=create_progress_charts(1))
                
            with gr.Accordion("🧠 Persistent User Memory & Habits", open=False):
                memory_badges_html = gr.HTML(value=render_memory_badges_html())
                
            with gr.Row():
                reset_btn = gr.Button("🔄 Reset System DB", size="sm", variant="secondary")
                seed_btn = gr.Button("🌱 Seed Demo Data", size="sm", variant="secondary")

        # RIGHT COLUMN: Chat Coach & Quick Actions
        with gr.Column(scale=7):
            with gr.Group():
                gr.Markdown("### 💬 GoalMate AI Coach")
                
                chatbot = gr.Chatbot(
                    value=[
                        {
                            "role": "assistant",
                            "content": (
                                "Hello! I am **GoalMate**, your autonomous personal goal coach. 🎯\n\n"
                                "I don't just chat—I actively analyze your constraints, create structured milestones, "
                                "monitor your progress, and dynamically adapt your plan when life gets in the way.\n\n"
                                "How can I help you today? You can say:\n"
                                "- *'I want to learn Python in two months.'*\n"
                                "- *'I haven't studied for four days.'*\n"
                                "- *'Daily check-in'*\n"
                                "- *'Can you give me my weekly review?'*"
                            )
                        }
                    ],
                    height=460
                )
                
                # Quick Action Chips
                with gr.Row():
                    btn_checkin = gr.Button("🎯 Daily Check-in", elem_classes=["quick-action-btn"], size="sm")
                    btn_review = gr.Button("📊 Weekly Review", elem_classes=["quick-action-btn"], size="sm")
                    btn_replan = gr.Button("⚡ Auto-Replan Overdue", elem_classes=["quick-action-btn"], size="sm")
                    btn_report = gr.Button("📈 Progress Report", elem_classes=["quick-action-btn"], size="sm")
                
                # Chat Input Row
                with gr.Row():
                    chat_input = gr.Textbox(
                        placeholder="Message GoalMate... (e.g. 'I want to learn Python in 2 months')",
                        show_label=False,
                        scale=9,
                        lines=1,
                        autofocus=True
                    )
                    send_btn = gr.Button("Send ➤", variant="primary", scale=2)
                    clear_btn = gr.Button("Clear", scale=1)

    # --- Bottom Workspace: Interactive Task Board ---
    with gr.Accordion("📋 Interactive Task Management Board", open=True):
        with gr.Row():
            task_select_dropdown = gr.Dropdown(
                label="Select Pending Task to Complete",
                choices=get_pending_task_choices(1),
                scale=8,
                interactive=True
            )
            complete_task_btn = gr.Button("✅ Mark Selected Task Done", variant="primary", scale=4)
            
        tasks_list_html = gr.HTML(value=render_tasks_list_html(1))

    # --- Reactive Event Handlers ---
    
    def refresh_ui_state(active_gid):
        """Refreshes all HTML views and dropdowns based on current DB state."""
        return (
            render_kpi_cards_html(active_gid),
            render_goals_sidebar_html(active_gid),
            create_progress_charts(active_gid),
            render_memory_badges_html(),
            render_tasks_list_html(active_gid),
            gr.update(choices=get_goal_choices(), value=active_gid),
            gr.update(choices=get_pending_task_choices(active_gid))
        )

    def handle_user_message(user_msg, chat_history, active_gid):
        """Processes message through Orchestrator and updates conversation."""
        if not user_msg.strip():
            return "", chat_history, active_gid
            
        # Append user message
        new_history = list(chat_history)
        new_history.append({"role": "user", "content": user_msg})
        
        # Run through multi-agent orchestrator
        agent_response, updated_gid = orchestrator.process_message(
            user_message=user_msg,
            conversation_history=new_history,
            active_goal_id=active_gid
        )
        
        # Append assistant response
        new_history.append({"role": "assistant", "content": agent_response})
        final_gid = updated_gid or active_gid
        
        return "", new_history, final_gid

    def trigger_quick_action(action_text, chat_history, active_gid):
        """Dispatches quick action chip prompt directly to agent."""
        return handle_user_message(action_text, chat_history, active_gid)

    def handle_complete_selected_task(task_id, chat_history, active_gid):
        """Marks task completed via UI button and notifies chat."""
        if not task_id:
            return chat_history, active_gid
            
        task = complete_task(task_id)
        if task:
            stats = calculate_progress(task["goal_id"])
            notification = (
                f"🎉 Task #{task['id']} **{task['title']}** marked as completed!\n"
                f"Your overall progress is now **{stats['completion_percentage']}%** with a streak of 🔥 **{stats['current_streak']} days**."
            )
            new_history = list(chat_history)
            new_history.append({"role": "assistant", "content": notification})
            return new_history, task["goal_id"]
        return chat_history, active_gid

    def on_goal_change(new_gid):
        """Switches active goal focus."""
        gid = new_gid if new_gid else 1
        return (gid,) + refresh_ui_state(gid)

    def handle_db_reset():
        """Cleans DB and updates views."""
        reset_db()
        return (None,) + refresh_ui_state(None)

    def handle_db_seed():
        """Seeds demo data and updates views."""
        gid = seed_demo_data()
        return (gid,) + refresh_ui_state(gid)

    # Wire up Send and Enter submit
    send_event = send_btn.click(
        fn=handle_user_message,
        inputs=[chat_input, chatbot, active_goal_state],
        outputs=[chat_input, chatbot, active_goal_state]
    ).then(
        fn=refresh_ui_state,
        inputs=[active_goal_state],
        outputs=[kpi_html, goals_sidebar_html, progress_chart, memory_badges_html, tasks_list_html, goal_dropdown, task_select_dropdown]
    )

    chat_input.submit(
        fn=handle_user_message,
        inputs=[chat_input, chatbot, active_goal_state],
        outputs=[chat_input, chatbot, active_goal_state]
    ).then(
        fn=refresh_ui_state,
        inputs=[active_goal_state],
        outputs=[kpi_html, goals_sidebar_html, progress_chart, memory_badges_html, tasks_list_html, goal_dropdown, task_select_dropdown]
    )

    # Wire up Quick Action Buttons
    btn_checkin.click(
        fn=lambda h, g: trigger_quick_action("Daily check-in", h, g),
        inputs=[chatbot, active_goal_state],
        outputs=[chat_input, chatbot, active_goal_state]
    ).then(
        fn=refresh_ui_state,
        inputs=[active_goal_state],
        outputs=[kpi_html, goals_sidebar_html, progress_chart, memory_badges_html, tasks_list_html, goal_dropdown, task_select_dropdown]
    )

    btn_review.click(
        fn=lambda h, g: trigger_quick_action("Give me my weekly review", h, g),
        inputs=[chatbot, active_goal_state],
        outputs=[chat_input, chatbot, active_goal_state]
    ).then(
        fn=refresh_ui_state,
        inputs=[active_goal_state],
        outputs=[kpi_html, goals_sidebar_html, progress_chart, memory_badges_html, tasks_list_html, goal_dropdown, task_select_dropdown]
    )

    btn_replan.click(
        fn=lambda h, g: trigger_quick_action("I missed my tasks recently, please replan", h, g),
        inputs=[chatbot, active_goal_state],
        outputs=[chat_input, chatbot, active_goal_state]
    ).then(
        fn=refresh_ui_state,
        inputs=[active_goal_state],
        outputs=[kpi_html, goals_sidebar_html, progress_chart, memory_badges_html, tasks_list_html, goal_dropdown, task_select_dropdown]
    )

    btn_report.click(
        fn=lambda h, g: trigger_quick_action("Show my progress report", h, g),
        inputs=[chatbot, active_goal_state],
        outputs=[chat_input, chatbot, active_goal_state]
    ).then(
        fn=refresh_ui_state,
        inputs=[active_goal_state],
        outputs=[kpi_html, goals_sidebar_html, progress_chart, memory_badges_html, tasks_list_html, goal_dropdown, task_select_dropdown]
    )

    # Wire up Complete Task Button
    complete_task_btn.click(
        fn=handle_complete_selected_task,
        inputs=[task_select_dropdown, chatbot, active_goal_state],
        outputs=[chatbot, active_goal_state]
    ).then(
        fn=refresh_ui_state,
        inputs=[active_goal_state],
        outputs=[kpi_html, goals_sidebar_html, progress_chart, memory_badges_html, tasks_list_html, goal_dropdown, task_select_dropdown]
    )

    # Goal dropdown selection change
    goal_dropdown.change(
        fn=on_goal_change,
        inputs=[goal_dropdown],
        outputs=[active_goal_state, kpi_html, goals_sidebar_html, progress_chart, memory_badges_html, tasks_list_html, goal_dropdown, task_select_dropdown]
    )

    # Reset & Seed
    reset_btn.click(
        fn=handle_db_reset,
        inputs=[],
        outputs=[active_goal_state, kpi_html, goals_sidebar_html, progress_chart, memory_badges_html, tasks_list_html, goal_dropdown, task_select_dropdown]
    )

    seed_btn.click(
        fn=handle_db_seed,
        inputs=[],
        outputs=[active_goal_state, kpi_html, goals_sidebar_html, progress_chart, memory_badges_html, tasks_list_html, goal_dropdown, task_select_dropdown]
    )

    # Clear chat
    clear_btn.click(
        fn=lambda: [
            {"role": "assistant", "content": "Chat history cleared. How can I help you with your goals today?"}
        ],
        inputs=[],
        outputs=[chatbot]
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", 7860)))
    try:
        demo.launch(server_name="127.0.0.1", server_port=port, css=custom_css, theme=gr.themes.Base(), share=False)
    except OSError:
        # Fallback to automatic available port selection if 7860 is busy
        print(f"Port {port} is occupied. Finding the next available port...")
        demo.launch(server_name="127.0.0.1", css=custom_css, theme=gr.themes.Base(), share=False)
