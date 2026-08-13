#!/usr/bin/env python3
"""Seed script for FriendConnect Firestore database."""

import datetime
from google.cloud import firestore

# CRITICAL: Hardcode the project ID as a literal string to avoid Agent Platform
# runtime project number issues.
PROJECT_ID = "qwiklabs-gcp-03-75b4c3d63ad8"
COLLECTION_NAME = "user_profiles"

SEEDED_PROFILES = [
    {
        "user_id": "alex_m",
        "name": "Alex Morgan",
        "bio": "Weekend pickleball enthusiast, mountain hiker, and specialty coffee brewer.",
        "interests": ["Pickleball & Racket Sports", "Outdoors & Nature", "Coffee & Tea Culture"],
        "status": "looking_for_friends",
        "location": "San Francisco, CA",
        "vibe_notes": "Energetic, outgoing, always down for a morning trail run or court game.",
        "contact_link": "https://connect.friendconnect.app/u/alex_m",
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "user_id": "sam_k",
        "name": "Sam Kim",
        "bio": "Passionate home baker and sourdough experimenter. Loves hosting weekend dinner parties.",
        "interests": ["Cooking & Culinary", "Baking & Desserts", "Board Games & Tabletop"],
        "status": "looking_for_friends",
        "location": "Oakland, CA",
        "vibe_notes": "Warm, creative host who brings artisanal bread and strategic board games.",
        "contact_link": "https://connect.friendconnect.app/u/sam_k",
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "user_id": "jordan_t",
        "name": "Jordan Taylor",
        "bio": "Avid mountain climber and landscape photographer exploring Sierra trails.",
        "interests": ["Outdoors & Nature", "Fitness & Exercise", "Photography & Visual Arts"],
        "status": "looking_for_friends",
        "location": "San Jose, CA",
        "vibe_notes": "Adventurous, thoughtful, loves sunrise hikes and capturing scenic trail photos.",
        "contact_link": "https://connect.friendconnect.app/u/jordan_t",
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "user_id": "taylor_r",
        "name": "Taylor Reed",
        "bio": "Car restoring weekend mechanic, woodworking enthusiast, and fitness buff.",
        "interests": ["Cars & Automotive", "DIY & Woodworking", "Fitness & Exercise"],
        "status": "looking_for_friends",
        "location": "Berkeley, CA",
        "vibe_notes": "Hands-on problem solver who loves garage projects and gym sessions.",
        "contact_link": "https://connect.friendconnect.app/u/taylor_r",
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "user_id": "casey_l",
        "name": "Casey Lee",
        "bio": "Indie game dev, tabletop campaign master, and sci-fi book worm.",
        "interests": ["Gaming & Esports", "Sci-Fi & Fantasy", "Board Games & Tabletop"],
        "status": "looking_for_friends",
        "location": "San Francisco, CA",
        "vibe_notes": "Witty, imaginative story-teller who loves co-op gaming and world building.",
        "contact_link": "https://connect.friendconnect.app/u/casey_l",
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
]


def seed_database():
    """Seeds the user_profiles collection in Firestore."""
    db = firestore.Client(project=PROJECT_ID)
    print(f"Connecting to Firestore for project: {PROJECT_ID}")

    collection_ref = db.collection(COLLECTION_NAME)
    for profile in SEEDED_PROFILES:
        doc_ref = collection_ref.document(profile["user_id"])
        doc_ref.set(profile)
        print(f"Seeded profile for {profile['name']} ({profile['user_id']})")

    print(f"Successfully seeded {len(SEEDED_PROFILES)} items into '{COLLECTION_NAME}'!")


if __name__ == "__main__":
    seed_database()
