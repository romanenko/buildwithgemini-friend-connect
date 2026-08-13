"""FastAPI proxy & Web Application for FriendConnect."""

import os
import uuid

import google.auth
import google.auth.transport.requests
import httpx
from a2a.client import ClientConfig, ClientFactory
from a2a.types import (
    AgentCard,
    FilePart,
    Message,
    Part,
    Role,
    TaskArtifactUpdateEvent,
    TextPart,
    TransportProtocol,
)
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

try:
    from firestore_tools import get_match_document, save_match_contact_info, seed_demo_users
except ImportError:
    from frontend.firestore_tools import get_match_document, save_match_contact_info, seed_demo_users

RESOURCE = os.environ.get(
    "AGENT_ENGINE_RESOURCE_NAME",
    "projects/517434892559/locations/us-east1/reasoningEngines/1114869606192775168",
)
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")
LOCATION = RESOURCE.split("/locations/")[1].split("/")[0]

A2A_BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
    f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
)
A2A_CARD_URL = f"{A2A_BASE}/.well-known/agent-card.json"

_A2UI_MIME = "application/json+a2ui"

_creds, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)


def _auth_headers() -> dict[str, str]:
    _creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {_creds.token}",
        "Content-Type": "application/json",
    }


app = FastAPI(title="FriendConnect Platform")


@app.exception_handler(Exception)
async def _json_errors(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={
            "parts": [{"kind": "text", "text": f"Error: {type(exc).__name__}: {exc}"}]
        },
    )


_contexts: dict[str, str] = {}
_card: AgentCard | None = None


async def _get_card(client: httpx.AsyncClient) -> AgentCard:
    global _card
    if _card is None:
        resp = await client.get(A2A_CARD_URL)
        resp.raise_for_status()
        card = AgentCard(**resp.json())
        card.url = A2A_BASE
        _card = card
    return _card


def _extract_parts(parts: list) -> list[dict]:
    out: list[dict] = []
    for p in parts:
        root = getattr(p, "root", p)
        if isinstance(root, TextPart) and getattr(root, "text", None):
            out.append({"kind": "text", "text": root.text})
        elif getattr(root, "data", None) is not None:
            meta = getattr(root, "metadata", None) or {}
            mime = meta.get("mimeType") if isinstance(meta, dict) else None
            if mime == _A2UI_MIME:
                out.append({"kind": "a2ui", "data": root.data})
        elif isinstance(root, FilePart):
            uri = getattr(getattr(root, "file", None), "uri", None)
            if uri:
                out.append({"kind": "text", "text": uri})
    return out


# Route: Landing / Index Page
@app.get("/", response_class=HTMLResponse)
async def index_page():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FriendConnect - Find Your Vibe</title>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Outfit', sans-serif;
      background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
      color: #f8fafc;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
      text-align: center;
    }
    .hero-card {
      background: rgba(30, 41, 59, 0.85);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 2rem;
      max-width: 520px;
      width: 100%;
      padding: 2.5rem 2rem;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .badge {
      display: inline-block;
      background: rgba(139, 92, 246, 0.2);
      border: 1px solid rgba(139, 92, 246, 0.4);
      color: #a855f7;
      font-size: 0.85rem;
      font-weight: 700;
      padding: 0.4rem 1.1rem;
      border-radius: 9999px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 1.25rem;
    }
    h1 {
      font-size: 2.5rem;
      font-weight: 800;
      background: linear-gradient(90deg, #ffffff, #a855f7, #38bdf8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.85rem;
      letter-spacing: -0.02em;
    }
    p.pitch {
      font-size: 1.1rem;
      color: #cbd5e1;
      line-height: 1.5;
      margin-bottom: 2rem;
      font-weight: 400;
      max-width: 440px;
    }
    .cta-btn {
      width: 100%;
      max-width: 320px;
      background: linear-gradient(90deg, #ec4899, #8b5cf6, #3b82f6);
      background-size: 200% auto;
      color: #ffffff;
      font-size: 1.25rem;
      font-weight: 700;
      padding: 1.1rem 1.75rem;
      border: none;
      border-radius: 1rem;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.6rem;
      box-shadow: 0 10px 25px -5px rgba(139, 92, 246, 0.4);
      transition: all 0.25s ease;
      margin-bottom: 2rem;
    }
    .cta-btn:hover {
      background-position: right center;
      transform: translateY(-2px);
      box-shadow: 0 15px 30px -5px rgba(139, 92, 246, 0.6);
    }
    .qr-container {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 1.25rem;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100%;
      max-width: 260px;
    }
    .qr-title {
      font-size: 0.8rem;
      color: #94a3b8;
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.05em;
      margin-bottom: 0.75rem;
    }
    .qr-frame {
      background: #ffffff;
      padding: 0.6rem;
      border-radius: 0.75rem;
      display: inline-block;
    }
    .qr-frame img {
      width: 150px;
      height: 150px;
      display: block;
    }
    .session-indicator {
      margin-top: 1.25rem;
      font-size: 0.8rem;
      color: #64748b;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }
    .dot {
      width: 8px;
      height: 8px;
      background: #22c55e;
      border-radius: 50%;
      display: inline-block;
    }
  </style>
</head>
<body>
  <div class="hero-card">
    <div class="badge">AI Matchmaker</div>
    <h1>FriendConnect</h1>
    <p class="pitch">An AI matchmaker that finds your vibe, connects you over shared passions, and helps you make real lifelong friends.</p>
    
    <a href="/chat-ui" class="cta-btn">
      Find Friends ✨
    </a>

    <div class="qr-container">
      <div class="qr-title">Scan to open on phone 📱</div>
      <div class="qr-frame">
        <img id="qrCodeImg" alt="QR Code to open page on mobile">
      </div>
    </div>

    <div class="session-indicator">
      <span class="dot"></span>
      <span id="sessionStatus">Anonymous Session Active</span>
    </div>
  </div>

  <script>
    // Ensure persistent Firebase anonymous session ID
    let anonId = localStorage.getItem('friendconnect_anon_id');
    if (!anonId) {
      anonId = 'anon_' + Math.random().toString(36).substring(2, 12);
      localStorage.setItem('friendconnect_anon_id', anonId);
    }
    document.getElementById('sessionStatus').textContent = 'Session: ' + anonId;

    // Dynamically generate QR code pointing to current window location URL
    const currentUrl = window.location.href;
    const qrImg = document.getElementById('qrCodeImg');
    qrImg.src = 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=' + encodeURIComponent(currentUrl);
  </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


# Route: Agent Chat UI Page
@app.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui_page():
    static_file = os.path.join(STATIC_DIR, "index.html")
    with open(static_file, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)


# Route: Agent Chat API Endpoint
@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    message = body.get("message", "")
    user_id = body.get("user_id") or "web-user"
    parts: list[dict] = []

    async with httpx.AsyncClient(headers=_auth_headers(), timeout=120) as client:
        card = await _get_card(client)
        factory = ClientFactory(
            ClientConfig(
                supported_transports=[
                    TransportProtocol.jsonrpc,
                    TransportProtocol.http_json,
                ],
                httpx_client=client,
            )
        )
        a2a_client = factory.create(card)

        msg = Message(
            message_id=str(uuid.uuid4()),
            role=Role.user,
            parts=[Part(root=TextPart(text=message))],
            context_id=_contexts.get(user_id),
        )

        last_task = None
        got_artifact_update = False
        async for event in a2a_client.send_message(msg):
            if not isinstance(event, tuple):
                continue
            task, update = event
            if task is not None:
                last_task = task
                if getattr(task, "context_id", None):
                    _contexts[user_id] = task.context_id
            if isinstance(update, TaskArtifactUpdateEvent):
                got_artifact_update = True
                parts.extend(_extract_parts(update.artifact.parts))

        if not got_artifact_update and last_task is not None:
            for artifact in getattr(last_task, "artifacts", None) or []:
                parts.extend(_extract_parts(artifact.parts))

    if not parts:
        parts = [{"kind": "text", "text": "(The agent didn't return a reply.)"}]
    return JSONResponse({"parts": parts})


# Route: Match Management Link API & Page
@app.get("/api/match/{link_id}")
async def get_match_api(link_id: str):
    res = get_match_document(link_id)
    return JSONResponse(res)


@app.post("/api/match/{link_id}/contact")
async def post_match_contact(link_id: str, req: Request):
    body = await req.json()
    contact_info = body.get("contact_info", "").strip()
    submitter_name = body.get("submitter_name", "").strip()
    if not contact_info:
        return JSONResponse(
            {"status": "error", "message": "Contact info cannot be empty."},
            status_code=400,
        )

    res = save_match_contact_info(
        link_id=link_id, contact_info=contact_info, submitter_name=submitter_name
    )
    return JSONResponse(res)


@app.get("/match/{link_id}", response_class=HTMLResponse)
async def match_page(link_id: str):
    res = get_match_document(link_id)
    if res.get("status") != "success":
        return HTMLResponse(
            content=f"""<!DOCTYPE html>
<html>
<head><title>Match Not Found - FriendConnect</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
<style>
body {{ font-family: 'Outfit', sans-serif; background: #0f172a; color: #f8fafc; display:flex; align-items:center; justify-content:center; min-height:100vh; margin:0; text-align:center; }}
.card {{ background: #1e293b; padding: 2rem; border-radius: 1rem; border: 1px solid #334155; max-width: 400px; width:90%; }}
h1 {{ color: #f43f5e; font-size: 1.5rem; margin-bottom: 0.5rem; }}
p {{ color: #94a3b8; }}
a {{ color: #38bdf8; text-decoration: none; font-weight: 600; display:inline-block; margin-top: 1rem; }}
</style>
</head>
<body>
<div class="card">
  <h1>Match Link Not Found</h1>
  <p>The match link '{link_id}' is invalid or expired.</p>
  <a href="/">← Return to FriendConnect</a>
</div>
</body>
</html>""",
            status_code=404,
        )

    match_data = res.get("match", {})
    user1 = res.get("user1_profile", {})
    user2 = res.get("user2_profile", {})

    shared_interest = match_data.get("shared_interest", "Shared Interests")
    icebreaker = match_data.get(
        "icebreaker_question", "By the way, what got you into this hobby?"
    )
    image_url = match_data.get(
        "kawaii_image_url",
        "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop",
    )

    submissions = match_data.get("contact_submissions", [])
    submissions_html = ""
    if submissions:
        for s in submissions:
            submissions_html += f"""
            <div class="contact-pill">
              <span class="submitter">{s.get('submitter_name', 'Participant')}:</span>
              <span class="info">{s.get('contact_info', '')}</span>
            </div>"""
    else:
        submissions_html = "<p class='empty-contacts'>No contact details shared yet. Be the first below!</p>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>You've Got a Friend Match! 🎉 - FriendConnect</title>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Outfit', sans-serif;
      background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
      color: #f8fafc;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
    }}
    .container {{
      background: rgba(30, 41, 59, 0.85);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 1.5rem;
      max-width: 580px;
      width: 100%;
      padding: 2.25rem;
      box-shadow: 0 20px 40px rgba(0,0,0,0.4);
      text-align: center;
    }}
    .badge {{
      display: inline-block;
      background: linear-gradient(90deg, #ec4899, #8b5cf6);
      color: #ffffff;
      font-weight: 700;
      font-size: 0.85rem;
      padding: 0.35rem 1rem;
      border-radius: 9999px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 1rem;
    }}
    h1 {{
      font-size: 1.85rem;
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 0.5rem;
    }}
    .names {{
      color: #38bdf8;
      font-weight: 600;
      font-size: 1.1rem;
      margin-bottom: 1.25rem;
    }}
    .image-frame {{
      width: 100%;
      max-height: 320px;
      border-radius: 1rem;
      overflow: hidden;
      margin-bottom: 1.5rem;
      border: 2px solid rgba(255,255,255,0.1);
      box-shadow: 0 10px 25px rgba(0,0,0,0.3);
      background: #0f172a;
    }}
    .image-frame img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }}
    .icebreaker-box {{
      background: rgba(15, 23, 42, 0.6);
      border-left: 4px solid #38bdf8;
      padding: 1rem 1.25rem;
      border-radius: 0.5rem;
      text-align: left;
      margin-bottom: 1.75rem;
    }}
    .icebreaker-label {{
      font-size: 0.8rem;
      color: #94a3b8;
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.05em;
      margin-bottom: 0.25rem;
    }}
    .icebreaker-text {{
      color: #f1f5f9;
      font-size: 1.05rem;
      font-weight: 500;
      font-style: italic;
    }}
    .section-title {{
      font-size: 1.1rem;
      font-weight: 700;
      color: #f8fafc;
      margin-bottom: 0.75rem;
      text-align: left;
    }}
    .shared-contacts {{
      margin-bottom: 1.75rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }}
    .contact-pill {{
      background: rgba(51, 65, 85, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 0.75rem 1rem;
      border-radius: 0.75rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.95rem;
    }}
    .submitter {{
      color: #a855f7;
      font-weight: 700;
    }}
    .info {{
      color: #38bdf8;
      font-weight: 600;
      word-break: break-all;
    }}
    .empty-contacts {{
      color: #64748b;
      font-size: 0.9rem;
      font-style: italic;
      text-align: left;
      padding: 0.5rem 0;
    }}
    .form-box {{
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.08);
      padding: 1.25rem;
      border-radius: 1rem;
      text-align: left;
    }}
    .input-group {{
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      margin-bottom: 0.85rem;
    }}
    label {{
      font-size: 0.85rem;
      color: #cbd5e1;
      font-weight: 600;
    }}
    input {{
      background: #1e293b;
      border: 1px solid #475569;
      color: #ffffff;
      padding: 0.65rem 0.85rem;
      border-radius: 0.5rem;
      font-family: inherit;
      font-size: 0.95rem;
      outline: none;
    }}
    input:focus {{
      border-color: #a855f7;
    }}
    button {{
      width: 100%;
      background: linear-gradient(90deg, #8b5cf6, #3b82f6);
      color: white;
      font-weight: 700;
      font-size: 1rem;
      padding: 0.75rem;
      border: none;
      border-radius: 0.5rem;
      cursor: pointer;
      transition: transform 0.15s ease, opacity 0.15s ease;
    }}
    button:hover {{
      opacity: 0.95;
      transform: translateY(-1px);
    }}
    .footer-link {{
      margin-top: 1.5rem;
      display: inline-block;
      color: #64748b;
      font-size: 0.85rem;
      text-decoration: none;
    }}
    .footer-link:hover {{ color: #94a3b8; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="badge">Match Confirmed ✨</div>
    <h1>You both love {shared_interest}!</h1>
    <div class="names">{user1.get('name', 'Participant 1')} & {user2.get('name', 'Participant 2')}</div>

    <div class="image-frame">
      <img src="{image_url}" alt="Cute Kawaii Friend Match Illustration">
    </div>

    <div class="icebreaker-box">
      <div class="icebreaker-label">By the way, question...</div>
      <div class="icebreaker-text">"{icebreaker}"</div>
    </div>

    <div class="section-title">Shared Contact Methods</div>
    <div class="shared-contacts" id="contactsList">
      {submissions_html}
    </div>

    <div class="form-box">
      <div class="section-title" style="margin-bottom:0.5rem; font-size:1rem;">Connect Outside the Platform</div>
      <p style="color:#94a3b8; font-size:0.85rem; margin-bottom:1rem;">Share your Instagram, phone number, or Telegram so your match can reach out!</p>
      
      <div class="input-group">
        <label for="nameInput">Your Name or Handle</label>
        <input type="text" id="nameInput" placeholder="e.g. Alex or @alex_m">
      </div>
      <div class="input-group">
        <label for="contactInput">Contact Method / Handle / Phone</label>
        <input type="text" id="contactInput" placeholder="e.g. +1 555-0199 or IG: @alex_morgan">
      </div>
      <button onclick="submitContact()">Share Contact Details 🚀</button>
    </div>

    <a href="/" class="footer-link">← Back to FriendConnect Home</a>
  </div>

  <script>
    async function submitContact() {{
      const name = document.getElementById('nameInput').value.trim();
      const contact = document.getElementById('contactInput').value.trim();
      if (!contact) {{
        alert('Please enter a phone number, Instagram handle, or email.');
        return;
      }}

      try {{
        const resp = await fetch('/api/match/{link_id}/contact', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ submitter_name: name, contact_info: contact }})
        }});
        const data = await resp.json();
        if (data.status === 'success') {{
          location.reload();
        }} else {{
          alert('Failed to save contact info: ' + (data.message || 'Unknown error'));
        }}
      }} catch (err) {{
        alert('Error connecting to server: ' + err);
      }}
    }}
  </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


# Special Demo Seeding Route
@app.post("/api/demo/seed")
@app.get("/api/demo/seed")
@app.get("/demo/seed")
async def demo_seed():
    res = seed_demo_users(count=5)
    return JSONResponse(res)


# Mount static files for Chat UI using absolute directory path
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
