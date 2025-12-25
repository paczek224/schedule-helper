import os, json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import tempfile

app = FastAPI()

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
REDIRECT_URI = "https://schedule-helper-wr80.onrender.com/oauth2callback"

@app.get("/", response_class=HTMLResponse)
async def home():
    return "<h1>Hello World!</h1><p><a href='/calendar'>Dodaj wydarzenie do Google Calendar</a></p>"

@app.get("/calendar")
async def start_calendar_flow():
    # Zapisz credentials.json tymczasowo do pliku
    credentials_info = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not credentials_info:
        return HTMLResponse("Brak credentials.json w zmiennych środowiskowych.", status_code=500)

    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(credentials_info)
        tmp_file_path = f.name

    flow = Flow.from_client_secrets_file(tmp_file_path, scopes=SCOPES, redirect_uri=REDIRECT_URI)
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )
    return RedirectResponse(url=authorization_url)

@app.get("/oauth2callback")
async def oauth2callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("Brak kodu autoryzacyjnego.", status_code=400)

    credentials_info = os.getenv("GOOGLE_CREDENTIALS_JSON")
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(credentials_info)
        tmp_file_path = f.name

    flow = Flow.from_client_secrets_file(tmp_file_path, scopes=SCOPES, redirect_uri=REDIRECT_URI)
    flow.fetch_token(code=code)
    credentials = flow.credentials

    service = build("calendar", "v3", credentials=credentials)
    now = datetime.now()
    event = {
        "summary": "Hello World Event",
        "description": "Dodane przez FastAPI",
        "start": {"dateTime": now.isoformat() + "Z", "timeZone": "Europe/Warsaw"},
        "end": {"dateTime": (now + timedelta(hours=1)).isoformat() + "Z", "timeZone": "Europe/Warsaw"}
    }
    created_event = service.events().insert(calendarId="primary", body=event).execute()
    return HTMLResponse(f"Wydarzenie utworzone: <a href='{created_event.get('htmlLink')}' target='_blank'>Sprawdź w kalendarzu</a>")