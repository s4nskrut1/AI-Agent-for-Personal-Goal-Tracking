import os
import gradio as gr
from ai_coach import generate_coach_response, load_env_file

load_env_file()

def create_gradio_coach_app():
    with gr.Blocks() as demo:
        gr.HTML("""
        <div style="display:flex; align-items:center; justify-content:space-between; padding: 12px 16px 8px 16px; border-bottom:1px solid #F1F5F9;">
            <div style="display:flex; align-items:center; gap:10px;">
                <img src="/assets/images/hinata_avatar.jpg" style="width:38px; height:38px; border-radius:50%; object-fit:cover; border:2px solid #FF6B35;" onerror="this.style.display='none'" />
                <div>
                    <h3 style="margin:0; font-size:1rem; font-weight:800; color:#1E2538;">AI Coach</h3>
                    <span style="font-size:0.73rem; color:#10B981; font-weight:700;">● Online (Gemini Powered)</span>
                </div>
            </div>
        </div>
        """)

        chatbot = gr.Chatbot(
            value=[
                {"role": "assistant", "content": "Hey! 👋 I'm your GoalMate AI Coach.\n\nTell me what you want to work on, how you're feeling, or ask me to break down something big into daily steps. Let's go! 🏐✨"}
            ],
            height=400,
            show_label=False,
            avatar_images=(None, "/assets/images/hinata_avatar.jpg"),
        )

        with gr.Row():
            chip1 = gr.Button("⚡ Plan my day", size="sm")
            chip2 = gr.Button("🎯 Break down a goal", size="sm")
            chip3 = gr.Button("💡 Tips & motivation", size="sm")

        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="Type your message...",
                show_label=False,
                scale=5,
                container=False
            )
            send_btn = gr.Button("Send →", scale=1, min_width=70, variant="primary")

        persona_radio = gr.Radio(
            choices=["High Energy (Hinata)", "Disciplined Strategist (Kageyama)", "Calm & Grounded (Daichi)"],
            value="High Energy (Hinata)",
            label="Coaching Style",
            visible=False
        )

        def respond(user_message, history, persona):
            if not user_message or not user_message.strip():
                return history, ""
            if history is None:
                history = []
            context = {"goals": [], "tasks": [], "streaks": {"currentStreak": 0, "weeklyProgress": 0}}
            res = generate_coach_response(f"[{persona}] {user_message}", "there", context)
            history = history + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": res["reply"]}
            ]
            return history, ""

        send_btn.click(respond, [msg_input, chatbot, persona_radio], [chatbot, msg_input])
        msg_input.submit(respond, [msg_input, chatbot, persona_radio], [chatbot, msg_input])

        chip1.click(lambda h, p: respond("Can you help me plan my productive day?", h, p), [chatbot, persona_radio], [chatbot, msg_input])
        chip2.click(lambda h, p: respond("I have a big goal — help me break it down into milestones.", h, p), [chatbot, persona_radio], [chatbot, msg_input])
        chip3.click(lambda h, p: respond("Give me tips and a quick motivational boost!", h, p), [chatbot, persona_radio], [chatbot, msg_input])

    return demo
