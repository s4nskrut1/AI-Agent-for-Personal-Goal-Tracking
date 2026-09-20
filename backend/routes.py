"""
FastAPI REST API Routes for GoalMate.
Exposes protected endpoints with JWT Bearer authentication and multi-user data isolation.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.schemas import (
    UserRegister, UserLogin, UserOut, TokenResponse, ForgotPasswordRequest,
    GoalCreate, GoalOut, TaskCreate, TaskOut, ProgressStats
)
from backend.auth import hash_password, verify_password, create_access_token, get_current_user
from services import goal_service, task_service, progress_service

api_router = APIRouter(prefix="/api")


# --- Authentication Endpoints ---
@api_router.post("/auth/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Registers a new user account with hashed password and generates a JWT."""
    existing = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    new_user = User(
        name=data.name.strip(),
        email=data.email.lower().strip(),
        password_hash=hash_password(data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id), "email": new_user.email, "name": new_user.name})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut(id=new_user.id, name=new_user.name, email=new_user.email, created_at=new_user.created_at.isoformat() if new_user.created_at else None)
    )


@api_router.post("/auth/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user via email and password, issuing a signed JWT."""
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    token = create_access_token({"sub": str(user.id), "email": user.email, "name": user.name})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut(id=user.id, name=user.name, email=user.email, created_at=user.created_at.isoformat() if user.created_at else None)
    )


@api_router.get("/auth/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns currently authenticated user profile."""
    return UserOut(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None
    )


@api_router.post("/auth/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Simulates secure password recovery dispatch without exposing tokens."""
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    return {
        "success": True,
        "message": f"If an account exists for {data.email}, a secure password reset link has been dispatched. (Expires in 1 hour)."
    }


# --- Goal Endpoints ---
@api_router.get("/goals", response_model=List[GoalOut])
def list_goals(status: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieves all goals owned by the authenticated user."""
    goals = goal_service.get_goals(current_user.id, status=status, db=db)
    return [GoalOut(
        id=g.id,
        user_id=g.user_id,
        title=g.title,
        description=g.description,
        category=g.category,
        target_date=g.target_date,
        priority=g.priority,
        daily_time_minutes=g.daily_time_minutes,
        preferred_schedule=g.preferred_schedule,
        status=g.status,
        created_at=g.created_at.isoformat() if g.created_at else None,
        updated_at=g.updated_at.isoformat() if g.updated_at else None
    ) for g in goals]


@api_router.post("/goals", response_model=GoalOut)
def create_goal(data: GoalCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Creates a new goal isolated to the current user."""
    g = goal_service.create_goal(current_user.id, data, db)
    return GoalOut(
        id=g.id,
        user_id=g.user_id,
        title=g.title,
        description=g.description,
        category=g.category,
        target_date=g.target_date,
        priority=g.priority,
        daily_time_minutes=g.daily_time_minutes,
        preferred_schedule=g.preferred_schedule,
        status=g.status,
        created_at=g.created_at.isoformat() if g.created_at else None,
        updated_at=g.updated_at.isoformat() if g.updated_at else None
    )


# --- Task Endpoints ---
@api_router.get("/tasks/today")
def get_today_tasks_api(goal_id: Optional[int] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieves today's tasks for current user."""
    tasks = task_service.get_today_tasks(current_user.id, goal_id=goal_id, db=db)
    return [t.to_dict() for t in tasks]


@api_router.post("/tasks/{task_id}/complete")
def complete_task_api(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Marks task completed for current user and updates progress telemetry."""
    task = task_service.complete_task(task_id, current_user.id, db)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or access denied.")
    stats = progress_service.calculate_progress(current_user.id, task.goal_id, db)
    return {"success": True, "task": task.to_dict(), "stats": stats}


# --- Progress & Telemetry Endpoints ---
@api_router.get("/progress")
def get_progress_api(goal_id: Optional[int] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Calculates completion rate, active streak, and weekly consistency."""
    return progress_service.calculate_progress(current_user.id, goal_id=goal_id, db=db)
