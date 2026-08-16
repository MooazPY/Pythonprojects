"""Unit tests for Hugging Face AI classifier."""

import asyncio
from filters.hf_ai_classifier import HuggingFaceClassifier, AIToxicityResult


def test_offline_fallback():
    async def _run():
        classifier = HuggingFaceClassifier(api_token="invalid_token")
        result = await classifier.classify_text("مرحباً بك في السيرفر", timeout_seconds=0.01)
        assert isinstance(result, AIToxicityResult)
        assert result.is_toxic is False
        assert result.model_used == classifier.model

    asyncio.run(_run())


def test_parse_hf_response():
    classifier = HuggingFaceClassifier()

    # Mock toxic / negative response from sentiment model
    toxic_data = [[{"label": "negative", "score": 0.94}, {"label": "positive", "score": 0.06}]]
    res = classifier._parse_hf_response(toxic_data, confidence_threshold=0.80)
    assert res.is_toxic is True
    assert res.confidence == 0.94
    assert res.toxic_score == 0.94
    assert "NEGATIVE" in res.label

    # Mock clean / positive response
    clean_data = [[{"label": "positive", "score": 0.99}, {"label": "negative", "score": 0.01}]]
    res = classifier._parse_hf_response(clean_data, confidence_threshold=0.80)
    assert res.is_toxic is False
    assert res.toxic_score == 0.01
    assert res.label == "POSITIVE"


def test_parse_hate_speech_response():
    classifier = HuggingFaceClassifier(model="Hate-speech-CNERG/dehatebert-mono-arabic")
    hate_data = [[{"label": "HATE", "score": 0.96}, {"label": "NON_HATE", "score": 0.04}]]
    res = classifier._parse_hf_response(hate_data, confidence_threshold=0.80)
    assert res.is_toxic is True
    assert res.confidence == 0.96
    assert "HATE" in res.label

def test_parse_non_hate_clean_text():
    classifier = HuggingFaceClassifier(model="Hate-speech-CNERG/dehatebert-mono-arabic")
    non_hate_data = [[{"label": "NON_HATE", "score": 0.95}, {"label": "HATE", "score": 0.05}]]
    res = classifier._parse_hf_response(non_hate_data, confidence_threshold=0.80)
    assert res.is_toxic is False
    assert res.label == "NON_HATE"
    assert res.confidence == 0.95
    assert res.toxic_score == 0.05


def test_hf_model_name_env_var():
    import os
    os.environ["HF_MODEL_NAME"] = "Hate-speech-CNERG/dehatebert-mono-arabic"
    classifier = HuggingFaceClassifier()
    assert classifier.model == "Hate-speech-CNERG/dehatebert-mono-arabic"
    assert "Hate-speech-CNERG/dehatebert-mono-arabic" in classifier.api_url



