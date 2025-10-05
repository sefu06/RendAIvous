# services/gemini_service.py
import os, json
from typing import List, Dict
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.0-flash" 

# Output = one object per free window
SCHEMA = {
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "windowStart": { "type": "string" },
      "windowEnd":   { "type": "string" },
      "place":       { "type": "string" },
      "activity":    { "type": "string" }
    },
    "required": ["windowStart", "windowEnd", "place", "activity"]
  }
}

def _prompt(location: str, preferences: List[str], free_windows: List[Dict]):
    return (
        "You are a group activity planner.\n"
        "For each free time window below, propose a specific PLACE (name) in the given location, and a concise ACTIVITY to do there.\n"
        "Output strictly JSON that matches the given schema (no extra keys, no prose).\n"
        f"- Location/area: {location}\n"
        f"- Preferences (optional): {preferences}\n"
        "- Keep activities realistic for the time window; avoid duplicates.\n"
        f"- Free windows (use these as windowStart/windowEnd in output): {free_windows}\n"
        "Return ONLY the JSON.\n"
    )

def generate_suggestions(
    *, location: str, preferences: List[str], free_windows: List[Dict]
) -> List[Dict]:
    model = genai.GenerativeModel(
        MODEL,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": SCHEMA,
        },
    )
    resp = model.generate_content(_prompt(location, preferences, free_windows))
    try:
        return json.loads(resp.text)
    except Exception as e:
        raise RuntimeError(f"Model returned invalid JSON: {e}")
    

    # --- Chatbot features (non-streaming + streaming) ---

from typing import Dict  # if not already imported

def generate_chat_reply(message: str, history: List[Dict[str, str]]) -> str:
    """
    history items look like: {"role": "user" | "assistant", "content": "..."}
    We'll map 'assistant' -> Gemini 'model' role.
    """
    conv = []
    for m in history:
        role = "user" if m.get("role") == "user" else "model"
        conv.append({"role": role, "parts": [m.get("content", "")]})

    model = genai.GenerativeModel(MODEL)
    chat = model.start_chat(history=conv)
    resp = chat.send_message(message)
    text = getattr(resp, "text", None)
    if not text:
        raise RuntimeError("Empty reply from model")
    return text

def stream_chat_reply(message: str, history: List[Dict[str, str]]):
    """
    Generator that yields text chunks (use with FastAPI StreamingResponse + SSE).
    """
    conv = []
    for m in history:
        role = "user" if m.get("role") == "user" else "model"
        conv.append({"role": role, "parts": [m.get("content", "")]})

    model = genai.GenerativeModel(MODEL)
    chat = model.start_chat(history=conv)
    resp = chat.send_message(message, stream=True)
    for chunk in resp:
        if getattr(chunk, "text", None):
            yield chunk.text
    try:
        resp.resolve()
    except Exception:
        pass

