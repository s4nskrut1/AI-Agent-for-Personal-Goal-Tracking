"""
Pixel-Perfect Visual Layout Renderer for GoalMate.
Guarantees 100% fidelity matching the reference mockup (media_1789289509305.jpg).
Uses FastAPI static routes for instant asset rendering.
"""
import datetime
from typing import List, Dict, Any, Optional


def get_initial_messages() -> List[Dict[str, str]]:
    """Returns the exact initial conversation seen in the reference mockup."""
    return [
        {
            "role": "assistant",
            "content": (
                "Hey Sanskruti! 👋<br><br>"
                "I'm your AI Goal Coach. I can help you set goals, create personalized plans, "
                "track your progress, adapt when things change, and keep you motivated.<br><br>"
                "What would you like to achieve today?"
            )
        },
        {
            "role": "user",
            "content": "I want to become internship-ready in Python in 3 months."
        },
        {
            "role": "assistant",
            "content": (
                "That's an amazing goal! 🚀<br><br>"
                "To create the best plan for you, I'll need a few details:<br><br>"
                "<div class='numbered-step-list'>"
                "<div class='numbered-step-item'><span class='step-num-badge'>1</span> What's your current level in Python? (Beginner / Some knowledge / Intermediate)</div>"
                "<div class='numbered-step-item'><span class='step-num-badge'>2</span> How much time can you dedicate per day or per week?</div>"
                "<div class='numbered-step-item'><span class='step-num-badge'>3</span> Do you have any specific areas you want to focus on? (e.g., Data Science, Web Dev, Projects)</div>"
                "</div><br>"
                "Once I have this, I'll create a personalized 3-month roadmap for you!"
            )
        }
    ]


def render_full_dashboard_html(
    user_name: str = "Sanskruti",
    streak_days: int = 6,
    goal_title: str = "Become internship-ready in Python",
    goal_status: str = "On Track",
    progress_pct: int = 72,
    deadline_str: str = "Dec 12, 2025",
    days_left: int = 68,
    milestones_done: int = 4,
    milestones_total: int = 6,
    consistency_pct: int = 78,
    tasks_list: Optional[List[Dict[str, Any]]] = None,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """Renders the complete, pixel-perfect 3-column SaaS dashboard."""
    robot_url = "/assets/ai_robot.png"
    hiker_full_url = "/assets/sidebar_hiker_full.png"
    python_logo_url = "/assets/python_logo.png"

    if tasks_list is None:
        tasks_list = [
            {"id": 1, "title": "Watch: Python Functions", "duration": "30 min", "done": True},
            {"id": 2, "title": "Solve 5 coding problems", "duration": "45 min", "done": False},
            {"id": 3, "title": "Revise notes", "duration": "15 min", "done": False},
            {"id": 4, "title": "Read about NumPy basics", "duration": "30 min", "done": False}
        ]

    if chat_history is None:
        chat_history = get_initial_messages()

    user_initial = user_name[0].upper() if user_name else "S"

    # Build Chat HTML
    chat_bubbles_html = []
    for msg in chat_history:
        if msg["role"] == "assistant":
            chat_bubbles_html.append(f"""
            <div class="chat-bubble-row bot-row">
                <div class="bot-avatar-wrap">
                    <img src="{robot_url}" class="avatar-robot-img" alt="Robot" />
                </div>
                <div class="chat-bubble bot-bubble">
                    {msg["content"]}
                </div>
            </div>
            """)
        else:
            chat_bubbles_html.append(f"""
            <div class="chat-bubble-row user-row">
                <div class="chat-bubble user-bubble">
                    {msg["content"]}
                </div>
                <div class="user-avatar-circle-sm">
                    {user_initial}
                </div>
            </div>
            """)

    # Build Tasks HTML
    tasks_html = []
    for t in tasks_list:
        is_done = t.get("done", False)
        check_class = "task-checkbox checked" if is_done else "task-checkbox"
        text_class = "task-title-text done" if is_done else "task-title-text"
        check_inner = "✓" if is_done else ""
        t_id = t.get("id", 1)
        tasks_html.append(f"""
        <div class="task-item-row" onclick="gmToggleTask({t_id})">
            <div class="task-item-left">
                <div class="{check_class}">{check_inner}</div>
                <span class="{text_class}">{t['title']}</span>
            </div>
            <span class="task-duration-badge">{t.get('duration', '30 min')}</span>
        </div>
        """)

    return f"""
    <div class="gm-app-wrapper">
        
        <!-- ================= LEFT SIDEBAR ================= -->
        <aside class="gm-sidebar">
            <div class="sidebar-top">
                <div class="gm-brand-logo">
                    <span class="gm-leaf-icon">🌱</span>
                    <div>
                        <div class="gm-brand-title">GoalMate</div>
                        <div class="gm-brand-tagline">Your AI Goal Coach</div>
                    </div>
                </div>

                <nav class="gm-nav-menu">
                    <div class="nav-menu-item active" onclick="gmNavigate('home')">
                        <span class="nav-item-icon">🏠</span>
                        <span>Home</span>
                    </div>
                    <div class="nav-menu-item" onclick="gmNavigate('goals')">
                        <span class="nav-item-icon">🎯</span>
                        <span>My Goals</span>
                    </div>
                    <div class="nav-menu-item" onclick="gmNavigate('progress')">
                        <span class="nav-item-icon">📊</span>
                        <span>Progress</span>
                    </div>
                    <div class="nav-menu-item" onclick="gmNavigate('insights')">
                        <span class="nav-item-icon">💡</span>
                        <span>Insights</span>
                    </div>
                    <div class="nav-menu-item" onclick="gmNavigate('settings')">
                        <span class="nav-item-icon">⚙️</span>
                        <span>Settings</span>
                    </div>
                </nav>
            </div>

            <!-- Bottom Climber Illustration Card -->
            <div class="sidebar-bottom-art">
                <img src="{hiker_full_url}" class="sidebar-hiker-image" alt="Climber Artwork" />
            </div>
        </aside>

        <!-- ================= MAIN CONTENT AREA ================= -->
        <main class="gm-main-content">
            
            <!-- TOP GREETING & STATUS BAR -->
            <header class="gm-top-header">
                <div class="greeting-left">
                    <h1 class="greeting-title">Good Evening, {user_name}! 👋</h1>
                    <p class="greeting-subtitle">Keep going. You're closer than you think.</p>
                </div>

                <div class="greeting-right">
                    <div class="quote-pill-badge">
                        <span class="quote-leaf">🌱</span>
                        <span>"Discipline today, freedom tomorrow."</span>
                    </div>
                    <div class="streak-pill-badge">
                        <span class="flame-icon">🔥</span>
                        <span class="streak-bold">{streak_days}</span>
                        <span class="streak-sub">day streak</span>
                    </div>
                    <div class="user-avatar-circle-lg">
                        {user_initial}
                    </div>
                </div>
            </header>

            <!-- 2-COLUMN WORKSPACE: CENTER COACH + RIGHT DASHBOARD -->
            <div class="gm-workspace-grid">
                
                <!-- ================= CENTER COLUMN: AI COACH ================= -->
                <section class="gm-center-column">
                    <!-- Main White Coach Card -->
                    <div class="gm-coach-card">
                        <!-- Card Header -->
                        <div class="coach-card-header">
                            <div class="coach-header-left">
                                <img src="{robot_url}" class="coach-avatar-circle" alt="GoalMate AI Robot" />
                                <div>
                                    <div class="coach-title-status">
                                        <span class="coach-name">GoalMate AI</span>
                                        <span class="coach-status-pill">
                                            <span class="green-dot"></span> Online
                                        </span>
                                    </div>
                                    <p class="coach-tagline">Your personal AI agent for a better you.</p>
                                </div>
                            </div>
                            <button class="clear-chat-btn" onclick="gmClearChat()">
                                <span>🗑️</span> Clear Chat
                            </button>
                        </div>

                        <!-- Chat Messages Scroll Container -->
                        <div class="coach-chat-stream" id="gmChatStream">
                            {''.join(chat_bubbles_html)}
                        </div>

                        <!-- Quick Choice Prompt Chips -->
                        <div class="quick-chips-row">
                            <button class="quick-chip-pill" onclick="gmSendPrompt('I\\'m a complete beginner')">
                                I'm a complete beginner
                            </button>
                            <button class="quick-chip-pill" onclick="gmSendPrompt('I can study 1-2 hours daily')">
                                I can study 1-2 hours daily
                            </button>
                            <button class="quick-chip-pill" onclick="gmSendPrompt('Focus on Data Science')">
                                Focus on Data Science
                            </button>
                            <button class="quick-chip-pill" onclick="gmSendPrompt('Just create a plan')">
                                Just create a plan
                            </button>
                        </div>

                        <!-- Pill Input Box -->
                        <div class="chat-input-pill-box">
                            <span class="paperclip-icon">📎</span>
                            <input 
                                type="text" 
                                class="chat-text-input" 
                                id="gmChatInput" 
                                placeholder="Type your message here..." 
                                onkeydown="if(event.key==='Enter') gmSubmitChat()"
                            />
                            <button class="send-action-btn" onclick="gmSubmitChat()">
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                    <line x1="22" y1="2" x2="11" y2="13"></line>
                                    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                                </svg>
                            </button>
                        </div>
                    </div>

                    <!-- 4 Bottom Action Cards (Grid) -->
                    <div class="bottom-action-cards-grid">
                        <div class="bottom-card" onclick="gmSendPrompt('Show today\\'s tasks')">
                            <div class="bottom-card-icon blue-cal">📅</div>
                            <div class="bottom-card-content">
                                <div class="bottom-card-title">Today's Tasks</div>
                                <div class="bottom-card-sub">See your plan for today</div>
                            </div>
                        </div>

                        <div class="bottom-card" onclick="gmSendPrompt('I want to mark my tasks as done')">
                            <div class="bottom-card-icon green-plus">➕</div>
                            <div class="bottom-card-content">
                                <div class="bottom-card-title">Update Progress</div>
                                <div class="bottom-card-sub">Mark tasks as done</div>
                            </div>
                        </div>

                        <div class="bottom-card" onclick="gmSendPrompt('I couldn\\'t study for the last two days because college got hectic')">
                            <div class="bottom-card-icon red-replan">🔄</div>
                            <div class="bottom-card-content">
                                <div class="bottom-card-title">Replan</div>
                                <div class="bottom-card-sub">Adjust your plan</div>
                            </div>
                        </div>

                        <div class="bottom-card" onclick="gmSendPrompt('Give me my weekly review and consistency insights')">
                            <div class="bottom-card-icon blue-chart">📊</div>
                            <div class="bottom-card-content">
                                <div class="bottom-card-title">Weekly Review</div>
                                <div class="bottom-card-sub">Get your insights</div>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- ================= RIGHT COLUMN: CARDS ================= -->
                <aside class="gm-right-column">
                    
                    <!-- CARD 1: CURRENT GOAL -->
                    <div class="dash-white-card current-goal-card">
                        <div class="dash-card-header">
                            <span class="dash-card-title">Current Goal</span>
                            <a href="#" class="dash-card-link" onclick="gmNavigate('goals'); return false;">View All &rarr;</a>
                        </div>

                        <div class="goal-identity-row">
                            <img src="{python_logo_url}" class="python-badge-icon" alt="Python Logo" />
                            <div class="goal-name-heading">{goal_title}</div>
                            <div class="status-pill-ontrack">{goal_status}</div>
                        </div>

                        <div class="goal-progress-section">
                            <div class="progress-track-bg">
                                <div class="progress-fill-active" style="width: {progress_pct}%;"></div>
                            </div>
                            <span class="progress-pct-bold">{progress_pct}%</span>
                        </div>

                        <div class="goal-meta-trio">
                            <div class="meta-column-box">
                                <span class="meta-label-tiny">📅 Deadline</span>
                                <span class="meta-val-strong">{deadline_str}</span>
                            </div>
                            <div class="meta-column-box">
                                <span class="meta-label-tiny">🎯 Time Left</span>
                                <span class="meta-val-strong">{days_left} days</span>
                            </div>
                            <div class="meta-column-box">
                                <span class="meta-label-tiny">📋 Milestones</span>
                                <span class="meta-val-strong">{milestones_done} / {milestones_total} completed</span>
                            </div>
                        </div>
                    </div>

                    <!-- CARD 2: TODAY'S TASKS -->
                    <div class="dash-white-card todays-tasks-card">
                        <div class="dash-card-header">
                            <span class="dash-card-title">Today's Tasks</span>
                            <a href="#" class="dash-card-link" onclick="gmNavigate('goals'); return false;">See All &rarr;</a>
                        </div>

                        <div class="tasks-vertical-list">
                            {''.join(tasks_html)}
                        </div>
                    </div>

                    <!-- CARD 3: WEEKLY PROGRESS -->
                    <div class="dash-white-card weekly-progress-card">
                        <div class="dash-card-header">
                            <span class="dash-card-title">Weekly Progress</span>
                            <span class="consistency-percentage-badge">{consistency_pct}% <span style="font-weight:500; font-size:11px; color:#687B6F;">Consistency</span></span>
                        </div>

                        <div class="weekly-bars-chart">
                            <div class="bar-column-item">
                                <div class="bar-tube-fill" style="height: 38%;"></div>
                                <span class="bar-day-name">Mon</span>
                            </div>
                            <div class="bar-column-item">
                                <div class="bar-tube-fill" style="height: 52%;"></div>
                                <span class="bar-day-name">Tue</span>
                            </div>
                            <div class="bar-column-item">
                                <div class="bar-tube-fill" style="height: 68%;"></div>
                                <span class="bar-day-name">Wed</span>
                            </div>
                            <div class="bar-column-item">
                                <div class="bar-tube-fill" style="height: 92%;"></div>
                                <span class="bar-day-name">Thu</span>
                            </div>
                            <div class="bar-column-item">
                                <div class="bar-tube-fill" style="height: 48%;"></div>
                                <span class="bar-day-name">Fri</span>
                            </div>
                            <div class="bar-column-item">
                                <div class="bar-tube-fill" style="height: 98%;"></div>
                                <span class="bar-day-name">Sat</span>
                            </div>
                            <div class="bar-column-item">
                                <div class="bar-tube-fill" style="height: 62%;"></div>
                                <span class="bar-day-name">Sun</span>
                            </div>
                        </div>
                    </div>

                    <!-- CARD 4: MOTIVATION FOR YOU -->
                    <div class="dash-white-card motivation-peach-card">
                        <div class="peach-quote-mark">❝</div>
                        <p class="peach-quote-text">
                            "You don't have to be great to start, but you have to start to be great."
                        </p>
                        <p class="peach-quote-author">— Zig Ziglar</p>
                    </div>

                </aside>
            </div>
        </main>
    </div>
    """
