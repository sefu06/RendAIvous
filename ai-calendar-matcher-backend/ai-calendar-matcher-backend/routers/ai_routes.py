# routers/ai_routes.py
from typing import List, Literal
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.gemini_service import (
    generate_suggestions,
    # keep these imports only if you added chat earlier
    # generate_chat_reply,
    # stream_chat_reply,
)

router = APIRouter(prefix="/ai", tags=["ai"])

# ---- Suggest endpoint models (no groupSize/budget) ----
class FreeWindow(BaseModel):
    start: str
    end: str

class SuggestionIn(BaseModel):
    location: str
    preferences: List[str] = []
    freeWindows: List[FreeWindow] = []

class SuggestionOut(BaseModel):
    windowStart: str
    windowEnd: str
    place: str
    activity: str

@router.post("/suggest", response_model=List[SuggestionOut])
def suggest(body: SuggestionIn):
    try:
        return generate_suggestions(
            location=body.location,
            preferences=body.preferences,
            free_windows=[w.model_dump() for w in body.freeWindows],
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Suggestions failed: {e}")

# ---- If you added chat endpoints earlier, keep them below unchanged ----
# class ChatMessage(BaseModel):
#     role: Literal["user", "assistant"]
#     content: str
# class ChatIn(BaseModel):
#     message: str
#     history: List[ChatMessage] = []
# class ChatOut(BaseModel):
#     reply: str
# @router.post("/chat", response_model=ChatOut)
# def chat(body: ChatIn):
#     try:
#         reply = generate_chat_reply(body.message, [m.model_dump() for m in body.history])
#         if not reply: raise RuntimeError("Empty reply")
#         return {"reply": reply}
#     except Exception as e:
#         raise HTTPException(status_code=502, detail=f"Chat failed: {e}")
# @router.post("/chat/stream")
# def chat_stream(body: ChatIn):
#     try:
#         def event_gen():
#             for token in stream_chat_reply(body.message, [m.model_dump() for m in body.history]):
#                 yield f"data: {token}\n\n"
#             yield "event: done\ndata: end\n\n"
#         return StreamingResponse(event_gen(), media_type="text/event-stream")
#     except Exception as e:
#         raise HTTPException(status_code=502, detail=f"Chat stream failed: {e}")

# --- Chat endpoints (add below your /ai/suggest route) ---

from typing import Literal
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.gemini_service import generate_chat_reply, stream_chat_reply

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatIn(BaseModel):
    message: str
    history: list[ChatMessage] = []

class ChatOut(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatOut)
def chat(body: ChatIn):
    try:
        reply = generate_chat_reply(body.message, [m.model_dump() for m in body.history])
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Chat failed: {e}")

@router.post("/chat/stream")
def chat_stream(body: ChatIn):
    try:
        def event_gen():
            for token in stream_chat_reply(body.message, [m.model_dump() for m in body.history]):
                yield f"data: {token}\n\n"
            yield "event: done\ndata: end\n\n"

        return StreamingResponse(event_gen(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Chat stream failed: {e}")

