"""
Application configuration.

All non-secret settings are read from config.toml (path resolved relative to this
file's directory parent, i.e. the backend/ root).  Secret values are read from
environment variables (loaded from the .env file via pydantic-settings).
"""
from __future__ import annotations

import os
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve config.toml from backend/config.toml regardless of cwd
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_CONFIG_PATH = _BACKEND_DIR / "config.toml"


def _load_toml() -> dict[str, Any]:
    with open(_CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


class Settings(BaseSettings):
    """
    Pydantic-Settings model.  Secrets come from environment variables / .env file.
    Non-secret structured config is loaded separately from config.toml.
    """

    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Secrets (from .env or real environment) ──────────────────────────────
    ebay_app_id: str = Field(default="", description="eBay Application ID (Client ID)")
    ebay_cert_id: str = Field(default="", description="eBay Certificate ID (Client Secret)")
    database_user: str = Field(default="ebay")
    database_password: str = Field(default="")
    api_token: str = Field(default="", description="Bearer token for API auth (optional)")

    # ── Non-secret config loaded separately ──────────────────────────────────
    # (populated after init from config.toml via _apply_toml)
    app_title: str = "eBay Market Intelligence"
    app_debug: bool = False
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_rotation: str = "50 MB"
    log_retention: str = "30 days"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173"]

    auth_enabled: bool = False

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "ebay_intel"
    db_pool_size: int = 10
    db_pool_max_overflow: int = 5

    ebay_site_id: str = "EBAY-GB"
    ebay_max_pages: int = 10
    ebay_results_per_page: int = 100
    ebay_request_timeout_seconds: float = 15.0
    ebay_retry_attempts: int = 3
    ebay_retry_backoff_seconds: float = 2.0

    scraper_enabled: bool = True
    scraper_completed_days: int = 90
    scraper_user_agent: str = "Mozilla/5.0 (compatible; EbayIntelBot/1.0)"
    scraper_delay_between_pages_seconds: float = 1.5

    scheduler_default_interval_minutes: int = 60
    scheduler_max_concurrent_polls: int = 3
    scheduler_jitter_seconds: int = 30

    def _apply_toml(self, data: dict[str, Any]) -> None:
        """Overlay config.toml values onto this settings instance."""
        app = data.get("app", {})
        self.app_title = app.get("title", self.app_title)
        self.app_debug = app.get("debug", self.app_debug)
        self.log_level = app.get("log_level", self.log_level)
        self.log_file = app.get("log_file", self.log_file)
        self.log_rotation = app.get("log_rotation", self.log_rotation)
        self.log_retention = app.get("log_retention", self.log_retention)

        api = data.get("api", {})
        self.api_host = api.get("host", self.api_host)
        self.api_port = api.get("port", self.api_port)
        self.cors_origins = api.get("cors_origins", self.cors_origins)

        auth = data.get("auth", {})
        self.auth_enabled = auth.get("enabled", self.auth_enabled)

        db = data.get("database", {})
        self.db_host = db.get("host", self.db_host)
        self.db_port = db.get("port", self.db_port)
        self.db_name = db.get("name", self.db_name)
        self.db_pool_size = db.get("pool_size", self.db_pool_size)
        self.db_pool_max_overflow = db.get("pool_max_overflow", self.db_pool_max_overflow)

        ebay = data.get("ebay", {})
        self.ebay_site_id = ebay.get("site_id", self.ebay_site_id)
        self.ebay_max_pages = ebay.get("max_pages", self.ebay_max_pages)
        self.ebay_results_per_page = ebay.get("results_per_page", self.ebay_results_per_page)
        self.ebay_request_timeout_seconds = ebay.get("request_timeout_seconds", self.ebay_request_timeout_seconds)
        self.ebay_retry_attempts = ebay.get("retry_attempts", self.ebay_retry_attempts)
        self.ebay_retry_backoff_seconds = ebay.get("retry_backoff_seconds", self.ebay_retry_backoff_seconds)

        scraper = data.get("scraper", {})
        self.scraper_enabled = scraper.get("enabled", self.scraper_enabled)
        self.scraper_completed_days = scraper.get("completed_days", self.scraper_completed_days)
        self.scraper_user_agent = scraper.get("user_agent", self.scraper_user_agent)
        self.scraper_delay_between_pages_seconds = scraper.get("delay_between_pages_seconds", self.scraper_delay_between_pages_seconds)

        sched = data.get("scheduler", {})
        self.scheduler_default_interval_minutes = sched.get("default_interval_minutes", self.scheduler_default_interval_minutes)
        self.scheduler_max_concurrent_polls = sched.get("max_concurrent_polls", self.scheduler_max_concurrent_polls)
        self.scheduler_jitter_seconds = sched.get("jitter_seconds", self.scheduler_jitter_seconds)

    def _apply_env_overrides(self) -> None:
        """Let DATABASE_HOST / DATABASE_PORT / DATABASE_NAME env vars override
        config.toml values so Docker Compose can set them at runtime."""
        if v := os.environ.get("DATABASE_HOST"):
            self.db_host = v
        if v := os.environ.get("DATABASE_PORT"):
            self.db_port = int(v)
        if v := os.environ.get("DATABASE_NAME"):
            self.db_name = v

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def public_config(self) -> dict[str, Any]:
        """Return a dict of non-secret config values safe to expose via the API."""
        return {
            "app": {"title": self.app_title, "debug": self.app_debug, "log_level": self.log_level},
            "api": {"host": self.api_host, "port": self.api_port, "cors_origins": self.cors_origins},
            "auth": {"enabled": self.auth_enabled},
            "database": {"host": self.db_host, "port": self.db_port, "name": self.db_name},
            "ebay": {
                "site_id": self.ebay_site_id,
                "max_pages": self.ebay_max_pages,
                "results_per_page": self.ebay_results_per_page,
                "retry_attempts": self.ebay_retry_attempts,
            },
            "scraper": {
                "enabled": self.scraper_enabled,
                "completed_days": self.scraper_completed_days,
                "delay_between_pages_seconds": self.scraper_delay_between_pages_seconds,
            },
            "scheduler": {
                "default_interval_minutes": self.scheduler_default_interval_minutes,
                "max_concurrent_polls": self.scheduler_max_concurrent_polls,
                "jitter_seconds": self.scheduler_jitter_seconds,
            },
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton Settings instance (loaded once, cached forever)."""
    s = Settings()
    if _CONFIG_PATH.exists():
        s._apply_toml(_load_toml())
    s._apply_env_overrides()
    return s
