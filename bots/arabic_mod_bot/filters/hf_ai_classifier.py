"""
Hugging Face AI Arabic Toxicity & Hate Speech Classifier.

Integrates hosted NLP inference models for Arabic language moderation.
Provides non-blocking async network calls with zero-lag fallback to local filters.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

import aiohttp

logger = logging.getLogger("arabic_mod_bot.filters.hf_ai_classifier")

# Default high-performance Arabic NLP model for toxicity and sentiment/hate classification
DEFAULT_HF_MODEL = "aubmindlab/bert-base-arabertv02"
HF_API_URL_TEMPLATE = "https://api-inference.huggingface.co/models/{model}"

TOXIC_LABELS = {
    "toxic", "hate", "profanity", "abusive", "offensive", "insult",
    "LABEL_1", "LABEL_TOXIC", "LABEL_HATE", "NEGATIVE"
}


@dataclass
class AIToxicityResult:
    is_toxic: bool
    confidence: float
    label: str
    model_used: str
    error: Optional[str] = None


class HuggingFaceClassifier:
    """Async Hugging Face Inference API client specialized for Arabic content moderation."""

    def __init__(self, api_token: Optional[str] = None, model: str = DEFAULT_HF_MODEL):
        self.api_token = api_token or os.environ.get("HUGGINGFACE_TOKEN", "")
        self.model = model
        self.api_url = HF_API_URL_TEMPLATE.format(model=self.model)

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    async def classify_text(
        self, text: str, confidence_threshold: float = 0.80, timeout_seconds: float = 2.5
    ) -> AIToxicityResult:
        """
        Classifies Arabic text for toxicity using Hugging Face API.
        Returns AIToxicityResult with fallback handling if offline or rate-limited.
        """
        cleaned_text = text.strip()
        if not cleaned_text or len(cleaned_text) < 2:
            return AIToxicityResult(
                is_toxic=False, confidence=0.0, label="clean", model_used=self.model
            )

        payload = {"inputs": cleaned_text}

        try:
            timeout = aiohttp.ClientTimeout(total=timeout_seconds)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.api_url, headers=self._get_headers(), json=payload
                ) as response:
                    if response.status != 200:
                        err_msg = f"HF API returned status {response.status}"
                        logger.warning("Hugging Face AI classifier bypass: %s", err_msg)
                        return AIToxicityResult(
                            is_toxic=False,
                            confidence=0.0,
                            label="error_fallback",
                            model_used=self.model,
                            error=err_msg,
                        )

                    data = await response.json()
                    return self._parse_hf_response(data, confidence_threshold)

        except Exception as e:
            logger.debug("Hugging Face API unavailable or timed out: %s", e)
            return AIToxicityResult(
                is_toxic=False,
                confidence=0.0,
                label="offline_fallback",
                model_used=self.model,
                error=str(e),
            )

    def _parse_hf_response(
        self, data: Any, confidence_threshold: float
    ) -> AIToxicityResult:
        """Parses Hugging Face classification output matrix."""
        try:
            # Output can be [[{'label': 'LABEL_1', 'score': 0.95}, ...]]
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                if isinstance(first_item, list) and len(first_item) > 0:
                    scores = first_item
                elif isinstance(first_item, dict):
                    scores = data
                else:
                    scores = []

                best_match = None
                max_score = 0.0

                for item in scores:
                    if isinstance(item, dict) and "score" in item:
                        score = float(item.get("score", 0.0))
                        lbl = str(item.get("label", "")).lower()

                        if score > max_score:
                            max_score = score
                            best_match = lbl

                if best_match and max_score >= confidence_threshold:
                    if any(t_lbl in best_match for t_lbl in TOXIC_LABELS):
                        return AIToxicityResult(
                            is_toxic=True,
                            confidence=max_score,
                            label=best_match,
                            model_used=self.model,
                        )

                return AIToxicityResult(
                    is_toxic=False,
                    confidence=max_score,
                    label=best_match or "clean",
                    model_used=self.model,
                )

        except Exception as e:
            logger.error("Failed to parse Hugging Face response data: %s", e)

        return AIToxicityResult(
            is_toxic=False, confidence=0.0, label="clean", model_used=self.model
        )
