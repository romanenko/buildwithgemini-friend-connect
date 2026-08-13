# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib
import os
from collections.abc import AsyncIterator

import google.auth
from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import Runner
from google.cloud import logging as google_cloud_logging

from app.app_utils import services
from app.app_utils.a2a import attach_a2a_routes
from app.app_utils.reasoning_engine_adapter import (
    attach_reasoning_engine_routes,
)
from app.app_utils.typing import Feedback

load_dotenv()
otel_to_cloud = os.environ.get(
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY", ""
).lower() in ("true", "1")
_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Runner for the A2A path, sharing the same session/artifact services as the
    # adk_api and reasoning_engine paths (see services.py). Imported here so the
    # agent is built after env/telemetry setup.
    from app.agent import app as adk_app
    from app.agent import root_agent

    runner = Runner(
        app=adk_app,
        session_service=services.get_session_service(),
        artifact_service=services.get_artifact_service(),
        auto_create_session=True,
    )
    # Shared by the A2A path and the reasoning_engine adapter routes.
    app.state.runner = runner
    app.state.agent_app_name = adk_app.name
    await attach_a2a_routes(
        app,
        agent=root_agent,
        runner=runner,
        task_store=InMemoryTaskStore(),
        rpc_path=f"/a2a/{adk_app.name}",
    )
    yield


app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=services.ARTIFACT_SERVICE_URI,
    allow_origins=allow_origins,
    session_service_uri=services.SESSION_SERVICE_URI,
    otel_to_cloud=otel_to_cloud,
    lifespan=lifespan,
)
app.title = "interest-analyzer"
app.description = "API for interacting with the Agent interest-analyzer"


# Proxy routes so the Vertex AI Console Playground (reasoning_engine SDK) can
# talk to this agent alongside the native adk_api routes.
attach_reasoning_engine_routes(app)


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


@app.get("/api/match/{link_id}")
def get_match_api(link_id: str) -> dict:
    """JSON endpoint for retrieving a match document and connected user profiles.

    Args:
        link_id: Unique link ID or match document ID.
    """
    from app.firestore_tools import get_match_document

    return get_match_document(link_id)


@app.get("/match/{link_id}")
def view_match_page(link_id: str):
    """Web route for viewing a match pair page via its unique link ID."""
    from fastapi.responses import HTMLResponse
    from app.firestore_tools import get_match_document

    match_res = get_match_document(link_id)
    if match_res.get("status") != "success":
        return HTMLResponse(
            status_code=404,
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>Match Not Found - FriendConnect</title></head>
            <body style="font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 4rem;">
                <h1>Match Link Not Found</h1>
                <p>Sorry! This match link may have expired or does not exist.</p>
            </body>
            </html>
            """,
        )

    match_data = match_res["match"]
    u1 = match_res.get("user1_profile", {})
    u2 = match_res.get("user2_profile", {})

    u1_name = u1.get("name", "User 1")
    u2_name = u2.get("name", "User 2")
    shared_interest = match_data.get("shared_interest", "Shared Passion")
    icebreaker = match_data.get("icebreaker_question", "By the way, what got you into this hobby?")
    image_url = match_data.get("kawaii_image_url", "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop")
    u1_link = u1.get("contact_link", "#")
    u2_link = u2.get("contact_link", "#")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FriendConnect Match — {u1_name} & {u2_name}</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #0b0f19;
                --card-bg: rgba(30, 41, 59, 0.7);
                --accent: #ec4899;
                --accent-glow: rgba(236, 72, 153, 0.4);
                --border: rgba(255, 255, 255, 0.1);
            }}
            body {{
                margin: 0;
                font-family: 'Outfit', sans-serif;
                background: var(--bg);
                color: #f8fafc;
                display: flex;
                flex-direction: column;
                align-items: center;
                min-height: 100vh;
                padding: 2rem 1rem;
                box-sizing: border-box;
            }}
            .container {{
                max-width: 680px;
                width: 100%;
                background: var(--card-bg);
                backdrop-filter: blur(16px);
                border: 1px solid var(--border);
                border-radius: 24px;
                padding: 2.5rem;
                box-shadow: 0 20px 40px rgba(0,0,0,0.5);
                text-align: center;
            }}
            .badge {{
                display: inline-block;
                background: linear-gradient(135deg, #ec4899, #8b5cf6);
                color: white;
                font-weight: 700;
                font-size: 0.875rem;
                padding: 0.5rem 1.25rem;
                border-radius: 9999px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 1.5rem;
            }}
            h1 {{
                font-size: 2.2rem;
                margin: 0 0 0.5rem 0;
                background: linear-gradient(to right, #f472b6, #c084fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .profiles-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
                margin: 2rem 0;
            }}
            .profile-card {{
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 1.25rem;
                text-align: left;
            }}
            .profile-card h3 {{
                margin: 0 0 0.5rem 0;
                color: #f384d4;
            }}
            .profile-card p {{
                font-size: 0.9rem;
                color: #cbd5e1;
                margin: 0 0 0.5rem 0;
            }}
            .kawaii-card {{
                margin: 2rem 0;
                border-radius: 20px;
                overflow: hidden;
                border: 2px solid rgba(244, 114, 182, 0.3);
                box-shadow: 0 10px 30px var(--accent-glow);
            }}
            .kawaii-card img {{
                width: 100%;
                max-height: 380px;
                object-fit: cover;
                display: block;
            }}
            .icebreaker-box {{
                background: rgba(236, 72, 153, 0.1);
                border-left: 4px solid var(--accent);
                padding: 1.25rem;
                border-radius: 12px;
                text-align: left;
                margin-bottom: 2rem;
            }}
            .icebreaker-title {{
                font-weight: 700;
                color: #f472b6;
                margin-bottom: 0.25rem;
            }}
            .btn-connect {{
                display: inline-block;
                background: linear-gradient(135deg, #ec4899, #8b5cf6);
                color: white;
                text-decoration: none;
                font-weight: 700;
                padding: 1rem 2rem;
                border-radius: 12px;
                transition: transform 0.2s, box-shadow 0.2s;
                box-shadow: 0 4px 15px var(--accent-glow);
            }}
            .btn-connect:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px var(--accent-glow);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <span class="badge">Match Confirmed ✨</span>
            <h1>{u1_name} ❤️ {u2_name}</h1>
            <p style="color: #94a3b8;">Shared Passion: <strong>{shared_interest}</strong></p>

            <div class="profiles-grid">
                <div class="profile-card">
                    <h3>{u1_name}</h3>
                    <p>{u1.get('bio', 'Looking for friends with shared interests!')}</p>
                    <small style="color: #94a3b8;">📍 {u1.get('location', 'Bay Area')}</small>
                </div>
                <div class="profile-card">
                    <h3>{u2_name}</h3>
                    <p>{u2.get('bio', 'Looking for friends with shared interests!')}</p>
                    <small style="color: #94a3b8;">📍 {u2.get('location', 'Bay Area')}</small>
                </div>
            </div>

            <div class="kawaii-card">
                <img src="{image_url}" alt="Kawaii {shared_interest} Art" />
            </div>

            <div class="icebreaker-box">
                <div class="icebreaker-title">💬 By the way...</div>
                <div>"{icebreaker}"</div>
            </div>

            <a href="{u1_link}" class="btn-connect" target="_blank">Connect Outside Platform 📱</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
