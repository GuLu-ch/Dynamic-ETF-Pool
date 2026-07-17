"""项目命令行入口。"""

import argparse
import importlib.util
import json
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from etf_pool.config import (
    CLASSIFICATION_CONFIG_PATH,
    DEFAULT_CONFIG_PATH,
    PROJECT_ROOT,
    SECONDARY_CLASSIFICATION_CONFIG_PATH,
    Settings,
    load_classification_config,
    load_config,
    load_secondary_classification_config,
)
from etf_pool.data.provider import TushareETFProvider
from etf_pool.data.sync import (
    classify_etf_snapshot,
    classify_secondary_snapshot,
    sync_and_classify_etfs,
)


def _doctor():
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


def _show_config(path: Path):
    print(json.dumps(load_config(path), ensure_ascii=False, indent=2))
    return 0


def _sync_classify(as_of_date: str, classification_config_path: Path):
    settings = Settings.from_env()
    provider = TushareETFProvider.from_settings(settings)
    classification_config = load_classification_config(classification_config_path)
    summary = sync_and_classify_etfs(
        provider=provider,
        data_dir=settings.data_dir,
        source=settings.data_provider,
        classification_config=classification_config,
        as_of_date=as_of_date,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _classify_snapshot(as_of_date: str, classification_config_path: Path):
    settings = Settings.from_env()
    classification_config = load_classification_config(classification_config_path)
    summary = classify_etf_snapshot(
        data_dir=settings.data_dir,
        source=settings.data_provider,
        classification_config=classification_config,
        as_of_date=as_of_date,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _classify_secondary(
    as_of_date: str,
    primary_version: str | None,
    classification_config_path: Path,
    secondary_config_path: Path,
):
    settings = Settings.from_env()
    classification_config = load_classification_config(classification_config_path)
    secondary_config = load_secondary_classification_config(secondary_config_path)
    selected_primary_version = primary_version or str(classification_config["version"])
    summary = classify_secondary_snapshot(
        data_dir=settings.data_dir,
        primary_version=selected_primary_version,
        secondary_config=secondary_config,
        as_of_date=as_of_date,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="etf-pool", description="动态ETF池工具")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="检查本地配置但不显示密钥")
    config_parser = subparsers.add_parser("show-config", help="显示当前生效的筛选配置")
    config_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    sync_parser = subparsers.add_parser("sync-classify", help="同步全部上市ETF并生成分类实验")
    sync_parser.add_argument("--as-of-date", default=date.today().isoformat())
    sync_parser.add_argument(
        "--classification-config",
        type=Path,
        default=CLASSIFICATION_CONFIG_PATH,
    )
    classify_parser = subparsers.add_parser("classify-snapshot", help="重新分类已有ETF快照")
    classify_parser.add_argument("--as-of-date", required=True)
    classify_parser.add_argument(
        "--classification-config",
        type=Path,
        default=CLASSIFICATION_CONFIG_PATH,
    )
    secondary_parser = subparsers.add_parser("classify-secondary", help="生成ETF二级相关暴露分组")
    secondary_parser.add_argument("--as-of-date", required=True)
    secondary_parser.add_argument("--primary-version")
    secondary_parser.add_argument(
        "--classification-config",
        type=Path,
        default=CLASSIFICATION_CONFIG_PATH,
    )
    secondary_parser.add_argument(
        "--secondary-config",
        type=Path,
        default=SECONDARY_CLASSIFICATION_CONFIG_PATH,
    )
    return parser


def main(argv: Sequence[str] | None = None):
    args = build_parser().parse_args(argv)
    if args.command == "doctor":
        return _doctor()
    if args.command == "show-config":
        return _show_config(args.config)
    if args.command == "sync-classify":
        return _sync_classify(args.as_of_date, args.classification_config)
    if args.command == "classify-snapshot":
        return _classify_snapshot(args.as_of_date, args.classification_config)
    if args.command == "classify-secondary":
        return _classify_secondary(
            args.as_of_date,
            args.primary_version,
            args.classification_config,
            args.secondary_config,
        )
    raise AssertionError(f"未处理的命令：{args.command}")
