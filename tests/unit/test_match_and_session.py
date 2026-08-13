"""Unit tests for anonymous session binding, match document creation, and web routes."""

from fastapi.testclient import TestClient
from app.fast_api_app import app
from app.firestore_tools import (
    bind_session_to_profile,
    get_profile_by_session_id,
    create_match_document,
    get_match_document,
    save_user_profile,
)

client = TestClient(app)


def test_anonymous_session_binding():
    """Verify binding an anonymous browser session ID to a user profile."""
    anon_session_id = "anon_session_test_12345"
    test_user_id = "alex_m"

    # Bind session to profile
    res = bind_session_to_profile(anon_session_id, test_user_id)
    assert res["status"] == "success"

    # Retrieve profile by session ID
    profile_res = get_profile_by_session_id(anon_session_id)
    assert profile_res["status"] == "success"
    assert profile_res["profile"]["user_id"] == test_user_id
    assert profile_res["profile"]["name"] == "Alex Morgan"


def test_create_and_get_match_document():
    """Verify creating a match document containing both user IDs and unique link ID."""
    u1 = "alex_m"
    u2 = "sam_k"

    match_res = create_match_document(
        user1_id=u1,
        user2_id=u2,
        shared_interest="Outdoors & Nature",
        icebreaker_question="By the way, what is your favorite hiking trail?",
        kawaii_image_url="https://example.com/kawaii_hiking.png",
    )

    assert match_res["status"] == "success"
    assert "unique_link_id" in match_res
    unique_link_id = match_res["unique_link_id"]
    assert unique_link_id.startswith("link-")

    # Fetch match document
    doc_res = get_match_document(unique_link_id)
    assert doc_res["status"] == "success"
    match_data = doc_res["match"]
    assert match_data["user1_id"] == u1
    assert match_data["user2_id"] == u2
    assert match_data["shared_interest"] == "Outdoors & Nature"

    # Check that both profiles are resolved
    assert doc_res["user1_profile"]["name"] == "Alex Morgan"
    assert doc_res["user2_profile"]["name"] == "Sam Kim"


def test_match_web_routes():
    """Verify FastAPI /api/match/{link_id} and /match/{link_id} web endpoints."""
    # Create a match
    match_res = create_match_document(
        user1_id="jordan_t",
        user2_id="alex_m",
        shared_interest="Outdoors & Nature",
        icebreaker_question="By the way, sunrise or sunset hikes?",
    )
    link_id = match_res["unique_link_id"]

    # Test JSON API endpoint
    json_response = client.get(f"/api/match/{link_id}")
    assert json_response.status_code == 200
    json_data = json_response.json()
    assert json_data["status"] == "success"
    assert json_data["match"]["user1_id"] == "jordan_t"

    # Test HTML Web route endpoint
    html_response = client.get(f"/match/{link_id}")
    assert html_response.status_code == 200
    assert "text/html" in html_response.headers["content-type"]
    assert "Jordan Taylor" in html_response.text
    assert "Alex Morgan" in html_response.text
    assert "By the way..." in html_response.text
