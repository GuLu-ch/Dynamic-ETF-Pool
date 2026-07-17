from pathlib import Path

from etf_pool.config import Settings, load_config


def test_default_config_has_screening_section() -> None:
    config = load_config()
    assert config["screening"]["min_history_days"] > 0


def test_settings_reads_standard_env_keys(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "TUSHARE_TOKEN=test-token\n"
        "ETF_DATA_PROVIDER=tushare\n"
        "ETF_POOL_DATA_DIR=custom-data\n",
        encoding="utf-8",
    )

    settings = Settings.from_env(env_file)

    assert settings.tushare_token == "test-token"
    assert settings.data_provider == "tushare"
    assert settings.data_dir.name == "custom-data"
