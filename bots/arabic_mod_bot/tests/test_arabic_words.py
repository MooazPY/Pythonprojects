"""Unit tests for Arabic normalization and profanity filter."""

from filters.arabic_words import ArabicWordFilter, normalize_arabic


def test_normalize_strips_diacritics():
    assert normalize_arabic("كَلب") == normalize_arabic("كلب")


def test_normalize_alef_variants():
    assert normalize_arabic("أحmaq") == normalize_arabic("احmaq".replace("mq", "مق"))


def test_normalize_repeated_letters():
    assert normalize_arabic("كلللب") == normalize_arabic("كلب")


def test_normalize_leet_speak():
    assert "خ" in normalize_arabic("5")


def test_filter_detects_plain_word():
    f = ArabicWordFilter(["كلب"], [])
    assert f.contains_violation("انت كلب")


def test_filter_detects_spaced_evasion():
    f = ArabicWordFilter(["كلب"], [])
    assert f.contains_violation("ك ل ب")


def test_filter_detects_custom_word():
    f = ArabicWordFilter([], ["كلمةاختبار"])
    assert f.contains_violation("هذه كلمةاختبار")


def test_filter_ignores_clean_text():
    f = ArabicWordFilter(["كلب"], [])
    assert not f.contains_violation("مرحبا بالجميع")
