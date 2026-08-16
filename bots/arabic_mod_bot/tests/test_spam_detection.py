"""Unit tests for spam / flood detection."""

from filters.spam_detection import SpamTracker


def test_message_flood_triggers():
    tracker = SpamTracker()
    guild_id, user_id = 1, 100
    for i in range(5):
        result = tracker.check(
            guild_id, user_id, f"msg {i}", max_messages=4, window_seconds=10
        )
    assert result.is_spam
    assert result.reason == "message_flood"


def test_duplicate_spam_triggers():
    tracker = SpamTracker()
    guild_id, user_id = 2, 200
    for _ in range(3):
        result = tracker.check(
            guild_id, user_id, "same text", max_messages=20, window_seconds=10
        )
    assert result.is_spam
    assert result.reason == "duplicate_spam"


def test_normal_messages_pass():
    tracker = SpamTracker()
    result = tracker.check(3, 300, "hello", max_messages=5, window_seconds=10)
    assert not result.is_spam


def test_cleanup_stale_history():
    import time
    tracker = SpamTracker()
    tracker.check(4, 400, "stale msg", max_messages=10, window_seconds=10)
    assert len(tracker._history) == 1

    time.sleep(0.02)
    cleaned = tracker.cleanup_stale_history(max_age_seconds=0.01)
    assert cleaned == 1
    assert len(tracker._history) == 0

