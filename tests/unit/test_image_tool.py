"""Unit tests for the gemini-3.1-flash-lite-image generation tool."""

from unittest.mock import MagicMock
from app.tools import generate_kawaii_interest_image, BUCKET_NAME


def test_generate_kawaii_interest_image():
    """Verify image tool generates image with gemini-3.1-flash-lite-image and returns public GCS URL."""
    mock_context = MagicMock()
    mock_context.save_artifact = MagicMock()

    url = generate_kawaii_interest_image(
        interest_topic="Pickleball & Racket Sports",
        prompt_description="Two cute panda friends playing pickleball with happy faces",
        tool_context=mock_context,
    )

    assert isinstance(url, str)
    assert url.startswith(f"https://storage.googleapis.com/{BUCKET_NAME}/")
    assert "kawaii_pickleball" in url

    # Verify save_artifact was invoked
    assert mock_context.save_artifact.called
