"""
Authentication UI Module for GoalMate (Matching Mockup #2).
Split-banner authentication with mountain landscape on left and Sign In / Register / Forgot Password on right.
"""
import gradio as gr
from backend.database import SessionLocal
from backend.auth import authenticate_user, register_user, create_access_token
from ui.styles import get_asset_data_uri


def render_auth_banner_html() -> str:
    """Renders the left visual mountain landscape banner."""
    mountain_b64 = get_asset_data_uri("mountain_scene.png")
    bg_style = f"background-image: url('{mountain_b64}');" if mountain_b64 else "background: #2D6A4F;"
    
    return f"""
    <div class="auth-banner-left" style="{bg_style}">
        <div class="auth-banner-overlay"></div>
        <div class="auth-banner-content">
            <div class="auth-brand-logo">
                <span class="auth-brand-leaf">🌱</span>
                <span class="auth-brand-name">GoalMate</span>
            </div>
            
            <div style="margin: auto 0;">
                <h1 class="auth-headline-title">Start Your Journey Here</h1>
                <p class="auth-subheadline-desc">
                    Transform your ambitions into actionable, daily steps with GoalMate's AI-driven coaching and adaptive pacing.
                </p>
                <div class="auth-rating-badges">
                    <div class="auth-rating-pill">⭐ 4.9 Rating</div>
                    <div class="auth-rating-pill">📈 10k+ Goals Tracked</div>
                    <div class="auth-rating-pill">🤖 Autonomous AI</div>
                </div>
            </div>
            
            <div style="font-size: 12px; color: rgba(255,255,255,0.7); display: flex; justify-content: space-between;">
                <span>© 2026 GoalMate AI Inc.</span>
                <span>Privacy &amp; Terms</span>
            </div>
        </div>
    </div>
    """


def handle_login(email: str, password: str):
    """Authenticates user credentials and returns session update."""
    if not email or not password:
        return None, None, gr.update(value="⚠️ Please provide both email and password.", visible=True)
    
    db = SessionLocal()
    try:
        user = authenticate_user(db, email, password)
        if not user:
            return None, None, gr.update(value="❌ Invalid email or password. Please try again.", visible=True)
        
        token = create_access_token({"sub": str(user.id), "email": user.email, "name": user.name})
        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
        return token, user_dict, gr.update(value="✅ Login successful! Redirecting...", visible=True)
    finally:
        db.close()


def handle_register(name: str, email: str, password: str, confirm_pass: str, terms_accepted: bool):
    """Registers new user, seeds demo goal, and returns session token."""
    if not name or not email or not password:
        return None, None, gr.update(value="⚠️ Please fill in all required fields.", visible=True)
    if len(password) < 6:
        return None, None, gr.update(value="⚠️ Password must be at least 6 characters.", visible=True)
    if password != confirm_pass:
        return None, None, gr.update(value="⚠️ Passwords do not match.", visible=True)
    if not terms_accepted:
        return None, None, gr.update(value="⚠️ You must accept the Terms of Service to continue.", visible=True)
    
    db = SessionLocal()
    try:
        user, token = register_user(db, name, email, password)
        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
        return token, user_dict, gr.update(value=f"🎉 Welcome aboard, {user.name}! Redirecting...", visible=True)
    except ValueError as e:
        return None, None, gr.update(value=f"⚠️ {str(e)}", visible=True)
    except Exception as e:
        return None, None, gr.update(value=f"❌ Registration error: {str(e)}", visible=True)
    finally:
        db.close()


def handle_forgot_password(email: str):
    """Simulates password recovery dispatch."""
    if not email or "@" not in email:
        return gr.update(value="⚠️ Please enter a valid email address.", visible=True)
    return gr.update(
        value=f"📩 If an account exists for **{email}**, password reset instructions have been sent (expires in 1 hour).",
        visible=True
    )
