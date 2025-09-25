import os
import pytest

# Set dummy env vars before imports
os.environ.setdefault("GOOGLE_API_KEY", "dummy")
os.environ.setdefault("GOOGLE_CSE_ID", "dummy")
os.environ.setdefault("OPENAI_API_KEY", "dummy")

from classifier import ClaimClassifier

# Dummy inputs
DUMMY_CLAIM = "Snowfalls are now just a thing of the past."
DUMMY_IMAGE = "tests/assets/sample.jpg"


def test_init():
    """Classifier initializes without errors."""
    clf = ClaimClassifier()
    assert clf is not None


def test_classify_output(monkeypatch):
    """Classify returns the expected structure with mocked deps."""

    #Patch retrievers to avoid real API calls
    monkeypatch.setattr("classifier.gpt_web_retrieval", lambda text: [{"title": "Mock"}])
    monkeypatch.setattr("classifier.google_search", lambda text, api_key, cse_id: [{"title": "Mock"}])
    monkeypatch.setattr("classifier.google_reverse_image", lambda image: [{"url": "https://mock.com"}])
    monkeypatch.setattr("classifier.search_fact_check", lambda text, api_key, cse_id: [{"site": "MockFact"}])

    #Patch GPTReasoner
    class FakeReasoner:
        def run(self, text, evidence, image):
            return {"verdict": "ACCURATE", "explanation": "mocked"}

    monkeypatch.setattr("classifier.GPTReasoner", lambda: FakeReasoner())

    clf = ClaimClassifier()
    result = clf.classify((DUMMY_IMAGE, DUMMY_CLAIM))

    #Assertions
    assert isinstance(result, dict)
    assert result["claim"] == DUMMY_CLAIM
    assert "evidence" in result
    assert "verdict" in result
    assert result["verdict"]["verdict"] in {"ACCURATE", "DISINFORMATION"}