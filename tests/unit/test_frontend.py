"""Unit tests for frontend FastAPI proxy, Landing Page, Chat UI, and Match Link routes."""

from fastapi.testclient import TestClient

from app.firestore_tools import create_match_document
from frontend.main import app

client = TestClient(app)


def test_landing_index_page():
    """Verify landing page title, pitch, CTA button, and QR code container."""
    res = client.get("/")
    assert res.status_code == 200
    assert "FriendConnect" in res.text
    assert "An AI matchmaker that finds your vibe" in res.text
    assert "Find Friends" in res.text
    assert "qrCodeImg" in res.text
    assert "friendconnect_anon_id" in res.text


def test_chat_ui_page():
    """Verify chat UI page route."""
    res = client.get("/chat-ui")
    assert res.status_code == 200
    assert "FriendConnect - Chat Agent" in res.text
    assert "friendconnect_anon_id" in res.text


def test_match_page_and_contact_submission():
    """Verify creating a match document, viewing the match page, and submitting contact info."""
    match_res = create_match_document(
        user1_id="alex_m",
        user2_id="sam_k",
        shared_interest="Pickleball & Racket Sports",
        icebreaker_question="By the way, how often do you play pickleball?",
        kawaii_image_url="https://storage.googleapis.com/friend-connect-media-qwiklabs-gcp-03-75b4c3d63ad8/kawaii_pickleball_bf1af2.jpg",
    )
    assert match_res["status"] == "success"
    link_id = match_res["unique_link_id"]

    # 1. Test GET /match/{link_id}
    res = client.get(f"/match/{link_id}")
    assert res.status_code == 200
    assert "You both love Pickleball &amp; Racket Sports!" in res.text or "You both love Pickleball & Racket Sports!" in res.text
    assert "kawaii_pickleball_bf1af2.jpg" in res.text

    # 2. Test POST /api/match/{link_id}/contact
    contact_res = client.post(
        f"/api/match/{link_id}/contact",
        json={"submitter_name": "Alex", "contact_info": "IG: @alex_m_pickleball"},
    )
    assert contact_res.status_code == 200
    assert contact_res.json()["status"] == "success"

    # 3. Test GET /match/{link_id} again to verify submitted contact appears
    res2 = client.get(f"/match/{link_id}")
    assert res2.status_code == 200
    assert "IG: @alex_m_pickleball" in res2.text
