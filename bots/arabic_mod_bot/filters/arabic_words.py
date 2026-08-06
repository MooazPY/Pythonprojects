"""
Arabic bad-word detection with evasion-proof normalization.

Handles complex obfuscation tactics:
  - Zero-width spaces and hidden unicode control characters
  - Tashkeel / diacritics (َ ً ُ ٌ ِ ٍ ْ ّ ـ)
  - Alef variants (أ إ آ ٱ ٲ ٳ) collapsed to bare alef (ا)
  - Taa marbuta / haa and alef maksura / yaa normalization
  - Tatweel/kashida stretching
  - Separators smuggled between letters (spaces, dots, underscores, hyphens)
  - Repeated character spam (كككللللب -> كلب)
  - Arabizi / number substitutions (5 -> خ, 3 -> ع, 7 -> ح, 9 -> ق)
"""

from __future__ import annotations

import re
import unicodedata
from typing import List, Pattern

from utils.data_loader import load_bad_words

# Arabic diacritics (tashkeel) + tatweel, stripped entirely.
_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670\u06D6-\u06ED\u0640]")

# Zero-width & invisible unicode characters used for filter bypass.
_INVISIBLE_CHARS_RE = re.compile(r"[\u200B-\u200D\uFEFF\u2060\u200E\u200F]")

# Non-letter separators inserted between letters.
_SEPARATOR_RE = re.compile(r"[\s\.\-_\*\/\+\=,\u200b\u200c\u200d\u2060]+")

# Collapse 3+ repeats of the same character down to 1.
_REPEAT_RE = re.compile(r"(.)\1{2,}")

_LETTER_NORMALIZATION = {
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ٲ": "ا", "ٳ": "ا",
    "ة": "ه",
    "ى": "ي", "ئ": "ي",
    "ؤ": "و",
}

# Arabizi / number substitutions in Arabic gaming/chat slang.
_LEET_NORMALIZATION = {
    "5": "خ",
    "3": "ع",
    "7": "ح",
    "9": "ق",
    "8": "غ",
    "2": "ا",
}


def normalize_arabic(text: str) -> str:
    """Normalizes Arabic text to neutralize evasion by obfuscation."""
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = _INVISIBLE_CHARS_RE.sub("", text)
    text = _DIACRITICS_RE.sub("", text)

    for src, dst in _LETTER_NORMALIZATION.items():
        text = text.replace(src, dst)
    for src, dst in _LEET_NORMALIZATION.items():
        text = text.replace(src, dst)

    text = _REPEAT_RE.sub(r"\1", text)
    return text


def _build_spaced_pattern(word: str) -> Pattern:
    """Builds regex that matches word even with separators inserted between letters."""
    escaped_letters = [re.escape(ch) for ch in word]
    pattern = _SEPARATOR_RE.pattern.join(f"(?:{ch})" for ch in escaped_letters)
    return re.compile(pattern, re.IGNORECASE)


class ArabicWordFilter:
    def __init__(self, base_words: List[str], custom_words: List[str] | None = None):
        self._base_words = list(dict.fromkeys(base_words))
        self._custom_words = list(dict.fromkeys(custom_words or []))
        self._rebuild()

    def _rebuild(self) -> None:
        all_words = self._base_words + self._custom_words
        normalized_words = sorted(
            {normalize_arabic(w) for w in all_words if w.strip()},
            key=len,
            reverse=True,
        )
        self._patterns = {w: _build_spaced_pattern(w) for w in normalized_words}

    def set_custom_words(self, custom_words: List[str]) -> None:
        self._custom_words = list(dict.fromkeys(custom_words))
        self._rebuild()

    def check(self, text: str) -> List[str]:
        """Returns list of matched banned words in `text`."""
        if not text:
            return []

        normalized = normalize_arabic(text)
        stripped = _SEPARATOR_RE.sub("", normalized)

        matches = []
        for word, pattern in self._patterns.items():
            if word in stripped or pattern.search(normalized):
                matches.append(word)
        return matches

    def contains_violation(self, text: str) -> bool:
        return bool(self.check(text))


_FALLBACK_BAD_WORDS: List[str] = [
    "كلب",
    "حمار",
    "غبي",
    "خنزير",
    "عرص",
    "قحبة",
    "كسمك",
    "منيك",
    "شرموطة",
    "زبي",
]

DEFAULT_BAD_WORDS: List[str] = load_bad_words(_FALLBACK_BAD_WORDS)
