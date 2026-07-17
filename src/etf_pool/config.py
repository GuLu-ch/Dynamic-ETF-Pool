"""Project paths and runtime configuration."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "default.json"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load the versioned JSON research configuration."""
    configured_path = path or os.getenv("ETF_POOL_CONFIG") or DEFAULT_CONFIG_PATH
    config_path = Path(configured_path)
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path
    with config_path.open(encoding="utf-8") as stream:
        config = json.load(stream)
    if not isinstance(config, dict):
        raise ValueError(f"Configuration root must be an object: {config_path}")
    return config


def _dotenv_values(path: Path) -> dict[str, str]:
    """Read the simple KEY=VALUE form used by this project's .env file."""
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if separator:
            values[key.strip()] = value.strip().strip("'\"")
    return values


@dataclass(frozen=True)
class Settings:
    """Secrets and machine-specific settings, kept outside version control."""

    tushare_token: str | None
    data_provider: str
    data_dir: Path

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> Settings:
        values = _dotenv_values(env_file or PROJECT_ROOT / ".env")
        token = os.getenv("TUSHARE_TOKEN") or values.get("TUSHARE_TOKEN")
        provider = os.getenv("ETF_DATA_PROVIDER") or values.get("ETF_DATA_PROVIDER", "tushare")
        data_dir_value = os.getenv("ETF_POOL_DATA_DIR") or values.get("ETF_POOL_DATA_DIR", "data")
        data_dir = Path(data_dir_value)
        if not data_dir.is_absolute():
            data_dir = PROJECT_ROOT / data_dir
        return cls(
            tushare_token=token.strip() if token else None,
            data_provider=provider.strip().lower(),
            data_dir=data_dir,
        )

    def require_token(self) -> str:
        if not self.tushare_token:
            raise RuntimeError("TUSHARE_TOKEN is not configured; see .env.example")
        return self.tushare_token
