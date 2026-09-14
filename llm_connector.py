"""
llm_connector.py - Multi-backend LLM Connector for EcoAgent.
Supports:
1. Ollama (local LLaMA 3, Mistral, Gemma 2) - 100% offline, free & open-source
2. Google Gemini API (Free tier fallback)
3. Deterministic RAG Citation Fallback - ensures zero failure during live demos
   even if Ollama is not started or no API key is provided.
"""

import os
import json
import requests
import socket

# Default configurations
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
DEFAULT_GEMINI_KEY = "AIzaSyC1lpl4L8-OFDfo1le7lEqFXRL5yhsfu_o"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", DEFAULT_GEMINI_KEY)

_OLLAMA_AVAILABLE = None  # Cache status to avoid repetitive connection timeouts


def is_ollama_available() -> bool:
    """Checks if local Ollama daemon is reachable (cached)."""
    global _OLLAMA_AVAILABLE
    if _OLLAMA_AVAILABLE is not None:
        return _OLLAMA_AVAILABLE

    # Ultra-fast TCP socket probe first (20ms timeout)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.02)
        result = sock.connect_ex(('127.0.0.1', 11434))
        sock.close()
        if result != 0:
            _OLLAMA_AVAILABLE = False
            return False
            
        r = requests.get("http://127.0.0.1:11434/api/tags", timeout=0.1)
        _OLLAMA_AVAILABLE = (r.status_code == 200)
    except Exception:
        _OLLAMA_AVAILABLE = False
        
    return _OLLAMA_AVAILABLE


def call_ollama(prompt: str, system_prompt: str = "", model: str = OLLAMA_MODEL) -> str:
    """Invokes local Ollama LLM with fast timeout."""
    global _OLLAMA_AVAILABLE
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {"temperature": 0.2}
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=0.8)
        r.raise_for_status()
        data = r.json()
        return data.get("response", "").strip()
    except Exception:
        _OLLAMA_AVAILABLE = False
        return ""


def call_gemini(prompt: str, system_prompt: str = "", api_key: str = "") -> str:
    """Invokes Google Gemini Free Tier API via REST."""
    key = api_key or os.environ.get("GEMINI_API_KEY", DEFAULT_GEMINI_KEY)
    if not key:
        raise ValueError("No Gemini API key provided.")
    
    models_to_try = ["gemini-3.6-flash", "gemini-3.5-flash"]

    for model_name in models_to_try:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"System Instructions: {system_prompt}\n\nTask: {prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024
            }
        }
        try:
            r = requests.post(endpoint, json=payload, timeout=3.0)
            if r.status_code == 200:
                data = r.json()
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
            elif r.status_code in (429, 403):
                # Quota exceeded or key blocked - do not retry other models to save latency
                break
        except Exception:
            continue
            
    return ""


def generate_llm_response(prompt: str, system_prompt: str = "", custom_gemini_key: str = "") -> dict:
    """
    Executes prompt using the best available free LLM backend:
    Gemini Cloud (if key provided & under quota) -> Ollama (Local) -> Grounded RAG Fallback.
    """
    active_key = custom_gemini_key or GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
    
    # 1. Try Gemini Free Tier Cloud API first if key is present
    if active_key:
        try:
            res = call_gemini(prompt, system_prompt, active_key)
            if res:
                return {"backend": "Google Gemini (Free Tier)", "text": res, "status": "success"}
        except Exception as e:
            pass

    # 2. Try local Ollama if active
    if is_ollama_available():
        try:
            res = call_ollama(prompt, system_prompt)
            if res:
                return {"backend": "Ollama (Local LLaMA-3)", "text": res, "status": "success"}
        except Exception as e:
            pass

    # 3. Fast deterministic grounded fallback (0.001s response time)
    return {
        "backend": "Grounded Citation Engine (Deterministic Fallback)",
        "text": "",
        "status": "offline_fallback"
    }
