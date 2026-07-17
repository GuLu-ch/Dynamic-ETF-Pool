"""Command-line entry points for project operations."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Sequence

from etf_pool.config import DEFAULT_CONFIG_PATH, PROJECT_ROOT, Settings, load_config


def _doctor() -> int:
    settings = Settings.from_env()
    checks = {
        "project_root": str(PROJECT_ROOT),
        "config_valid": bool(load_config()),
        "token_configured": bool(settings.tushare_token),
        "provider": settings.data_provider,
        "provider_installed": importlib.util.find_spec(settings.data_provider) is not None,
        "data_dir": str(settings.data_dir),
    }
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0 if checks["config_valid"] and checks["provider_installed"] else 1


def _show_config(path: Path) -> int:
    print(json.dumps(load_config(path), ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="etf-pool", description="Dynamic ETF pool tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="check local configuration without exposing secrets")
    config_parser = subparsers.add_parser("show-config", help="print the effective research config")
    config_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "doctor":
        return _doctor()
    if args.command == "show-config":
        return _show_config(args.config)
    raise AssertionError(f"Unhandled command: {args.command}")
