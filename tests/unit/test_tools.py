# Copyright 2026 Google LLC
import pytest
from app.tools import get_interest_catalogue, validate_interest_score, INTEREST_CATALOGUE

def test_interest_catalogue_length():
    catalogue = get_interest_catalogue()
    assert len(catalogue) >= 15
    assert len(catalogue) <= 20

def test_interest_catalogue_schema():
    catalogue = get_interest_catalogue()
    for item in catalogue:
        assert "id" in item
        assert "name" in item
        assert "description" in item

def test_validate_interest_score():
    assert validate_interest_score(0.85) == 0.85
    assert validate_interest_score(1.5) == 1.0
    assert validate_interest_score(-0.2) == 0.0
