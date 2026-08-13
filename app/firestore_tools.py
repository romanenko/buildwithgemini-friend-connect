"""Firestore database integration tools for FriendConnect agent."""

import datetime
import uuid

from google.cloud import firestore
from google.cloud.firestore import FieldFilter

# CRITICAL: Hardcode the project ID as a literal string to avoid Agent Platform
# runtime project number issues.
PROJECT_ID = "qwiklabs-gcp-03-75b4c3d63ad8"
COLLECTION_NAME = "user_profiles"
MATCHES_COLLECTION_NAME = "matches"
ANON_SESSIONS_COLLECTION = "anon_sessions"


def _get_db_client() -> firestore.Client:
    """Returns a Firestore client instance bound to the explicit project ID."""
    return firestore.Client(project=PROJECT_ID)


def get_user_profile(user_id: str) -> dict:
    """Retrieves a user profile document from Firestore by user_id."""
    db = _get_db_client()
    doc_ref = db.collection(COLLECTION_NAME).document(user_id)
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        data["user_id"] = user_id
        return {"status": "success", "profile": data}
    else:
        return {
            "status": "not_found",
            "message": f"No profile found for user_id '{user_id}'.",
        }


def save_user_profile(
    user_id: str,
    name: str,
    bio: str,
    interests: list[str],
    status: str = "looking_for_friends",
    location: str = "San Francisco, CA",
    vibe_notes: str = "",
    anon_session_id: str = "",
) -> dict:
    """Creates or updates a user profile document in Firestore and links it to an anonymous session."""
    db = _get_db_client()
    doc_ref = db.collection(COLLECTION_NAME).document(user_id)

    contact_link = f"https://connect.friendconnect.app/u/{user_id}"
    profile_data = {
        "user_id": user_id,
        "name": name,
        "bio": bio,
        "interests": interests,
        "status": status,
        "location": location,
        "vibe_notes": vibe_notes,
        "contact_link": contact_link,
        "anon_session_id": anon_session_id,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    doc_ref.set(profile_data, merge=True)

    if anon_session_id:
        bind_session_to_profile(anon_session_id, user_id)

    return {
        "status": "success",
        "message": f"Saved profile for {name} ({user_id}) in Firestore.",
        "profile": profile_data,
    }


def bind_session_to_profile(anon_session_id: str, user_id: str) -> dict:
    """Binds an anonymous browser session identity to a user profile in Firestore."""
    db = _get_db_client()
    session_ref = db.collection(ANON_SESSIONS_COLLECTION).document(anon_session_id)
    mapping_data = {
        "anon_session_id": anon_session_id,
        "user_id": user_id,
        "bound_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    session_ref.set(mapping_data, merge=True)

    # Also update profile
    profile_ref = db.collection(COLLECTION_NAME).document(user_id)
    profile_ref.set({"anon_session_id": anon_session_id}, merge=True)

    return {
        "status": "success",
        "message": f"Bound anonymous session '{anon_session_id}' to profile '{user_id}'.",
    }


def get_profile_by_session_id(anon_session_id: str) -> dict:
    """Retrieves a user profile bound to an anonymous session ID."""
    db = _get_db_client()
    session_ref = db.collection(ANON_SESSIONS_COLLECTION).document(anon_session_id)
    doc = session_ref.get()

    if doc.exists:
        user_id = doc.to_dict().get("user_id")
        if user_id:
            return get_user_profile(user_id)

    # Fallback query directly on user_profiles
    query = db.collection(COLLECTION_NAME).where(
        filter=FieldFilter("anon_session_id", "==", anon_session_id)
    )
    for profile_doc in query.stream():
        data = profile_doc.to_dict()
        data["user_id"] = profile_doc.id
        return {"status": "success", "profile": data}

    return {
        "status": "not_found",
        "message": f"No profile bound to anonymous session '{anon_session_id}'.",
    }


def search_candidate_profiles(
    status: str = "looking_for_friends", exclude_user_id: str = ""
) -> list[dict]:
    """Retrieves all candidate profiles in Firestore filtered by status."""
    db = _get_db_client()
    collection_ref = db.collection(COLLECTION_NAME)
    query = collection_ref.where(filter=FieldFilter("status", "==", status))

    candidates = []
    for doc in query.stream():
        data = doc.to_dict()
        if exclude_user_id and data.get("user_id") == exclude_user_id:
            continue
        candidates.append(data)

    return candidates


def update_profile_status(user_id: str, status: str) -> dict:
    """Updates the lifecycle status field of a user profile in Firestore."""
    db = _get_db_client()
    doc_ref = db.collection(COLLECTION_NAME).document(user_id)
    doc_ref.update(
        {
            "status": status,
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    )

    return {
        "status": "success",
        "user_id": user_id,
        "new_status": status,
    }


def create_match_document(
    user1_id: str,
    user2_id: str,
    shared_interest: str,
    icebreaker_question: str = "By the way, what got you into this hobby?",
    kawaii_image_url: str = "",
) -> dict:
    """Creates a match document in the matches collection containing both user IDs and a unique link ID."""
    db = _get_db_client()

    unique_link_id = f"link-{uuid.uuid4().hex[:12]}"
    match_id = f"match_{user1_id}_{user2_id}"

    if not kawaii_image_url:
        kawaii_image_url = "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop"

    match_data = {
        "match_id": match_id,
        "user1_id": user1_id,
        "user2_id": user2_id,
        "unique_link_id": unique_link_id,
        "shared_interest": shared_interest,
        "icebreaker_question": icebreaker_question,
        "kawaii_image_url": kawaii_image_url,
        "match_url": f"/match/{unique_link_id}",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    db.collection(MATCHES_COLLECTION_NAME).document(match_id).set(match_data)
    db.collection(MATCHES_COLLECTION_NAME).document(unique_link_id).set(match_data)

    update_profile_status(user1_id, "matched")
    update_profile_status(user2_id, "matched")

    return {
        "status": "success",
        "match_id": match_id,
        "unique_link_id": unique_link_id,
        "match_url": f"/match/{unique_link_id}",
        "match": match_data,
    }


def get_match_document(link_id: str) -> dict:
    """Retrieves a match document by unique_link_id or match_id, resolving both user profiles."""
    db = _get_db_client()
    doc_ref = db.collection(MATCHES_COLLECTION_NAME).document(link_id)
    doc = doc_ref.get()

    if not doc.exists:
        query = db.collection(MATCHES_COLLECTION_NAME).where(
            filter=FieldFilter("unique_link_id", "==", link_id)
        )
        for match_doc in query.stream():
            doc = match_doc
            break

    if doc.exists:
        match_data = doc.to_dict()
        user1_profile = get_user_profile(match_data.get("user1_id", "")).get("profile", {})
        user2_profile = get_user_profile(match_data.get("user2_id", "")).get("profile", {})

        return {
            "status": "success",
            "match": match_data,
            "user1_profile": user1_profile,
            "user2_profile": user2_profile,
        }
    else:
        return {
            "status": "not_found",
            "message": f"No match found for link ID '{link_id}'.",
        }


def save_match_contact_info(link_id: str, contact_info: str, submitter_name: str = "") -> dict:
    """Saves contact info submitted by a participant for a match in Firestore."""
    db = _get_db_client()
    doc_ref = db.collection(MATCHES_COLLECTION_NAME).document(link_id)
    doc = doc_ref.get()

    if not doc.exists:
        query = db.collection(MATCHES_COLLECTION_NAME).where(
            filter=FieldFilter("unique_link_id", "==", link_id)
        )
        for match_doc in query.stream():
            doc_ref = match_doc.reference
            doc = match_doc
            break

    if not doc.exists:
        return {"status": "not_found", "message": f"Match '{link_id}' not found."}

    match_data = doc.to_dict() or {}
    contacts = match_data.get("contact_submissions", [])

    new_entry = {
        "submitter_name": submitter_name or "Matched Participant",
        "contact_info": contact_info,
        "submitted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    contacts.append(new_entry)

    doc_ref.set({"contact_submissions": contacts}, merge=True)

    match_id = match_data.get("match_id")
    if match_id and match_id != doc_ref.id:
        db.collection(MATCHES_COLLECTION_NAME).document(match_id).set({"contact_submissions": contacts}, merge=True)

    return {"status": "success", "contact_submissions": contacts}


def seed_demo_users(count: int = 5) -> dict:
    """Seeds a batch of demo user profiles into Firestore with status='looking_for_friends'."""
    db = _get_db_client()
    demo_samples = [
        {
            "user_id": "demo_maya_p",
            "name": "Maya Patel",
            "bio": "Pickleball player on weekends, home chef & sourdough baking fanatic!",
            "interests": ["Pickleball & Racket Sports", "Cooking & Culinary Arts"],
            "status": "looking_for_friends",
            "location": "San Francisco, CA",
            "vibe_notes": "Energetic, competitive, loves food tours",
        },
        {
            "user_id": "demo_carlos_r",
            "name": "Carlos Rodriguez",
            "bio": "Avid mountain hiker, drone photographer, and nature enthusiast.",
            "interests": ["Outdoors & Nature", "Photography & Videography"],
            "status": "looking_for_friends",
            "location": "Oakland, CA",
            "vibe_notes": "Calm, adventurous, loves early morning trail runs",
        },
        {
            "user_id": "demo_aria_c",
            "name": "Aria Chen",
            "bio": "AI engineer by day, tabletop RPG gamer & indie game dev by night.",
            "interests": ["Technology & Gadgets", "Gaming & Esports", "Board Games & Tabletop"],
            "status": "looking_for_friends",
            "location": "San Jose, CA",
            "vibe_notes": "Geeky, thoughtful, loves strategy games",
        },
        {
            "user_id": "demo_jordan_s",
            "name": "Jordan Smith",
            "bio": "Restoring classic 70s cars and crafting custom hardwood furniture.",
            "interests": ["Cars & Automotive", "Crafting & DIY"],
            "status": "looking_for_friends",
            "location": "Berkeley, CA",
            "vibe_notes": "Hands-on, creative, passionate builder",
        },
        {
            "user_id": "demo_chloe_t",
            "name": "Chloe Taylor",
            "bio": "Yoga teacher, plant mom with 40+ houseplants, and acoustic guitarist.",
            "interests": ["Wellness & Mindfulness", "Gardening & Horticulture", "Music & Audio"],
            "status": "looking_for_friends",
            "location": "San Francisco, CA",
            "vibe_notes": "Warm, peaceful, grounded and musical",
        },
    ]

    seeded_ids = []
    for user in demo_samples[:count]:
        user_id = user["user_id"]
        user["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        db.collection(COLLECTION_NAME).document(user_id).set(user, merge=True)
        seeded_ids.append(user_id)

    return {
        "status": "success",
        "message": f"Seeded {len(seeded_ids)} demo user profiles into Firestore.",
        "seeded_user_ids": seeded_ids,
    }
