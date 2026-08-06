"""Unit tests for Hugging Face AI classifier."""

import asyncio
import pytest
from filters.hf_ai_classifier import HuggingFaceClassifier, AIToxicityResult


def test_offline_fallback():
    async def _run():
        classifier = HuggingFaceClassifier(api_token="invalid_token")
        result = await classifier.classify_text("مرحباً بك في السيرفر", timeout_seconds=0.1)
        assert isinstance(result, AIToxicityResult)
        assert result.is_toxic is False
        assert result.model_used == "aubmindlab/bert-base-arabertv02"

    asyncio.run(_run())


def test_parse_hf_response():
    classifier = HuggingFaceClassifier()

    # Mock toxic response from HF model
    toxic_data = [[{"label": "TOXIC", "score": 0.94}, {"label": "CLEAN", "score": 0.06}]]
    res = classifier._parse_hf_response(toxic_data, confidence_threshold=0.80)
    assert res.is_toxic is True
    assert res.confidence == 0.94

    # Mock clean response
    clean_data = [[{"label": "CLEAN", "score": 0.99}, {"label": "TOXIC", "score": 0.01}]]
    res = classifier._parse_hf_response(clean_data, confidence_threshold=0.80)
    assert res.is_toxic is False
