"""Unit tests for TTLCacheStore and i18n translation resolver."""

import time
from config.cache_store import TTLCacheStore
from utils.i18n import t


def test_ttl_cache_set_get_and_expiration():
    cache = TTLCacheStore(default_ttl_seconds=1, max_size=5)
    cache.set("k1", "v1")

    assert cache.get("k1") == "v1"
    assert cache.hits == 1

    time.sleep(1.1)
    assert cache.get("k1") is None
    assert cache.misses == 1


def test_ttl_cache_eviction():
    cache = TTLCacheStore(default_ttl_seconds=300, max_size=2)
    cache.set("k1", "v1")
    cache.set("k2", "v2")
    cache.set("k3", "v3")  # Evicts k1

    assert cache.get("k1") is None
    assert cache.get("k2") == "v2"
    assert cache.get("k3") == "v3"


def test_i18n_translation_resolver():
    ar_msg = t("permission_error", lang="ar")
    assert "ليس لديك الصلاحية" in ar_msg

    en_msg = t("permission_error", lang="en")
    assert "You do not have sufficient permissions" in en_msg

    tmpl_ar = t("role_error", lang="ar", role="Moderator")
    assert "Moderator" in tmpl_ar

