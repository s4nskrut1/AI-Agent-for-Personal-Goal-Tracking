import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional

from ai_coach import generate_coach_response, load_env_file
from gradio_interface import create_gradio_coach_app
import gradio as gr

load_env_file()

app = FastAPI(title="GoalMate API Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    userName: Optional[str] = "there"
    context: Optional[Dict[str, Any]] = None

@app.post("/api/coach/chat")
async def coach_chat(req: ChatRequest):
    try:
        response_data = generate_coach_response(
            message=req.message,
            user_name=req.userName or "there",
            context=req.context or {}
        )
        return JSONResponse(content=response_data)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "reply": "I ran into an issue, but let's keep going!"}
        )

@app.get("/api/coach/status")
async def coach_status():
    api_key_configured = bool(os.environ.get("GEMINI_API_KEY", "").strip())
    return {
        "gemini_configured": api_key_configured,
        "model": "gemini-2.5-flash" if api_key_configured else "goalmate-coach-v1",
        "gradio_path": "/gradio"
    }

# Mount Gradio Coach Interface directly at /gradio
demo = create_gradio_coach_app()
app = gr.mount_gradio_app(app, demo, path="/gradio")

# Mount frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")

    @app.get("/")
    async def serve_index():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="http://127.0.0.1:7860/", status_code=307)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000)
