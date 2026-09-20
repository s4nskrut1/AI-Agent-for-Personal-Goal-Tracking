"""
GoalMate — Light Theme CSS matching Master Reference (media_1789749154473.jpg).
Vibrant unfaded images, no quotes overlay, SVG graphs, and interactive past-task editing.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
ASSET_DIR = f"{BASE_DIR}/assets"

GOALMATE_CSS = f"""
/* ── RESET & GLOBAL (NO SCROLLBARS, FULLY SCROLLABLE) ───────── */
* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    -ms-overflow-style: none !important;  /* IE and Edge */
    scrollbar-width: none !important;  /* Firefox */
}}

*::-webkit-scrollbar,
body::-webkit-scrollbar,
div::-webkit-scrollbar,
html::-webkit-scrollbar,
textarea::-webkit-scrollbar,
.gradio-container::-webkit-scrollbar {{
    display: none !important;
    width: 0px !important;
    height: 0px !important;
    background: transparent !important;
}}

body, .gradio-container {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    background: #F8F9FA !important;
    color: #1E2538 !important;
    min-height: 100vh;
}}

.gradio-container > .main > div {{ padding: 0 !important; }}

/* ── THREE COLUMN APP SHELL ────────────────────────────────── */
#gm-shell {{
    display: flex;
    height: 100vh;
    max-height: 100vh;
    overflow: hidden;
    background: #F8F9FA;
}}

/* ── COLUMN 1: LEFT SIDEBAR WITH VIBRANT BACKGROUND IMAGE ──── */
#gm-sidebar {{
    width: 230px;
    min-width: 230px;
    max-width: 230px;
    background-color: #FFFFFF;
    background-image: linear-gradient(180deg, 
        rgba(255, 255, 255, 0.78) 0%, 
        rgba(255, 255, 255, 0.25) 35%, 
        rgba(255, 255, 255, 0.05) 65%, 
        rgba(255, 255, 255, 0.65) 100%), 
        url('/gradio_api/file={ASSET_DIR}/sidebar_hinata_new.png');
    background-size: cover;
    background-position: bottom center;
    border-right: 1px solid #EAECEF;
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow-y: auto;
    overflow-x: hidden;
    position: relative;
    box-shadow: 2px 0 8px rgba(0,0,0,0.03);
}}

.sidebar-brand {{
    padding: 18px 16px 14px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(6px);
    border-bottom: 1px solid rgba(234, 236, 239, 0.6);
}}

.sidebar-logo {{
    width: 38px;
    height: 38px;
    border-radius: 50%;
    object-fit: cover;
    box-shadow: 0 2px 6px rgba(242, 123, 53, 0.25);
}}

.brand-text h2 {{
    font-size: 1.2rem;
    font-weight: 800;
    color: #1E2538;
    letter-spacing: -0.02em;
    line-height: 1.1;
}}

.brand-text span {{
    font-size: 0.68rem;
    color: #718096;
    display: block;
    margin-top: 2px;
}}

.sidebar-nav {{
    padding: 10px 12px 0 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}}

.nav-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    border-radius: 10px;
    font-size: 0.88rem;
    font-weight: 600;
    color: #4A5568;
    text-decoration: none;
    transition: all 0.15s ease;
    border: none;
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(4px);
    width: 100%;
    text-align: left;
    cursor: pointer;
}}

.nav-item:hover {{
    background: rgba(255, 240, 230, 0.9);
    color: #F27B35;
}}

.nav-item.active {{
    background: #FFF0E6 !important;
    color: #F27B35 !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 4px rgba(242, 123, 53, 0.15);
}}

.sidebar-goals-accordion {{
    display: flex;
    flex-direction: column;
    padding: 4px 12px 6px 12px;
    gap: 3px;
    animation: fadeInSlide 0.2s ease;
}}

@keyframes fadeInSlide {{
    from {{ opacity: 0; transform: translateY(-4px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.goals-count-badge {{
    background: #EDF2F7;
    color: #4A5568;
    font-size: 0.68rem;
    font-weight: 700;
    padding: 1px 7px;
    border-radius: 999px;
    margin-left: 6px;
}}

.goals-chevron {{
    color: #A0AEC0;
    font-size: 0.65rem;
    margin-left: auto;
    font-weight: bold;
}}

.sidebar-goals-section {{
    padding: 6px 12px;
    display: flex;
    flex-direction: column;
    gap: 3px;
}}

.sidebar-goal-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(4px);
    border-radius: 8px;
    padding: 6px 8px 6px 14px;
    margin-bottom: 2px;
    transition: all 0.15s ease;
}}

.sidebar-goal-row:hover {{
    background: #FFF0E6;
}}

.sidebar-goal-link {{
    font-size: 0.8rem;
    font-weight: 600;
    color: #4A5568;
    cursor: pointer;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
}}

.sidebar-goal-row:hover .sidebar-goal-link {{
    color: #F27B35;
}}

.sidebar-del-btn {{
    background: none;
    border: none;
    color: #CBD5E0;
    font-size: 0.8rem;
    cursor: pointer;
    padding: 2px 4px;
    border-radius: 4px;
    transition: all 0.12s;
}}

.sidebar-del-btn:hover {{
    color: #E53E3E;
    background: rgba(229, 62, 62, 0.1);
}}

/* ── COLUMN 2: MAIN DASHBOARD ──────────────────────────────── */
#gm-main {{
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
    background: #F8F9FA;
}}

#gm-center {{
    flex: 1;
    overflow-y: auto;
    padding: 0 22px 24px 22px;
}}

/* ── HERO BANNER (VIBRANT, NO QUOTE OVERLAY) ──────────────── */
.hero-card {{
    background: #FFFFFF;
    border: 1px solid #EAECEF;
    border-radius: 16px;
    margin-top: 16px;
    margin-bottom: 16px;
    overflow: hidden;
    position: relative;
    min-height: 130px;
    display: flex;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}}

.hero-bg-img {{
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: left center;
    opacity: 1.0 !important;
}}

.hero-overlay {{
    position: absolute;
    left: 0; top: 0; width: 100%; height: 100%;
    background: linear-gradient(90deg, 
        rgba(255,255,255,0) 45%, 
        rgba(255,255,255,0.7) 75%, 
        rgba(255,255,255,0.92) 100%);
}}

.hero-content {{
    position: relative;
    z-index: 2;
    margin-left: auto;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-end;
    text-align: right;
}}

.hero-date-badge {{
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(4px);
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.74rem;
    color: #718096;
    font-weight: 600;
    margin-bottom: 6px;
}}

.hero-greeting-title {{
    font-size: 1.25rem;
    color: #1A202C;
    font-weight: 800;
    letter-spacing: -0.01em;
}}

/* ── 2-COLUMN DASHBOARD GRID ───────────────────────────────── */
.dash-grid-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 16px;
}}

/* ── CARD STYLING ──────────────────────────────────────────── */
.gm-card {{
    background: #FFFFFF;
    border: 1px solid #EAECEF;
    border-radius: 16px;
    padding: 16px 18px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}

.clickable-card {{
    cursor: pointer;
}}

.clickable-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}}

.card-top-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}}

.card-title-wrap {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.92rem;
    font-weight: 700;
    color: #1E2538;
}}

.card-header-link {{
    font-size: 0.78rem;
    font-weight: 600;
    color: #718096;
    text-decoration: none;
    cursor: pointer;
    transition: color 0.12s;
}}

.card-header-link:hover {{
    color: #F27B35;
}}

/* ── CURRENT GOAL CARD ─────────────────────────────────────── */
.goal-title-h {{
    font-size: 1.15rem;
    font-weight: 800;
    color: #1A202C;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
}}

.goal-meta-subtitle {{
    font-size: 0.78rem;
    color: #A0AEC0;
    margin-bottom: 14px;
}}

.progress-track-outer {{
    background: #EDF2F7;
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
    position: relative;
    margin-bottom: 14px;
}}

.progress-bar-fill-orange {{
    background: linear-gradient(90deg, #F27B35 0%, #FF9554 100%);
    height: 100%;
    border-radius: 999px;
    transition: width 0.4s ease;
}}

.goal-stats-pill-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}}

.goal-stat-pill {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: #F7FAFC;
    border: 1px solid #EDF2F7;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 0.78rem;
    color: #4A5568;
    font-weight: 600;
}}

/* ── QUICK STATS 2x2 GRID ─────────────────────────────────── */
.quick-stats-2x2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}}

.qs-box {{
    background: #F7FAFC;
    border: 1px solid #EDF2F7;
    border-radius: 12px;
    padding: 12px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}}

.qs-icon-wrap {{
    width: 34px;
    height: 34px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
}}

.qs-val {{
    font-size: 1.25rem;
    font-weight: 800;
    color: #1A202C;
    line-height: 1.1;
}}

.qs-lbl {{
    font-size: 0.72rem;
    color: #718096;
    font-weight: 500;
    margin-top: 2px;
}}

/* ── TASK CHECKBOXES & RETROACTIVE EDITING ─────────────────── */
.task-row-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 9px 8px;
    border-radius: 8px;
    border-bottom: 1px solid #F1F3F5;
    transition: background 0.12s;
}}

.task-row-item:hover {{
    background: #F7FAFC;
}}

.task-row-item:last-child {{
    border-bottom: none;
}}

.task-check-circle {{
    width: 22px;
    height: 22px;
    border-radius: 6px;
    border: 2px solid #CBD5E0;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 0.8rem;
    font-weight: bold;
    color: #FFFFFF;
    transition: all 0.15s ease;
    flex-shrink: 0;
    user-select: none;
}}

.task-check-circle:hover {{
    border-color: #10B981;
    background: rgba(16, 185, 129, 0.1);
}}

.task-check-circle.completed {{
    background: #10B981 !important;
    border-color: #10B981 !important;
}}

.task-title-text {{
    flex: 1;
    font-size: 0.86rem;
    color: #2D3748;
    font-weight: 500;
    cursor: pointer;
}}

.task-title-text.completed {{
    text-decoration: line-through;
    color: #A0AEC0;
}}

.task-tag-badge {{
    background: #EBF8FF;
    color: #3182CE;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 6px;
}}

.task-time-meta {{
    font-size: 0.74rem;
    color: #A0AEC0;
    white-space: nowrap;
}}

/* ── TASK CATEGORY HEADERS (ONGOING, PAST, UPCOMING) ───────── */
.task-scroll-box {{
    max-height: 255px;
    overflow-y: auto;
    padding-right: 4px;
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
}}

.task-sec-badge {{
    font-size: 0.73rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin: 12px 0 6px 2px;
    display: flex;
    align-items: center;
    gap: 6px;
}}

.task-sec-badge.ongoing {{
    color: #DD6B20;
}}

.task-sec-badge.past {{
    color: #718096;
}}

.task-sec-badge.upcoming {{
    color: #3182CE;
}}

/* ── WEEKLY PROGRESS VERTICAL BARS ─────────────────────────── */
.weekly-bars-container {{
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    height: 140px;
    padding: 10px 6px 4px 6px;
    gap: 8px;
}}

.w-col {{
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    height: 100%;
    gap: 6px;
}}

.w-pct-label {{
    font-size: 0.72rem;
    font-weight: 700;
    color: #4A5568;
    min-height: 16px;
    line-height: 16px;
}}

.w-track {{
    width: 24px;
    height: 90px;
    background: #F1F5F9;
    border-radius: 999px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    overflow: hidden;
    position: relative;
}}

.w-fill {{
    width: 100%;
    background: linear-gradient(180deg, #FF9554 0%, #F27B35 100%);
    border-radius: 999px;
    transition: height 0.4s ease;
}}

.w-day-label {{
    font-size: 0.74rem;
    font-weight: 600;
    color: #718096;
}}

.w-col.today .w-day-label {{
    color: #F27B35;
    font-weight: 800;
}}

.w-col.today .w-track {{
    background: #FFF0E6;
    box-shadow: 0 0 0 1.5px rgba(242, 123, 53, 0.25);
}}

/* ── MILESTONES CARD ───────────────────────────────────────── */
.milestones-list {{
    display: flex;
    flex-direction: column;
    gap: 4px;
}}

.milestone-row-item {{
    display: flex;
    align-items: center;
    padding: 8px 4px;
    border-radius: 8px;
    border-bottom: 1px solid #F8F9FA;
    transition: background 0.12s ease;
}}

.milestone-row-item:last-child {{
    border-bottom: none;
}}

.milestone-row-item:hover {{
    background: #F7FAFC;
}}

.ms-badge {{
    width: 24px;
    height: 24px;
    min-width: 24px;
    border-radius: 50%;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.74rem;
    font-weight: 700;
    flex-shrink: 0;
}}

.ms-title {{
    flex: 1;
    font-size: 0.84rem;
    font-weight: 600;
    color: #2D3748;
    margin-left: 10px;
    margin-right: 8px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.ms-ratio {{
    font-size: 0.76rem;
    font-weight: 600;
    color: #718096;
    width: 34px;
    text-align: right;
    margin-right: 10px;
    flex-shrink: 0;
}}

.ms-track {{
    width: 80px;
    min-width: 80px;
    height: 6px;
    background: #EDF2F7;
    border-radius: 999px;
    overflow: hidden;
    flex-shrink: 0;
}}

.ms-fill {{
    height: 100%;
    border-radius: 999px;
    transition: width 0.3s ease;
}}

.ms-pct {{
    font-size: 0.74rem;
    font-weight: 700;
    color: #718096;
    width: 38px;
    text-align: right;
    margin-left: 8px;
    flex-shrink: 0;
}}

/* ── RECENT ACTIVITY CARD ──────────────────────────────────── */
.activity-list {{
    display: flex;
    flex-direction: column;
    gap: 4px;
}}

.activity-row-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 6px;
    border-radius: 8px;
    border-bottom: 1px solid #F8F9FA;
    transition: background 0.12s ease;
}}

.activity-row-item:last-child {{
    border-bottom: none;
}}

.activity-row-item:hover {{
    background: #F7FAFC;
}}

.act-icon-box {{
    width: 32px;
    height: 32px;
    min-width: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    font-weight: 700;
    flex-shrink: 0;
}}

.act-details {{
    flex: 1;
    min-width: 0;
}}

.act-title {{
    font-size: 0.82rem;
    font-weight: 700;
    color: #1A202C;
    line-height: 1.2;
}}

.act-desc {{
    font-size: 0.73rem;
    color: #718096;
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.act-time {{
    font-size: 0.72rem;
    color: #A0AEC0;
    font-weight: 500;
    white-space: nowrap;
    margin-left: 8px;
}}

/* ── DAY-WISE PROGRESS GRAPH CARD ──────────────────────────── */
.graph-badge-chip {{
    background: #FFF0E6;
    color: #F27B35;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 6px;
    border: 1px solid rgba(242, 123, 53, 0.2);
}}

.graph-metric-strip {{
    display: flex;
    align-items: center;
    justify-content: space-around;
    background: #F8F9FA;
    border: 1px solid #EDF2F7;
    border-radius: 8px;
    padding: 6px 12px;
    margin-bottom: 8px;
}}

.graph-metric-col {{
    text-align: center;
}}

.graph-metric-val {{
    font-size: 0.95rem;
    font-weight: 800;
    color: #1A202C;
    line-height: 1.1;
}}

.graph-metric-lbl {{
    font-size: 0.66rem;
    font-weight: 600;
    color: #718096;
    margin-top: 1px;
}}

.svg-progress-wrap {{
    width: 100%;
    position: relative;
}}

/* ── MILESTONES STEPPER ROADMAP ────────────────────────────── */
.stepper-container {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 8px 8px 8px;
    position: relative;
}}

.step-node {{
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    z-index: 2;
}}

.step-circle {{
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 800;
    color: #FFFFFF;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}}

.step-circle.done {{
    background: #10B981;
}}

.step-circle.active {{
    background: #F27B35;
    box-shadow: 0 0 0 4px rgba(242, 123, 53, 0.2);
}}

.step-circle.pending {{
    background: #E2E8F0;
    color: #718096;
}}

.step-label {{
    font-size: 0.72rem;
    font-weight: 700;
    color: #4A5568;
    margin-top: 6px;
    max-width: 80px;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.step-connector {{
    flex: 1;
    height: 3px;
    background: #E2E8F0;
    margin: 0 -8px 18px -8px;
    position: relative;
    z-index: 1;
}}

.step-connector.done {{
    background: #10B981;
}}

/* ── DELETE GOAL BUTTON ────────────────────────────────────── */
.btn-delete-goal {{
    background: #FFF5F5;
    border: 1px solid #FEB2B2;
    color: #E53E3E;
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 0.8rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.15s ease;
    display: flex;
    align-items: center;
    gap: 6px;
}}

.btn-delete-goal:hover {{
    background: #E53E3E;
    color: #FFFFFF;
}}

/* ── COLUMN 3: AI COACH PANEL ──────────────────────────────── */
#gm-coach {{
    width: 340px;
    min-width: 340px;
    max-width: 340px;
    background: #FFFFFF;
    border-left: 1px solid #EAECEF;
    display: flex;
    flex-direction: column;
    height: 100vh;
}}

.coach-header-bar {{
    padding: 16px 18px 12px 18px;
    border-bottom: 1px solid #EAECEF;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.coach-info-left {{
    display: flex;
    align-items: center;
    gap: 10px;
}}

.coach-avatar-img {{
    width: 36px;
    height: 36px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #F27B35;
}}

.coach-name-title {{
    font-size: 0.95rem;
    font-weight: 800;
    color: #1A202C;
}}

.coach-status-green {{
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.72rem;
    color: #10B981;
    font-weight: 700;
}}

.status-dot-pulse {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #10B981;
}}

/* Gradio Chatbot */
#coach-chatbot {{
    flex: 1 !important;
    border: none !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}}

#coach-chatbot .message.user {{
    background: #EBF8FF !important;
    color: #2B6CB0 !important;
    border-radius: 14px 14px 2px 14px !important;
    font-weight: 500 !important;
    font-size: 0.86rem !important;
}}

#coach-chatbot .message.bot {{
    background: #F7FAFC !important;
    color: #2D3748 !important;
    border-radius: 14px 14px 14px 2px !important;
    border: 1px solid #EDF2F7 !important;
    font-size: 0.86rem !important;
    line-height: 1.45 !important;
}}

/* Coach Input Bar */
.coach-input-container {{
    padding: 12px 14px 16px 14px;
    border-top: 1px solid #EAECEF;
    display: flex;
    gap: 8px;
    align-items: center;
}}

#coach-input textarea {{
    border: 1px solid #E2E8F0 !important;
    border-radius: 20px !important;
    padding: 10px 16px !important;
    font-size: 0.85rem !important;
    resize: none !important;
    box-shadow: none !important;
}}

#coach-input textarea:focus {{
    border-color: #F27B35 !important;
}}

#coach-send-btn {{
    width: 40px !important;
    height: 40px !important;
    min-width: 40px !important;
    border-radius: 50% !important;
    background: #F27B35 !important;
    border: none !important;
    color: #FFFFFF !important;
    font-size: 1rem !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
}}

/* Quick Task Reschedule Pills */
.task-reorder-actions {{
    display: flex;
    align-items: center;
    gap: 6px;
    margin-left: 6px;
}}

.btn-reschedule-quick {{
    background: #F7FAFC;
    border: 1px solid #E2E8F0;
    color: #718096;
    font-size: 0.68rem;
    font-weight: 700;
    padding: 3px 7px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.12s ease;
    white-space: nowrap;
}}

.btn-reschedule-quick:hover {{
    background: #FFF0E6;
    border-color: #F27B35;
    color: #F27B35;
    transform: translateY(-1px);
}}

/* 1-Month Compact Heatmap */
.compact-heatmap-wrap {{
    background: #FFFFFF;
    border-radius: 14px;
    padding: 4px 2px;
}}

/* Clean Analytics View */
.analytics-metric-box {{
    background: #F8F9FA;
    border: 1px solid #EDF2F7;
    border-radius: 12px;
    padding: 12px 14px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}

/* Sidebar User Footer */
.sidebar-user-footer {{
    margin-top: auto;
    padding: 10px 14px;
    background: rgba(247, 250, 252, 0.85);
    border: 1px solid #EDF2F7;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.15s ease;
}}

.sidebar-user-footer:hover {{
    background: #FFF0E6;
    border-color: #F27B35;
}}

/* Global Cleanups */
footer {{ display: none !important; }}
.gradio-container {{ max-width: 100% !important; }}
"""
