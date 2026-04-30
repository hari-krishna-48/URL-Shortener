"""Load configuration from config.json with environment variable overrides."""

from __future__ import annotations

import json
import os
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"

with open(_CONFIG_PATH, encoding="utf-8") as f:
    _config = json.load(f)

# Environment variables override config.json values (Needed for Docker)
mongodb_port: int = int(os.getenv("MONGODB_PORT", _config["mongodb"]["port"]))
mongodb_host: str = os.getenv("MONGODB_HOST", _config["mongodb"]["host"])
mongodb_database: str = os.getenv("MONGODB_DATABASE", _config["mongodb"]["database"])
mongodb_collections: dict[str, str] = _config["mongodb"]["collections"]
bonus: bool = os.getenv("BONUS", str(_config["bonus"])).lower() in ("true", "1", "yes")

# Instance ID (only in Docker)
instance_id: str | None = os.getenv("INSTANCE_ID") if os.getenv("DOCKER_ENV") == "true" else None
