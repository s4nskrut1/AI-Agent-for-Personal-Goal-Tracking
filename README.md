# 🌱 GoalMate — Autonomous AI Personal Goal Tracking System

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Gradio UI](https://img.shields.io/badge/Frontend-Gradio%206.0-orange.svg)](https://gradio.app/)
[![LLM](https://img.shields.io/badge/LLM-Google%20Gemini-4285F4.svg)](https://aistudio.google.com/)
[![Security](https://img.shields.io/badge/Auth-JWT%20%2B%20Bcrypt-critical.svg)](#-authentication--security)
[![Database](https://img.shields.io/badge/Storage-SQLite%20%2B%20SQLAlchemy-lightgrey.svg)](https://sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **GoalMate** is an end-to-end, academic and hackathon-grade **Autonomous AI Personal Goal Coach**. 
> Unlike passive todo list apps or simple chat wrappers that offer generic motivational quotes, GoalMate observes user progress, identifies when a user is falling behind or progressing faster than expected, diagnoses the underlying cause (missed days, academic crunch, shifted capacity), and dynamically adapts the schedule in the database without cognitive cramming.

---

## 📑 Table of Contents
1. [Core Product Idea & Agent vs. Chatbot](#-core-product-idea--agent-vs-chatbot)
2. [Hero USP: Dynamic Adaptive Replanning](#-hero-usp-dynamic-adaptive-replanning)
3. [System Architecture Diagram](#-system-architecture-diagram)
4. [API Keys & Configuration Guide](#-api-keys--configuration-guide)
5. [Directory Structure](#-directory-structure)
6. [Authentication & Security](#-authentication--security)
7. [Installation & Setup](#-installation--setup)
8. [Running the Application](#-running-the-application)
9. [15-Step Viva & Hackathon Demo Script](#-15-step-viva--hackathon-demo-script)
10. [Visual Design & Assets](#-visual-design--assets)
11. [Architectural Defense & FAQ](#-architectural-defense--faq)

---

## 💡 Core Product Idea & Agent vs. Chatbot

### Why GoalMate is an AI Agent, NOT a Chatbot

Traditional productivity software falls into two flawed extremes:
1. **Passive Todo Lists & Trackers**: Require tedious manual entry, lack intelligence on realistic pacing, and induce guilt when tasks inevitably slip.
2. **Standard LLM Chatbots**: Provide boilerplate markdown advice without persistent memory, cannot mutate real databases deterministically, and cannot recalculate time constraints when life happens.

**GoalMate implements a complete autonomous agentic loop:**
$$\text{Observe} \longrightarrow \text{Reason} \longrightarrow \text{Plan} \longrightarrow \text{Act} \longrightarrow \text{Observe} \longrightarrow \text{Adapt} \longrightarrow \text{Re-plan}$$

| Dimension | Generic LLM Chatbot | GoalMate Autonomous Agent |
| :--- | :--- | :--- |
| **State Persistence** | Ephemeral chat window only | Relational SQLite database with ACID guarantees & foreign key cascades |
| **Authentication** | None / Single-tenant mock | Real bcrypt password hashing + signed JWT tokens with expiration |
| **Action Execution** | Hallucinates markdown checkboxes | Executes validated Python tools (`create_goal`, `create_task`, `complete_task`) |
| **Constraint Handling** | Ignores actual daily availability | Enforces strict daily minute capacity ceilings (e.g. 60m/day) |
| **Schedule Slips** | Says *"Try harder tomorrow!"* | Diagnoses blockers, calculates lag, redistributes backlog, smooths workload |
| **Data Validation** | Raw text without guarantees | Pydantic v2 schemas validating every request, response, and tool output |
| **Offline Resilience** | Completely breaks if API key expires | Dual-engine with intelligent offline heuristic planner ensuring 100% demo uptime |

---

## ⚡ Hero USP: Dynamic Adaptive Replanning

When a user reports:
> *"I couldn't study for the last two days because college got hectic."*

GoalMate doesn't offer empty platitudes. Instead:
1. **Compares Expected vs. Actual Pace**: Detects that 2 daily milestones slipped.
2. **Diagnoses Context**: Recognizes academic crunch from conversation context and persists it to user memory.
3. **Preserves Deadline**: Retains the original target milestone completion date where mathematically feasible.
4. **Prevents Cognitive Cramming**: Smoothly spreads the unfinished tasks across the upcoming 3–6 days while capping tomorrow's restart day at **45 minutes** to rebuild psychological momentum.
5. **Commits Database Mutations**: Updates `due_date` and sets `status = 'rescheduled'` with updated timestamps in SQLite.
6. **Visibly Refreshes Dashboard**: Today's task list, progress percentage, streak, and weekly consistency bar chart update in real-time.

---

## 📊 System Architecture Diagram

```mermaid
flowchart TD
    subgraph Client [Gradio 6.0 Frontend + Custom CSS]
        AuthView[Authentication Views\nLogin / Register / Forgot Password]
        DashboardView[3-Column SaaS Dashboard\nSidebar | AI Coach Chat | Dashboard Cards]
        GoalsView[My Goals & Milestone Roadmaps]
        ProgressView[Telemetry & Consistency Analytics]
        InsightsView[Behavioral AI Insights]
    end

    subgraph BackendAPI [FastAPI Backend]
        AuthRouter[/api/auth - JWT & Bcrypt]
        GoalRouter[/api/goals - Goals & Milestones]
        TaskRouter[/api/tasks - Daily Tasks & Status]
        ProgressRouter[/api/progress - Analytics & Replanning]
    end

    subgraph ServiceLayer [Business Logic Services]
        AuthService[Auth Service\nToken encoding/decoding, passlib]
        GoalService[Goal Service\nCRUD & Multi-user isolation]
        TaskService[Task Service\nToday's tasks, date shifts]
        ProgressService[Progress Service\nStreak & pace calculation]
        ResearchService[Research Service\nTavily Web Search]
    end

    subgraph AgentLayer [Autonomous AI Agent]
        AgentOrchestrator[Agent Orchestrator\nObserve -> Reason -> Route -> Act -> Adapt]
        LLMClient[Isolated Gemini LLM Client\nagent/llm.py]
        ToolSuite[Deterministic Tool Suite\ncreate_goal, complete_task, replan_goal, etc.]
        ReplannerEngine[Adaptive Replanner\nBacklog smoothing without cramming]
    end

    subgraph StorageLayer [Persistence Layer]
        SQLAlchemyORM[SQLAlchemy ORM Models]
        SQLiteDB[(SQLite Database\ndata/goalmate.db)]
    end

    Client <--> BackendAPI
    BackendAPI <--> ServiceLayer
    ServiceLayer <--> AgentLayer
    AgentLayer <--> ToolSuite
    ToolSuite <--> SQLAlchemyORM
    ServiceLayer <--> SQLAlchemyORM
    SQLAlchemyORM <--> SQLiteDB
    AgentLayer <--> ResearchService
```

---

## 🔑 API Keys & Configuration Guide

### 1. Key Requirements Summary
| Environment Variable | Status | Purpose | Where to Get |
| :--- | :---: | :--- | :--- |
| **`GEMINI_API_KEY`** | **REQUIRED** | Powers core AI Goal Coach, goal decomposition, planning & adaptive replanning | [Google AI Studio](https://aistudio.google.com/) |
| **`JWT_SECRET_KEY`** | **REQUIRED** | Cryptographic secret for signing and verifying user session JWT tokens | Generate via `openssl rand -hex 32` or any 64-char string |
| **`TAVILY_API_KEY`** | **OPTIONAL** | Enables live web research for courses, roadmaps & coding projects | [Tavily AI](https://tavily.com/) |

### 2. Location of the `.env` File
Create `.env` in the root of the project:
```text
C:\Users\SANSKRUTI\.gemini\antigravity\scratch\GoalMate\.env
```

```env
# 1. PRIMARY LLM: Google Gemini API Key
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
GEMINI_MODEL=gemini-2.5-flash

# 2. AUTHENTICATION: JWT Secret Key
JWT_SECRET_KEY=goalmate_academic_hackathon_super_secret_jwt_key_2026_x99
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 3. WEB RESEARCH: Tavily API Key (Optional)
TAVILY_API_KEY=YOUR_TAVILY_API_KEY_HERE

# 4. DATABASE & SERVER
DATABASE_URL=sqlite:///./data/goalmate.db
PORT=7860
HOST=127.0.0.1
```

---

## 📁 Directory Structure

```text
GoalMate/
├── app.py                     # Entry point: FastAPI server mounting Gradio app
├── requirements.txt           # Verified clean dependencies
├── README.md                  # Academic & hackathon-grade documentation
├── .env.example               # Template for environment variables
├── .env                       # Local secrets (gitignored)
├── .gitignore                 # Ignores .env, __pycache__, *.db
├── test_full_system.py        # Comprehensive 8-stage automated test suite
│
├── backend/
│   ├── __init__.py
│   ├── database.py            # SQLAlchemy engine, sessionmaker, Base, init_db()
│   ├── models.py              # SQLAlchemy ORM models (User, Goal, Milestone, Task, ProgressLog)
│   ├── schemas.py             # Pydantic v2 schemas for API requests & responses
│   ├── auth.py                # Password hashing (bcrypt) & JWT token handlers
│   └── routes.py              # FastAPI REST endpoints with user authentication
│
├── agent/
│   ├── __init__.py
│   ├── llm.py                 # Isolated Gemini LLM client (swappable provider)
│   ├── prompts.py             # System instructions for GoalMate agent & planner
│   ├── tools.py               # Deterministic tool suite callable by LLM
│   ├── replanner.py           # Adaptive replanning engine (smoothing backlogs)
│   └── agent.py               # Core agent loop: Observe -> Reason -> Act -> Adapt
│
├── services/
│   ├── __init__.py
│   ├── goal_service.py        # Goal & milestone business logic with user isolation
│   ├── task_service.py        # Task CRUD, today's tasks, completion
│   ├── progress_service.py    # Progress telemetry, streak & consistency calculation
│   └── research_service.py    # Optional Tavily live web research + curated fallback
│
├── ui/
│   ├── __init__.py
│   ├── styles.py              # Custom CSS rules & base64 image loader
│   ├── styles.css             # Base stylesheet (Cream & Sage Green aesthetic)
│   ├── auth_ui.py             # Login, Register, and Forgot Password UI components
│   └── components.py          # Visual HTML cards, metrics, and Plotly charts
│
├── assets/
│   ├── hiker.png              # Hiker on mountain cliff at sunrise
│   ├── mountain_scene.png     # Mountain landscape over lake (Auth banner)
│   ├── ai_robot.png           # Cute AI robot coach holding a sprout
│   ├── auth_mockup.jpg        # Design reference for auth
│   └── dashboard_mockup.jpg   # Design reference for dashboard
│
└── data/
    └── goalmate.db            # SQLite database file
```

---

## 🔒 Authentication & Security

- **Bcrypt Password Hashing**: Plaintext passwords are never stored. Passwords are salted and hashed via `passlib[bcrypt]`.
- **JWT Token Authentication**: Signed HMAC-SHA256 tokens contain `sub` (user ID), `email`, `exp`, and `iat`.
- **Strict Multi-Tenant Isolation**: Every query (`Goal`, `Milestone`, `Task`, `ProgressLog`) filters by `user_id == current_user.id`. User A cannot view or mutate User B data.
- **Clean First-Run Experience**: New users begin with an empty workspace and add only the goals, tasks, and progress they choose to track.

---

## 🛠️ Installation & Setup

```bash
# 1. Clone repository
cd GoalMate

# 2. Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 3. Install verified dependencies
pip install -r requirements.txt

# 4. Copy environment configuration
cp .env.example .env
# Edit .env and insert your GEMINI_API_KEY
```

---

## 🚀 Running the Application

### Start Application Server:
```bash
python app.py
```
Open **`http://127.0.0.1:7860`** in your browser.

### Run Automated System Verification:
```bash
python test_full_system.py
```

---

## 🎬 15-Step Viva & Hackathon Demo Script

For your college presentation, follow these exact 15 steps to showcase the full depth of GoalMate:

1. **Boot Screen**: Open `http://127.0.0.1:7860`. Highlight the **Split-Banner Authentication** view matching Mockup #2 with the mountain scene illustration and rating badges.
2. **User Registration**: Click **Create Account**, enter name (e.g. `Alex Rivera`), email, and password. Point out that passwords are hashed via **bcrypt** and an authenticated **JWT token** is issued.
3. **Login Transition**: Click **Sign In**. Watch the UI smoothly reveal the **3-Column SaaS Dashboard** matching Mockup #1.
4. **Top Header**: Highlight the personalized greeting *"Good Evening, Alex! 👋"*, the discipline quote pill, and the active **5-day streak** badge.
5. **Left Sidebar**: Show the GoalMate brand logo, the navigation links, the **Climber Art card** (*"Climb Higher Every Day"*) using `assets/hiker.png`, and the motivational quote card.
6. **Center AI Coach**: Point out the cute robot avatar from `assets/ai_robot.png` and the *"Online • Adaptive Planning Active"* status pill.
7. **Interactive Quick Chips**: Point out the clickable chips beneath the chat: *"I'm ready for tomorrow! 🚀"*, *"Show Today's Tasks"*, *"Recommend Free Resources"*.
8. **Right Column Cards**: Show the **4 KPI cards** (Streak, Progress %, Health, Consistency), the **Current Goal** card with progress bar, and the **Today's Tasks** checklist.
9. **Interactive Task Completion**: Select a task from the Quick Complete dropdown and click **"✅ Done"**. Watch the streak increment, progress percentage rise to **62.5%**, and the AI coach celebrate in chat.
10. **The Hero Feature — Slipped Schedule Report**: Click the chip: *"I couldn't study for the last two days because college got hectic"*.
11. **Observe AI Diagnosis**: Watch GoalMate diagnose the missed days, acknowledge the college crunch with empathy, and explain the recovery strategy without guilt.
12. **Verify Workload Cap**: Show that tomorrow's restart day is capped at **<= 45 minutes** (one focused task) to rebuild momentum.
13. **Verify SQLite Database Mutation**: Show that subsequent tasks have been redistributed smoothly and their status updated to `rescheduled` in SQLite.
14. **Web Research via Tavily**: Ask *"Recommend the best free courses and practice sites for Python"*. Show how the research service retrieves curated or live web resources.
15. **Multi-User Isolation**: Sign out, create a second user (e.g. `Sam Smith`), and prove that Sam's database records are strictly isolated from Alex's.

---

## 🎨 Visual Design & Assets

The UI faithfully implements the **Cream & Sage Green** visual aesthetic from the reference designs:
- **Canvas Background**: Light cream (`#F8F9F5` / `#FBF9F4`)
- **Primary Accent**: Forest & Sage Green (`#2D6A4F`, `#22543D`, `#EAF4EE`)
- **Warm Highlights**: Peach & Amber (`#FFF5EC`, `#FFDCC3`, `#D97706`)
- **Typography**: Clean modern sans-serif with Playfair Display italic accents
- **Custom Graphic Assets**:
  - `assets/mountain_scene.png`: Mountain landscape over serene lake for Auth banner
  - `assets/hiker.png`: Climber reaching mountain summit for sidebar motivation
  - `assets/ai_robot.png`: Friendly AI robot coach avatar holding a sprout

---

## 🏛️ Architectural Defense & FAQ

### Q: Why SQLite instead of an external cloud database for the demo?
> **Answer**: SQLite requires zero local setup, has zero cloud credential dependencies, and supports full ACID transactions and foreign keys. It guarantees the application boots anywhere immediately, while the SQLAlchemy ORM makes migrating to PostgreSQL simply a 1-line change to `DATABASE_URL`.

### Q: How does GoalMate prevent hallucination during goal planning?
> **Answer**: All LLM outputs are parsed through structured JSON schemas. Tool calls are strictly deterministic Python functions that validate inputs using Pydantic v2 before persisting them to the database.

### Q: Why do you cap tomorrow's restart session at 45 minutes?
> **Answer**: Based on behavioral psychology and atomic habits research, schedule slips cause cognitive guilt and anxiety. Cramming overdue tasks into the next day leads to burnout and abandonment. Capping tomorrow's restart workload guarantees a quick win that rebuilds streak momentum.

---

## 📄 License
This project is open-source under the **MIT License**.
