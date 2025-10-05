# main.py
import os
import json
from datetime import datetime
from typing import List, Tuple

import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# AI endpoints (make sure routers/ai_routes.py exists)
from routers.ai_routes import router as ai_router

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

app = FastAPI(title="RendAIvous API", version="1.0.0")

# --- CORS (Vite defaults) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Healthcheck ---
@app.get("/healthz")
def healthz():
    return {"ok": True}

# --- Google OAuth (inline) ---
@app.get("/login")
def login():
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=https://www.googleapis.com/auth/calendar.readonly"
        "&access_type=offline"
        "&prompt=consent"
    )
    return RedirectResponse(auth_url)

@app.get("/auth/callback")
def auth_callback(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    return requests.post(token_url, data=data).json()

# --- Include AI router under /v1 ---
app.include_router(ai_router, prefix="/v1")

# ------------------------
# Calendar helpers
# ------------------------

def _parse_iso(dt: str) -> datetime:
    """Accept '...Z' or timezone offsets for fromisoformat."""
    return datetime.fromisoformat(dt.replace("Z", "+00:00"))

def get_user_events(access_token: str, refresh_token: str, start_iso: str, end_iso: str) -> List[dict]:
    """Fetch all events for a user across all calendars; auto-refresh token if needed."""
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    if not creds.valid:
        creds.refresh(Request())

    service = build("calendar", "v3", credentials=creds)

    calendar_list = service.calendarList().list().execute()
    calendar_ids = [cal["id"] for cal in calendar_list.get("items", [])]

    all_events: List[dict] = []
    for cal_id in calendar_ids:
        events = service.events().list(
            calendarId=cal_id,
            timeMin=start_iso,
            timeMax=end_iso,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        all_events.extend(events.get("items", []))
    return all_events

def convert_to_busy_intervals(events: List[dict]) -> List[Tuple[datetime, datetime]]:
    busy: List[Tuple[datetime, datetime]] = []
    for event in events:
        start = event["start"].get("dateTime") or event["start"].get("date")
        end = event["end"].get("dateTime") or event["end"].get("date")
        busy.append((_parse_iso(start), _parse_iso(end)))
    return sorted(busy)

def merge_busy_intervals(list_of_busy_intervals: List[List[Tuple[datetime, datetime]]]) -> List[List[datetime]]:
    """Combine busy intervals across all users."""
    all_busy = sorted([interval for user in list_of_busy_intervals for interval in user])
    merged: List[List[datetime]] = []
    for start, end in all_busy:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return merged

def get_free_intervals(merged_busy: List[List[datetime]], start_day: datetime, end_day: datetime) -> List[Tuple[datetime, datetime]]:
    """Return time windows where everyone is free within [start_day, end_day]."""
    free: List[Tuple[datetime, datetime]] = []
    current = start_day
    for busy_start, busy_end in merged_busy:
        if current < busy_start:
            free.append((current, busy_start))
        current = max(current, busy_end)
    if current < end_day:
        free.append((current, end_day))
    return free

# ------------------------
# Calendar endpoints
# ------------------------

@app.get("/shared_free_time")
def shared_free_time(
    start: str = Query(..., description="Start ISO e.g. 2025-10-04T09:00:00"),
    end: str = Query(..., description="End ISO e.g. 2025-10-04T17:00:00"),
    users: List[str] = Query(..., description='Each item is JSON: {"access_token":"...","refresh_token":"..."}'),
):
    """Calculate shared free time among multiple users."""
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        all_users_busy: List[List[Tuple[datetime, datetime]]] = []
        for user_str in users:
            user = json.loads(user_str)
            access_token = user.get("access_token")
            refresh_token = user.get("refresh_token")
            if not access_token or not refresh_token:
                return {"error": "Each user must provide access_token and refresh_token"}

            events = get_user_events(
                access_token,
                refresh_token,
                start_dt.isoformat() + "Z",
                end_dt.isoformat() + "Z",
            )
            busy_intervals = convert_to_busy_intervals(events)
            all_users_busy.append(busy_intervals)

        merged_busy = merge_busy_intervals(all_users_busy)
        free_intervals = get_free_intervals(merged_busy, start_dt, end_dt)

        return {
            "start_range": start_dt.isoformat(),
            "end_range": end_dt.isoformat(),
            "shared_free_time": [{"start": s.isoformat(), "end": e.isoformat()} for s, e in free_intervals],
        }

    except HttpError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}

@app.get("/user_free_time")
def user_free_time(
    start: str = Query(..., description="Start datetime ISO"),
    end: str = Query(..., description="End datetime ISO"),
    access_token: str = Query(...),
    refresh_token: str = Query(...),
):
    """Return free time for a single user."""
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        events = get_user_events(access_token, refresh_token, start_dt.isoformat() + "Z", end_dt.isoformat() + "Z")
        busy = convert_to_busy_intervals(events)
        merged_busy = merge_busy_intervals([busy])
        free = get_free_intervals(merged_busy, start_dt, end_dt)

        return {"free_time": [{"start": s.isoformat(), "end": e.isoformat()} for s, e in free]}

    except HttpError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}
