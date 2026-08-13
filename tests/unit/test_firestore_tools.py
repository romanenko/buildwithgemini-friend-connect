"""Unit tests for Firestore database tools."""

import pytest
from app.firestore_tools import (
    get_user_profile,
    save_user_profile,
    search_candidate_profiles,
    update_profile_status,
)


def test_firestore_seeded_profile_read():
    """Verify reading a seeded profile from Firestore."""
    result = get_user_profile("alex_m")
    assert result["status"] == "success"
    profile = result["profile"]
    assert profile["name"] == "Alex Morgan"
    assert "Pickleball & Racket Sports" in profile["interests"]


def test_firestore_save_and_update():
    """Verify creating/updating a profile and modifying status in Firestore."""
    test_user_id = "test_unit_user"
    save_res = save_user_profile(
        user_id=test_user_id,
        name="Test Runner",
        bio="I love unit testing and high coverage.",
        interests=["Tech & Coding", "Gaming & Esports"],
        status="looking_for_friends",
    )
    assert save_res["status"] == "success"

    # Read back
    read_res = get_user_profile(test_user_id)
    assert read_res["status"] == "success"
    assert read_res["profile"]["name"] == "Test Runner"

    # Update status
    update_res = update_profile_status(test_user_id, status="matched")
    assert update_res["status"] == "success"
    assert update_res["new_status"] == "matched"

    # Verify updated status
    read_updated = get_user_profile(test_user_id)
    assert read_updated["profile"]["status"] == "matched"


def test_firestore_search_candidate_profiles():
    """Verify querying candidates with status='looking_for_friends'."""
    candidates = search_candidate_profiles(status="looking_for_friends")
    assert isinstance(candidates, list)
    assert len(candidates) >= 1
    # Check that seeded user alex_m or sam_k is in results
    names = [c["name"] for c in candidates]
    valid_names = {"Sam Kim", "Alex Morgan", "Casey Lee", "Taylor Reed", "Jordan Taylor"}
    assert any(name in valid_names for name in names)
