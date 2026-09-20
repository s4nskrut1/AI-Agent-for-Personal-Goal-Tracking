"""
GoalMate — Application Entry Point.
FastAPI + Gradio unified architecture for instant interactive clicks,
live task checkboxes, goal switching, and agentic AI coaching.
"""
import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and not os.environ.get(k):
                        os.environ[k] = v
        print("[OK] Environment variables loaded from .env")
    else:
        print("[WARN] No .env file found. Gemini features may not work.")

load_env()

from backend.models import init_db
init_db()
print("[OK] Database initialized")

import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from backend.services import (
    complete_task as svc_complete_task,
    delete_goal as svc_delete_goal,
    reschedule_single_task as svc_reschedule_task,
    get_session
)
from backend.auth import authenticate_user, register_user, create_access_token
from ui.dashboard import build_app, JS_HEAD, render_full_dashboard
from ui.login import render_login_page
from ui.styles import GOALMATE_CSS

# 1. Initialize FastAPI app
f_app = FastAPI(title="GoalMate API")

# Static assets mount for GoalMate custom assets (mounted at /gm-assets to avoid conflicting with Gradio internal /assets)
if os.path.exists("assets"):
    f_app.mount("/gm-assets", StaticFiles(directory="assets"), name="gm_assets")
if os.path.exists("frontend/assets"):
    f_app.mount("/frontend/assets", StaticFiles(directory="frontend/assets"), name="frontend_assets")

# 2. Authentication and Navigation Endpoints
@f_app.get("/login", response_class=HTMLResponse)
async def get_login_page():
    return HTMLResponse(render_login_page())

@f_app.post("/api/auth/login")
async def api_login(req: Request):
    try:
        body = await req.json()
        email = body.get("email", "").strip()
        password = body.get("password", "")
        user = authenticate_user(email, password)
        if not user:
            return JSONResponse({"success": False, "error": "Invalid email or password"}, status_code=401)
        token = create_access_token(user.id, user.email)
        return JSONResponse({"success": True, "token": token, "user": {"id": user.id, "name": user.name, "email": user.email}})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@f_app.post("/api/auth/register")
async def api_register(req: Request):
    try:
        body = await req.json()
        email = body.get("email", "").strip()
        name = body.get("name", "").strip()
        password = body.get("password", "")
        user, err = register_user(email, name, password)
        if err:
            return JSONResponse({"success": False, "error": err}, status_code=400)
        token = create_access_token(user.id, user.email)
        return JSONResponse({"success": True, "token": token, "user": {"id": user.id, "name": user.name, "email": user.email}})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

# 3. Interactive API Endpoints for instant clicks
@f_app.post("/api/task/toggle")
async def api_toggle_task(req: Request):
    try:
        body = await req.json()
        task_id = int(body.get("task_id", 0))
        completed = bool(body.get("completed", True))
        task = svc_complete_task(task_id, completed)
        return JSONResponse({"success": True, "task_id": task_id, "status": "completed" if completed else "pending"})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@f_app.post("/api/task/reschedule")
async def api_reschedule_task(req: Request):
    try:
        from datetime import date, timedelta
        body = await req.json()
        task_id = int(body.get("task_id", 0))
        target = str(body.get("target", "today")).strip().lower()
        if target == "today":
            target_date = date.today()
        elif target == "tomorrow":
            target_date = date.today() + timedelta(days=1)
        else:
            target_date = date.fromisoformat(target)
        task = svc_reschedule_task(task_id, target_date)
        if task:
            return JSONResponse({"success": True, "task_id": task_id, "scheduled_date": str(target_date)})
        return JSONResponse({"success": False, "error": "Task not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@f_app.post("/api/goal/delete")
async def api_delete_goal(req: Request):
    try:
        body = await req.json()
        goal_id = int(body.get("goal_id", 0))
        success = svc_delete_goal(goal_id)
        return JSONResponse({"success": success, "goal_id": goal_id})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@f_app.get("/api/dashboard/html")
async def api_dashboard_html():
    try:
        sidebar, main = render_full_dashboard(selected_goal_id=None, current_view="dashboard")
        return JSONResponse({"sidebar": sidebar, "main": main})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@f_app.get("/api/progress/html")
async def api_progress_html():
    try:
        sidebar, main = render_full_dashboard(selected_goal_id=None, current_view="progress")
        return JSONResponse({"sidebar": sidebar, "main": main})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@f_app.get("/api/goal/{goal_id}/html")
async def api_goal_html(goal_id: int):
    try:
        sidebar, main = render_full_dashboard(selected_goal_id=goal_id, current_view="goal")
        return JSONResponse({"sidebar": sidebar, "main": main})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@f_app.get("/api/db/state")
async def api_db_state():
    db = get_session()
    try:
        from backend.models import Goal, Task
        g_count = db.query(Goal).count()
        t_done = db.query(Task).filter(Task.status == "completed").count()
        t_total = db.query(Task).count()
        return JSONResponse({"hash": f"{g_count}-{t_done}-{t_total}"})
    finally:
        db.close()

# 3. Build Gradio app & mount it onto FastAPI root
demo = build_app()
app = gr.mount_gradio_app(
    f_app,
    demo,
    path="/",
    allowed_paths=["frontend/assets/images", "assets"],
    head=JS_HEAD,
    css=GOALMATE_CSS
)

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  GoalMate -- Agentic AI Goal Management System")
    print("=" * 55)
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        print(f"  [OK] Gemini API key: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("  [WARN] No GEMINI_API_KEY -- AI Coach will use fallback mode")
    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"  -> Running on: http://{host}:{port}")
    print("=" * 55 + "\n")

    uvicorn.run(app, host=host, port=port, log_level="warning")
