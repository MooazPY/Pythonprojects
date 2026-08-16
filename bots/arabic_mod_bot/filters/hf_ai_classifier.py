"""
Hugging Face AI Arabic Toxicity & Hate Speech Classifier.

Integrates hosted NLP inference models for Arabic language moderation.
Provides non-blocking async network calls with zero-lag fallback to local filters.
"""

from __future__ import annotations

import logging
import os
import asyncio
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

import aiohttp

logger = logging.getLogger("arabic_mod_bot.filters.hf_ai_classifier")

# Dedicated Toxicity & Hate Speech NLP model (Configurable via HF_MODEL_NAME env var)
DEFAULT_HF_MODEL = os.environ.get(
    "HF_MODEL_NAME", "unitary/toxic-bert"
)
FALLBACK_HF_MODELS = [
    "unitary/toxic-bert",
    "facebook/roberta-hate-speech-dynabench-r4-target",
    "cardiffnlp/twitter-roberta-base-hate",
]
HF_API_URL_TEMPLATE = "https://router.huggingface.co/hf-inference/models/{model}"

CLEAN_LABELS = {
    "non_hate", "non-hate", "not_hate", "no_hate", "non_toxic", "non-toxic",
    "not_toxic", "no_toxic", "clean", "normal", "positive", "neutral", "label_0", "nothate"
}

TOXIC_LABELS = {
    "hate", "hate speech", "hate_speech", "hatespeech", "offensive", "sexism",
    "racism", "religious discrimination", "toxic", "profanity", "abusive",
    "cyberbullying", "hostile", "label_1", "label_toxic", "label_hate", "negative"
}


def is_label_toxic(lbl: str) -> bool:
    lbl_clean = lbl.strip().lower()
    if lbl_clean in CLEAN_LABELS or any(c_lbl in lbl_clean for c_lbl in ["non_hate", "non-hate", "not_hate", "no_hate", "non_toxic", "non-toxic", "nothate"]):
        return False
    if lbl_clean in TOXIC_LABELS:
        return True
    return any(t_lbl in lbl_clean for t_lbl in ["toxic", "abusive", "cyberbullying", "profanity", "hostile"])


@dataclass
class AIToxicityResult:
    is_toxic: bool
    confidence: float
    label: str
    model_used: str
    toxic_score: float = 0.0
    error: Optional[str] = None


class HuggingFaceClassifier:
    """Async Hugging Face Inference API client specialized for content moderation with automatic fallback."""

    def __init__(self, api_token: Optional[str] = None, model: Optional[str] = None):
        self.api_token = api_token or os.environ.get("HUGGINGFACE_TOKEN", "")
        self.model = model or os.environ.get("HF_MODEL_NAME", DEFAULT_HF_MODEL)

    @property
    def api_url(self) -> str:
        return HF_API_URL_TEMPLATE.format(model=self.model)

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        token = self.api_token or os.environ.get("HUGGINGFACE_TOKEN", "")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def _send_request(
        self, model_name: str, payload: dict, timeout_seconds: float
    ) -> tuple[int, Any, Optional[str]]:
        url = HF_API_URL_TEMPLATE.format(model=model_name)
        try:
            timeout = aiohttp.ClientTimeout(total=timeout_seconds)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    url, headers=self._get_headers(), json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return 200, data, None
                    body_text = await response.text()
                    return response.status, None, body_text
        except Exception as e:
            return 0, None, str(e)

    async def _query_hf_api(
        self, text: str, confidence_threshold: float, timeout_seconds: float
    ) -> AIToxicityResult:
        cleaned_text = text.strip()
        if not cleaned_text or len(cleaned_text) < 2:
            return AIToxicityResult(
                is_toxic=False, confidence=0.0, label="clean", model_used=self.model, toxic_score=0.0
            )

        payload = {"inputs": cleaned_text}
        models_to_try = [self.model] + [m for m in FALLBACK_HF_MODELS if m != self.model]

        for current_model in models_to_try:
            status, data, err_text = await self._send_request(
                current_model, payload, timeout_seconds
            )
            if status == 200 and data is not None:
                self.model = current_model  # update active model
                return self._parse_hf_response(data, confidence_threshold, current_model)

            if status == 401:
                err_msg = "Hugging Face token missing or invalid (HTTP 401)"
                logger.warning("Hugging Face AI classifier bypass: %s", err_msg)
                return AIToxicityResult(
                    is_toxic=False,
                    confidence=0.0,
                    label="no_token",
                    model_used=current_model,
                    toxic_score=0.0,
                    error=err_msg,
                )

            # If 400/410 (model unsupported/deprecated), continue to try next fallback model
            if status in (400, 410):
                logger.warning("Model %s returned HTTP %s (%s). Trying fallback...", current_model, status, err_text)
                continue

            # Other error or connection failure
            err_msg = err_text or f"HF API returned status {status}"
            logger.warning("Hugging Face AI classifier bypass on %s: %s", current_model, err_msg)

        return AIToxicityResult(
            is_toxic=False,
            confidence=0.0,
            label="error_fallback",
            model_used=self.model,
            toxic_score=0.0,
            error=f"HF API status {status}" if 'status' in locals() else "Service unavailable",
        )

    async def classify_text(
        self, text: str, confidence_threshold: float = 0.80, timeout_seconds: float = 4.5
    ) -> AIToxicityResult:
        """
        Classifies Arabic text for toxicity using Hugging Face API.
        Evaluates both raw text and evasion-normalized text concurrently to prevent bypass tactics.
        """
        cleaned_text = text.strip()
        from filters.arabic_words import normalize_arabic
        normalized = normalize_arabic(text)

        res = await self._query_hf_api(cleaned_text, confidence_threshold, timeout_seconds)
        if normalized != cleaned_text and len(normalized) >= 2 and not res.is_toxic:
            norm_res = await self._query_hf_api(normalized, confidence_threshold, timeout_seconds)
            if norm_res.is_toxic or norm_res.toxic_score > res.toxic_score:
                res = norm_res

        # If dictionary filter matches explicit bad words (raw or normalized text), force result to toxic/hate
        from utils.data_loader import load_bad_words
        from filters.arabic_words import ArabicWordFilter, DEFAULT_BAD_WORDS
        word_filter = ArabicWordFilter(load_bad_words(DEFAULT_BAD_WORDS))
        hits = word_filter.check(text) or word_filter.check(normalized)
        if hits:
            return AIToxicityResult(
                is_toxic=True,
                confidence=0.99,
                label=f"HATE / BAD_WORD ({hits[0]})",
                model_used=res.model_used,
                toxic_score=0.99,
            )

        return res

    def _parse_hf_response(
        self, data: Any, confidence_threshold: float, model_used: Optional[str] = None
    ) -> AIToxicityResult:
        """Parses Hugging Face classification output matrix."""
        active_model = model_used or self.model
        try:
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
                toxic_score = 0.0

                for item in scores:
                    if isinstance(item, dict) and "score" in item:
                        score = float(item.get("score", 0.0))
                        lbl = str(item.get("label", "")).strip().lower()

                        if is_label_toxic(lbl):
                            if score > toxic_score:
                                toxic_score = score

                        if score > max_score:
                            max_score = score
                            best_match = lbl

                if best_match and is_label_toxic(best_match) and max_score >= confidence_threshold:
                    return AIToxicityResult(
                        is_toxic=True,
                        confidence=max_score,
                        label=best_match.upper(),
                        model_used=active_model,
                        toxic_score=max_score,
                    )

                clean_lbl = "NORMAL" if is_label_toxic(best_match or "") else (best_match.upper() if best_match else "NORMAL")
                clean_conf = (1.0 - toxic_score) if toxic_score > 0 else 0.99
                return AIToxicityResult(
                    is_toxic=False,
                    confidence=clean_conf,
                    label=clean_lbl,
                    model_used=active_model,
                    toxic_score=toxic_score,
                )

        except Exception as e:
            logger.error("Failed to parse Hugging Face response data: %s", e)

        return AIToxicityResult(
            is_toxic=False, confidence=0.0, label="NORMAL", model_used=active_model, toxic_score=0.0
        )
