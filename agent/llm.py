"""
GoalMate — Gemini Agentic LLM Layer.
Handles function calling loop with proper Gemini API calls using direct REST.
"""
import os
import json
import logging
import requests
from typing import List, Dict, Any, Tuple

from agent.tools import TOOL_DECLARATIONS, execute_tool

logger = logging.getLogger("goalmate-llm")

GEMINI_MODELS = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-latest"]

SYSTEM_PROMPT = """You are the GoalMate AI Coach — a professional, concise, and genuinely helpful productivity assistant.

Your persona: Calm, direct, slightly warm. Inspired by the disciplined dedication of Shoyo Hinata — not the anime hype, but the quiet consistency of someone who shows up every day.

You have access to real tools that read from and write to the user's actual database. When a user asks you to create a goal, analyze progress, or change plans — you MUST use the appropriate tool and actually do it.

Rules:
- Never claim to do something you didn't actually do with a tool.
- Never invent progress data. Always read from tools.
- When user says "I want to learn X in Y days" → call create_goal_with_plan immediately. Don't ask unnecessary questions unless genuinely needed.
- For create_goal_with_plan: generate realistic milestones (5-7) and tasks (1-2 per day). Tasks should be concrete and actionable.
- Keep responses concise. 2-4 sentences after an action. Don't write essays.
- Don't use excessive emojis or hype language like "AMAZING!!!" or "You've got this!!! 🔥🔥🔥".
- After completing a tool action, briefly confirm what changed and what the user should do next.
- For destructive operations (delete goal), confirm intent before executing.
"""


def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip("'\"")
                        os.environ["GEMINI_API_KEY"] = key
                        break
    return key


def call_gemini(messages: List[Dict], tools: List[Dict] = None, model: str = None) -> Dict:
    """Make a single Gemini API call. Returns full response dict."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError("No GEMINI_API_KEY configured")
    
    for m in (GEMINI_MODELS if model is None else [model]):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
            payload = {"contents": messages}
            if tools:
                payload["tools"] = [{"function_declarations": tools}]
            payload["system_instruction"] = {"parts": [{"text": SYSTEM_PROMPT}]}
            
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code in (503, 429):
                logger.warning(f"Model {m} unavailable ({resp.status_code}), trying next...")
                continue
            else:
                logger.error(f"Gemini error {resp.status_code}: {resp.text[:200]}")
                continue
        except requests.Timeout:
            logger.warning(f"Model {m} timed out, trying next...")
            continue
        except Exception as e:
            logger.error(f"Request error with {m}: {e}")
            continue
    
    raise RuntimeError("All Gemini models unavailable")


def agent_chat(user_message: str, history: List[Dict]) -> Tuple[str, List[Dict], List[str]]:
    """
    Main agentic chat function.
    Returns: (reply_text, updated_history, list_of_actions_taken)
    """
    api_key = get_api_key()
    if not api_key:
        return "No Gemini API key configured. Please add GEMINI_API_KEY to your .env file.", history, []
    
    # Build Gemini message history format
    gemini_messages = []
    for msg in history[-12:]:  # Keep last 12 messages for context
        role = "user" if msg["role"] == "user" else "model"
        gemini_messages.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })
    
    # Add current user message
    gemini_messages.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })
    
    actions_taken = []
    max_tool_loops = 4  # prevent infinite tool loops
    
    for loop_i in range(max_tool_loops):
        try:
            response = call_gemini(gemini_messages, TOOL_DECLARATIONS)
        except Exception as e:
            logger.error(f"Gemini call failed: {e}")
            return f"I'm having trouble connecting to Gemini right now. Error: {str(e)[:100]}", history, []
        
        candidates = response.get("candidates", [])
        if not candidates:
            break
        
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        
        # Check if there are function calls in the response
        function_calls = [p for p in parts if "functionCall" in p]
        text_parts = [p.get("text", "") for p in parts if "text" in p]
        
        if not function_calls:
            # No more function calls — this is the final text response
            final_text = "\n".join(text_parts).strip()
            if not final_text:
                final_text = "Done."
            
            # Update history
            new_history = history + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": final_text}
            ]
            return final_text, new_history, actions_taken
        
        # Add assistant's response (with function calls) to the conversation
        gemini_messages.append({"role": "model", "parts": parts})
        
        # Execute all function calls
        function_results = []
        for fc_part in function_calls:
            fc = fc_part["functionCall"]
            tool_name = fc["name"]
            tool_args = fc.get("args", {})
            
            logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
            result = execute_tool(tool_name, tool_args)
            actions_taken.append(tool_name)
            
            function_results.append({
                "functionResponse": {
                    "name": tool_name,
                    "response": {"result": result}
                }
            })
        
        # Add tool results back to conversation
        gemini_messages.append({
            "role": "user",
            "parts": function_results
        })
    
    # Fallback if loop exceeded
    return "I processed your request but couldn't generate a final response. Please try again.", history, actions_taken
