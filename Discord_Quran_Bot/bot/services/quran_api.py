import logging
import random
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


class QuranApiError(Exception):
    """Raised when the Quran API call fails."""


EDITION_ALIASES = {
    "en": "en.sahih",
    "fr": "fr.hamidullah",
    "ur": "ur.ahmedali",
    "tr": "tr.vakfi",
    "id": "id.indonesian",
    "de": "de.bubenheim",
    "es": "es.cortes",
    "ru": "ru.kuliev",
    "bn": "bn.bengali",
    "ar": "ar",
}

EDITION_LABELS = {
    "en.sahih": "Sahih International",
    "fr.hamidullah": "Hamidullah (French)",
    "ur.ahmedali": "Ahmed Ali (Urdu)",
    "tr.vakfi": "Diyanet (Turkish)",
    "id.indonesian": "Indonesian",
    "de.bubenheim": "Bubenheim (German)",
    "es.cortes": "Cortes (Spanish)",
    "ru.kuliev": "Kuliev (Russian)",
    "bn.bengali": "Bengali",
    "ar": "Arabic",
}

RECITER_ALIASES = {
    "alafasy": "ar.alafasy",
    "husary": "ar.husary",
    "minshawi": "ar.minshawi",
    "sudais": "ar.abdurrahmaansudais",
}


class QuranService:
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self._session = session
        self._surah_info_cache: dict[int, dict] = {}

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_random_ayah(self, translation: str = "en") -> dict:
        try:
            session = await self._get_session()
            async with session.get("https://api.alquran.cloud/v1/surah") as response:
                response.raise_for_status()
                payload = await response.json()
                surahs = payload.get("data", [])
                if not surahs:
                    raise QuranApiError("No Quran chapters were returned from the API.")
                surah = random.choice(surahs)
                ayah_num = random.randint(1, surah.get("numberOfAyahs", 1))
                return await self.get_ayah(surah["number"], ayah_num, translation=translation)
        except Exception as exc:  # pragma: no cover - network path
            logger.warning("Failed to fetch Quran data via alquran.cloud: %s", exc)
            raise QuranApiError("Unable to reach the Quran API right now.") from exc

    async def get_ayah(self, surah: int, ayah: int, translation: str = "en") -> dict:
        try:
            session = await self._get_session()
            url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/{translation}"
            async with session.get(url) as response:
                response.raise_for_status()
                payload = await response.json()
                return payload["data"]
        except Exception as exc:  # pragma: no cover - network path
            logger.warning("Failed to fetch ayah %s:%s: %s", surah, ayah, exc)
            raise QuranApiError("Unable to reach the Quran API right now.") from exc

    async def get_surah_info(self, surah: int) -> dict:
        if surah in self._surah_info_cache:
            return self._surah_info_cache[surah]

        try:
            session = await self._get_session()
            url = f"https://api.alquran.cloud/v1/surah/{surah}"
            async with session.get(url) as response:
                response.raise_for_status()
                payload = await response.json()
                surah_data = payload["data"]
                self._surah_info_cache[surah] = surah_data
                return surah_data
        except Exception as exc:  # pragma: no cover - network path
            logger.warning("Failed to fetch surah info %s: %s", surah, exc)
            raise QuranApiError("Unable to fetch surah information right now.") from exc

    def resolve_edition(self, language: str) -> str:
        language = language.strip()
        if "." in language:
            return language
        return EDITION_ALIASES.get(language.lower(), language)

    def edition_label(self, language: str) -> str:
        edition = self.resolve_edition(language)
        return EDITION_LABELS.get(edition, edition)

    async def get_recitation_url(self, surah: int, ayah: int, reciter: str = "alafasy") -> str | None:
        edition = RECITER_ALIASES.get(reciter.lower(), reciter)
        try:
            session = await self._get_session()
            url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/{edition}"
            async with session.get(url) as response:
                response.raise_for_status()
                payload = await response.json()
                return payload.get("data", {}).get("audio")
        except Exception as exc:
            logger.warning("Recitation lookup failed for %s:%s (%s): %s", surah, ayah, reciter, exc)
            return None

    async def get_translation(self, surah: int, ayah: int, language: str = "en") -> Optional[dict]:
        edition = self.resolve_edition(language)
        try:
            session = await self._get_session()
            url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/{edition}"
            async with session.get(url) as response:
                response.raise_for_status()
                payload = await response.json()
                return payload.get("data")
        except Exception as exc:  # pragma: no cover - network path
            logger.warning("Translation lookup failed for %s:%s in %s: %s", surah, ayah, language, exc)
            return None
