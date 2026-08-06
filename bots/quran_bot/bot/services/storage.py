import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional


class GuildSettingsStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or os.path.join(os.getcwd(), "guild_settings.sqlite3"))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._initialize_db()

    def _initialize_db(self) -> None:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS command_stats (
                guild_id TEXT NOT NULL,
                command TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (guild_id, command)
            )
            """
        )
        self._conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None  # type: ignore[assignment]

    def __enter__(self) -> "GuildSettingsStore":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def get_guild_settings(self, guild_id: str) -> Dict[str, Any]:
        if guild_id is None:
            guild_id = "global"
        cursor = self._conn.execute(
            "SELECT data FROM guild_settings WHERE guild_id = ?",
            (guild_id,),
        )
        row = cursor.fetchone()
        if not row:
            return {}
        return json.loads(row["data"])

    def save_guild_settings(self, guild_id: str, settings: Dict[str, Any]) -> None:
        if guild_id is None:
            guild_id = "global"
        data = json.dumps(settings)
        self._conn.execute(
            "INSERT INTO guild_settings (guild_id, data) VALUES (?, ?) "
            "ON CONFLICT(guild_id) DO UPDATE SET data = excluded.data",
            (guild_id, data),
        )
        self._conn.commit()

    def increment_command_count(self, guild_id: Optional[str], command: str) -> None:
        if guild_id is None:
            guild_id = "global"
        self._conn.execute(
            "INSERT INTO command_stats (guild_id, command, count) VALUES (?, ?, 1) "
            "ON CONFLICT(guild_id, command) DO UPDATE SET count = count + 1",
            (guild_id, command),
        )
        self._conn.commit()

    def get_command_stats(self, guild_id: Optional[str]) -> Dict[str, int]:
        if guild_id is None:
            guild_id = "global"
        cursor = self._conn.execute(
            "SELECT command, count FROM command_stats WHERE guild_id = ?",
            (guild_id,),
        )
        return {row["command"]: row["count"] for row in cursor.fetchall()}
