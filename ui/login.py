"""
GoalMate — Clean Haikyuu Anime Authentication View.
Clean background image without any text overlays.
Glassmorphic login & sign-up card with full auth functionality.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
ASSET_DIR = f"{BASE_DIR}/assets"
FRONTEND_ASSET_DIR = f"{BASE_DIR}/frontend/assets/images"


def render_login_page() -> str:
    """Renders the clean anime background with glassmorphic auth card."""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GoalMate — Log In</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }}
        *::-webkit-scrollbar {{
            display: none !important;
            width: 0 !important;
            height: 0 !important;
        }}
        html, body {{
            width: 100%;
            height: 100vh;
            overflow: hidden;
            background: #0B132B;
        }}
        .login-viewport {{
            position: relative;
            width: 100vw;
            height: 100vh;
            background-image: url('/gm-assets/login_bg_clean.jpg'), url('/frontend/assets/images/login_bg_clean.jpg'), url('/gradio_api/file={ASSET_DIR}/login_bg_clean.jpg');
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 8vw;
        }}

        /* Floating Glass Card */
        .login-card-floating {{
            width: 390px;
            max-width: 90vw;
            background: rgba(255, 255, 255, 0.94);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border-radius: 28px;
            padding: 36px 32px 32px 32px;
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.28), 0 4px 16px rgba(0, 0, 0, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.85);
            transition: all 0.3s ease;
        }}
        .card-crest {{
            text-align: center;
            margin-bottom: 10px;
        }}
        .card-crest-icon {{
            width: 44px;
            height: 44px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background: #FFF0E6;
            box-shadow: 0 4px 12px rgba(242, 123, 53, 0.15);
            font-size: 1.35rem;
        }}
        .card-title {{
            font-size: 1.45rem;
            font-weight: 800;
            color: #1A202C;
            text-align: center;
            letter-spacing: -0.01em;
        }}
        .card-subtitle {{
            font-size: 0.82rem;
            color: #718096;
            text-align: center;
            margin-top: 4px;
            margin-bottom: 22px;
        }}

        /* Form Inputs */
        .form-group {{
            margin-bottom: 14px;
        }}
        .form-label {{
            display: block;
            font-size: 0.78rem;
            font-weight: 700;
            color: #4A5568;
            margin-bottom: 6px;
        }}
        .input-wrap {{
            position: relative;
            display: flex;
            align-items: center;
        }}
        .input-icon {{
            position: absolute;
            left: 14px;
            font-size: 0.95rem;
            color: #A0AEC0;
            pointer-events: none;
        }}
        .input-field {{
            width: 100%;
            padding: 11px 14px 11px 40px;
            background: #F8F9FA;
            border: 1.5px solid #E2E8F0;
            border-radius: 12px;
            font-size: 0.86rem;
            color: #1A202C;
            outline: none;
            transition: all 0.15s ease;
        }}
        .input-field:focus {{
            border-color: #F27B35;
            background: #FFFFFF;
            box-shadow: 0 0 0 3px rgba(242, 123, 53, 0.15);
        }}
        .eye-toggle-btn {{
            position: absolute;
            right: 12px;
            background: none;
            border: none;
            cursor: pointer;
            color: #A0AEC0;
            font-size: 0.95rem;
            padding: 4px;
        }}
        .eye-toggle-btn:hover {{
            color: #4A5568;
        }}

        /* Aux Row */
        .form-aux-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 12px 0 18px 0;
            font-size: 0.76rem;
        }}
        .remember-label {{
            display: flex;
            align-items: center;
            gap: 6px;
            color: #4A5568;
            cursor: pointer;
            user-select: none;
        }}
        .remember-label input {{
            accent-color: #F27B35;
            cursor: pointer;
        }}
        .forgot-link {{
            color: #DD6B20;
            text-decoration: none;
            font-weight: 600;
            cursor: pointer;
        }}
        .forgot-link:hover {{
            text-decoration: underline;
        }}

        /* Submit Button */
        .btn-primary-orange {{
            width: 100%;
            padding: 12px;
            background: linear-gradient(90deg, #F27B35 0%, #FF8A3D 100%);
            border: none;
            border-radius: 12px;
            color: #FFFFFF;
            font-size: 0.92rem;
            font-weight: 800;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(242, 123, 53, 0.35);
            transition: all 0.15s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        .btn-primary-orange:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(242, 123, 53, 0.45);
        }}
        .btn-primary-orange:active {{
            transform: translateY(0);
        }}

        .card-footer-switch {{
            margin-top: 18px;
            text-align: center;
            font-size: 0.8rem;
            color: #718096;
        }}
        .card-footer-switch a {{
            color: #F27B35;
            font-weight: 700;
            text-decoration: none;
            cursor: pointer;
            margin-left: 4px;
        }}
        .card-footer-switch a:hover {{
            text-decoration: underline;
        }}

        .auth-error-msg {{
            display: none;
            padding: 9px 12px;
            background: #FFF5F5;
            border: 1px solid #FEB2B2;
            border-radius: 10px;
            color: #C53030;
            font-size: 0.78rem;
            font-weight: 600;
            margin-bottom: 14px;
            text-align: center;
        }}

        .login-topbar {{
            position: absolute;
            top: 0;
            left: 0;
            z-index: 10;
            padding: 24px 36px;
        }}
        .brand-logo-group {{
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            cursor: pointer;
        }}
        .brand-logo-img {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            object-fit: cover;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            background: #FFFFFF;
        }}
        .brand-title-wrap h1 {{
            font-size: 1.65rem;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.02em;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.45);
            font-style: italic;
            line-height: 1.1;
        }}
        .brand-title-wrap p {{
            font-size: 0.78rem;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.95);
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.45);
            margin-top: 1px;
        }}

        @media (max-width: 900px) {{
            .login-viewport {{
                justify-content: center;
                padding-right: 0;
            }}
            .login-card-floating {{
                width: 92%;
                margin: 0 auto;
            }}
            .login-topbar {{
                padding: 16px 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="login-viewport">
        <!-- TOP-LEFT BRAND LOGO & TITLE -->
        <div class="login-topbar">
            <div class="brand-logo-group" onclick="window.location.href='/'" title="Go to GoalMate Dashboard">
                <img src="/gm-assets/volleyball_logo.jpg" class="brand-logo-img" alt="GoalMate Logo" onerror="this.src='/frontend/assets/images/volleyball_logo.jpg'">
                <div class="brand-title-wrap">
                    <h1>GoalMate</h1>
                    <p>Small steps. Big dreams.</p>
                </div>
            </div>
        </div>

        <!-- FLOATING AUTH CARD -->
        <div class="login-card-floating">
            <div class="card-crest">
                <span class="card-crest-icon">🏐</span>
            </div>
            <h2 class="card-title" id="auth-heading">Welcome back!</h2>
            <p class="card-subtitle" id="auth-subheading">Log in to continue your journey with GoalMate.</p>

            <div class="auth-error-msg" id="auth-error-box"></div>

            <form id="auth-form" onsubmit="event.preventDefault(); window.handleAuthSubmit();">
                <div class="form-group" id="name-group" style="display: none;">
                    <label class="form-label">Full Name</label>
                    <div class="input-wrap">
                        <span class="input-icon">👤</span>
                        <input type="text" id="auth-name" class="input-field" placeholder="Enter your full name">
                    </div>
                </div>

                <div class="form-group">
                    <label class="form-label" id="email-label">Email or Username</label>
                    <div class="input-wrap">
                        <span class="input-icon">✉️</span>
                        <input type="text" id="auth-email" class="input-field" placeholder="Enter your email or username" required value="sanskriti@example.com">
                    </div>
                </div>

                <div class="form-group">
                    <label class="form-label">Password</label>
                    <div class="input-wrap">
                        <span class="input-icon">🔒</span>
                        <input type="password" id="auth-password" class="input-field" placeholder="Enter your password" required value="password123">
                        <button type="button" class="eye-toggle-btn" onclick="window.togglePasswordVisibility()">👁️</button>
                    </div>
                </div>

                <div class="form-aux-row" id="aux-row">
                    <label class="remember-label">
                        <input type="checkbox" id="remember-me" checked>
                        <span>Remember me</span>
                    </label>
                    <a class="forgot-link" onclick="alert('Password reset link has been dispatched to your email.')">Forgot password?</a>
                </div>

                <button type="submit" class="btn-primary-orange" id="auth-submit-btn">
                    <span>Log In</span>
                    <span>&rarr;</span>
                </button>
            </form>

            <div class="card-footer-switch">
                <span id="switch-prompt">Don't have an account?</span>
                <a id="switch-btn" onclick="window.toggleAuthMode()">Sign Up</a>
            </div>
        </div>
    </div>

    <script>
        let isSignUpMode = false;

        window.togglePasswordVisibility = function() {{
            const pwd = document.getElementById('auth-password');
            if (pwd.type === 'password') {{
                pwd.type = 'text';
            }} else {{
                pwd.type = 'password';
            }}
        }};

        window.toggleAuthMode = function() {{
            isSignUpMode = !isSignUpMode;
            const heading = document.getElementById('auth-heading');
            const subheading = document.getElementById('auth-subheading');
            const nameGroup = document.getElementById('name-group');
            const submitBtn = document.getElementById('auth-submit-btn');
            const switchPrompt = document.getElementById('switch-prompt');
            const switchBtn = document.getElementById('switch-btn');
            const auxRow = document.getElementById('aux-row');
            const errBox = document.getElementById('auth-error-box');
            errBox.style.display = 'none';

            if (isSignUpMode) {{
                heading.innerText = 'Create your account';
                subheading.innerText = 'Start your journey to bigger dreams today.';
                nameGroup.style.display = 'block';
                if (auxRow) auxRow.style.display = 'none';
                submitBtn.innerHTML = '<span>Sign Up</span> <span>&rarr;</span>';
                switchPrompt.innerText = 'Already have an account?';
                switchBtn.innerText = 'Log In';
            }} else {{
                heading.innerText = 'Welcome back!';
                subheading.innerText = 'Log in to continue your journey with GoalMate.';
                nameGroup.style.display = 'none';
                if (auxRow) auxRow.style.display = 'flex';
                submitBtn.innerHTML = '<span>Log In</span> <span>&rarr;</span>';
                switchPrompt.innerText = "Don't have an account?";
                switchBtn.innerText = 'Sign Up';
            }}
        }};

        window.handleAuthSubmit = async function() {{
            const email = document.getElementById('auth-email').value.trim();
            const password = document.getElementById('auth-password').value;
            const name = document.getElementById('auth-name').value.trim();
            const errBox = document.getElementById('auth-error-box');
            errBox.style.display = 'none';

            if (!email || !password) {{
                errBox.innerText = 'Please enter both email and password.';
                errBox.style.display = 'block';
                return;
            }}

            const endpoint = isSignUpMode ? '/api/auth/register' : '/api/auth/login';
            const payload = isSignUpMode 
                ? {{ name: name || 'Sanskriti', email: email, password: password }}
                : {{ email: email, password: password }};

            try {{
                const res = await fetch(endpoint, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }});
                const data = await res.json();
                if (data.success) {{
                    localStorage.setItem('gm_token', data.token || 'auth_token');
                    localStorage.setItem('gm_user', JSON.stringify(data.user || {{ name: 'Sanskriti' }}));
                    window.location.href = '/';
                }} else {{
                    errBox.innerText = data.error || 'Authentication failed. Please check credentials.';
                    errBox.style.display = 'block';
                }}
            }} catch (err) {{
                errBox.innerText = 'Network error. Please try again.';
                errBox.style.display = 'block';
            }}
        }};
    </script>
</body>
</html>
"""
