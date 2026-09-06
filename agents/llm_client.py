"""
Unified LLM Client for GoalMate.
Supports Google Gemini (via google-genai), Groq, and OpenAI with automated
failover and offline heuristic resilience.
"""
import os
import json
import logging
from typing import Optional, Dict, Any

from config import (
    GEMINI_API_KEY,
    GROQ_API_KEY,
    OPENAI_API_KEY,
    GEMINI_MODEL,
    GROQ_MODEL,
    OPENAI_MODEL
)

logger = logging.getLogger("GoalMate.LLM")


class LLMClient:
    """Manages multi-provider LLM inference with graceful error handling and fallbacks."""

    def __init__(self):
        self.gemini_client = None
        self.groq_client = None
        
        # Initialize Gemini if key provided
        if GEMINI_API_KEY:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                logger.info("Google GenAI client initialized.")
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI client: {e}")

        # Initialize Groq if key provided
        if GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=GROQ_API_KEY)
                logger.info("Groq client initialized.")
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}")

    def generate_response(
        self,
        prompt: str,
        system_instruction: str = "You are GoalMate, an expert autonomous AI personal goal coach.",
        json_mode: bool = False
    ) -> str:
        """
        Attempts to generate response from available LLMs in order of priority:
        1. Google Gemini
        2. Groq
        3. OpenAI (if key provided)
        Returns text or JSON string. Raises or falls back if none available.
        """
        # 1. Try Gemini
        if self.gemini_client:
            try:
                full_prompt = f"System: {system_instruction}\n\nUser: {prompt}"
                if json_mode:
                    full_prompt += "\n\nCRITICAL: Respond ONLY with a valid JSON object. Do not wrap in markdown quotes if possible or use ```json blocks."
                
                response = self.gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=full_prompt
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini generation error: {e}. Trying secondary provider...")

        # 2. Try Groq
        if self.groq_client:
            try:
                messages = [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ]
                kwargs: Dict[str, Any] = {
                    "model": GROQ_MODEL,
                    "messages": messages,
                    "temperature": 0.4
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                    
                completion = self.groq_client.chat.completions.create(**kwargs)
                return completion.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"Groq generation error: {e}.")

        # 3. If no LLM available or both failed, raise RuntimeError so calling agent uses heuristic fallback
        raise RuntimeError("No external LLM provider available or request quota exceeded.")


# Global singleton instance
llm_client = LLMClient()
