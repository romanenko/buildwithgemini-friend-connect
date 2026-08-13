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

"""Tools and catalogue definitions for the Interest Analyzer Agent."""

from typing import Dict, List, Any

# Predefined catalogue of 20 interest areas
INTEREST_CATALOGUE = [
    {
        "id": "outdoors_nature",
        "name": "Outdoors & Nature",
        "description": "Hiking, camping, mountain climbing, outdoor exploration, and nature appreciation.",
    },
    {
        "id": "fitness_exercise",
        "name": "Fitness & Exercise",
        "description": "Gym workouts, running, crossfit, swimming, weightlifting, and physical training.",
    },
    {
        "id": "pickleball_racket_sports",
        "name": "Pickleball & Racket Sports",
        "description": "Pickleball, tennis, badminton, squash, and racquetball.",
    },
    {
        "id": "cars_automotive",
        "name": "Cars & Automotive",
        "description": "Sports cars, auto repair, restoration, racing, mechanics, and car culture.",
    },
    {
        "id": "cooking_culinary",
        "name": "Cooking & Culinary Arts",
        "description": "Home cooking, baking, fine dining, recipe experimentation, mixology, and gastronomy.",
    },
    {
        "id": "technology_gadgets",
        "name": "Technology & Gadgets",
        "description": "Programming, artificial intelligence, smart home gadgets, robotics, and tech innovations.",
    },
    {
        "id": "photography_video",
        "name": "Photography & Videography",
        "description": "Landscape photography, portraiture, video editing, cinematography, and drone filming.",
    },
    {
        "id": "travel_exploration",
        "name": "Travel & Exploration",
        "description": "Backpacking, international travel, road trips, cultural immersion, and sightseeing.",
    },
    {
        "id": "gaming_esports",
        "name": "Gaming & Esports",
        "description": "Video games, PC/console gaming, competitive gaming, game development, and streaming.",
    },
    {
        "id": "music_audio",
        "name": "Music & Audio",
        "description": "Playing instruments, music production, concert going, singing, and audiophile gear.",
    },
    {
        "id": "reading_literature",
        "name": "Reading & Literature",
        "description": "Fiction/non-fiction books, book clubs, creative writing, poetry, and storytelling.",
    },
    {
        "id": "art_design",
        "name": "Art & Design",
        "description": "Painting, drawing, graphic design, sculpting, digital art, and interior design.",
    },
    {
        "id": "gardening_horticulture",
        "name": "Gardening & Horticulture",
        "description": "Indoor plants, vegetable gardening, landscaping, urban farming, and botany.",
    },
    {
        "id": "personal_finance",
        "name": "Personal Finance & Investing",
        "description": "Stock trading, real estate, budgeting, cryptocurrency, and financial independence.",
    },
    {
        "id": "crafting_diy",
        "name": "Crafting & DIY",
        "description": "Woodworking, home improvement, knitting, pottery, 3D printing, and handmade crafts.",
    },
    {
        "id": "fashion_style",
        "name": "Fashion & Style",
        "description": "Streetwear, vintage clothing, fashion design, styling, and apparel trends.",
    },
    {
        "id": "film_cinema",
        "name": "Film & Cinema",
        "description": "Movie watching, film critique, screenwriting, cinema history, and filmmaking.",
    },
    {
        "id": "pets_animal_care",
        "name": "Pets & Animal Care",
        "description": "Dog training, cat care, aquariums, animal welfare, and pet companionship.",
    },
    {
        "id": "board_games_tabletop",
        "name": "Board Games & Tabletop",
        "description": "Strategy board games, Dungeons & Dragons, TCGs, chess, and tabletop gaming.",
    },
    {
        "id": "wellness_mindfulness",
        "name": "Wellness & Mindfulness",
        "description": "Yoga, meditation, mental health, breathwork, nutrition, and holistic health.",
    },
]


def get_interest_catalogue() -> List[Dict[str, str]]:
    """Retrieves the full predefined catalogue of 20 interest areas.

    Returns:
        List of interest categories with their names and descriptions.
    """
    return INTEREST_CATALOGUE


def validate_interest_score(score: float) -> float:
    """Clamps and validates a similarity score between 0.0 and 1.0.

    Args:
        score: Floating point similarity score.

    Returns:
        Validated score clamped to [0.0, 1.0].
    """
    return max(0.0, min(1.0, float(score)))


# Hardcoded Bucket and Project constants
BUCKET_NAME = "friend-connect-media-qwiklabs-gcp-03-75b4c3d63ad8"
PROJECT_ID = "qwiklabs-gcp-03-75b4c3d63ad8"


def generate_kawaii_interest_image(
    interest_topic: str,
    prompt_description: str = "",
    tool_context: Any = None,
) -> str:
    """Generates a funny, heartfelt kawaii illustration for an area of interest using gemini-3.1-flash-lite-image.

    Saves the image as an ADK artifact and uploads it to public Cloud Storage.

    Args:
        interest_topic: Area of interest (e.g., 'Pickleball & Racket Sports', 'Outdoors & Nature').
        prompt_description: Optional additional prompt details or scene description.
        tool_context: ADK ToolContext injected by the runtime.

    Returns:
        Public HTTPS URL string (https://storage.googleapis.com/<bucket>/<object>).
    """
    import uuid
    from google import genai
    from google.genai import types
    from google.cloud import storage

    prompt = (
        f"A funny, heartfelt, cute kawaii-style illustration of two adorable, gender-neutral cute little blob creatures becoming friends over {interest_topic}. "
        f"Portray the characters as soft, round, friendly blob characters (not specifically male or female) with big happy smiling eyes and joyful expressions. "
        f"{prompt_description} Vibrant pastel colors, cute wholesome aesthetic, high quality vector art style."
    )

    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global",
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    image_part = None
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_part = part
                break

    if not image_part or not image_part.inline_data:
        raise ValueError("Failed to generate image from gemini-3.1-flash-lite-image model.")

    image_bytes = image_part.inline_data.data
    mime_type = image_part.inline_data.mime_type or "image/jpeg"
    ext = "jpg" if "jpeg" in mime_type else "png"

    topic_slug = "".join(c if c.isalnum() else "_" for c in interest_topic.lower()).strip("_")
    filename = f"kawaii_{topic_slug}_{uuid.uuid4().hex[:8]}.{ext}"

    # (1) Save with tool_context.save_artifact for Playground Artifacts panel
    if tool_context and hasattr(tool_context, "save_artifact"):
        try:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=filename, artifact=artifact_part)
        except Exception as e:
            pass

    # (2) Upload image bytes to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return public_url
