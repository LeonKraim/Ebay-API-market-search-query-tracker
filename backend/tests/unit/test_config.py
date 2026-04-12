"""Unit tests for app configuration loading."""
from __future__ import annotations

import os
import pytest

from app.config import Settings, get_settings


class TestSettings:
    def test_defaults_loaded(self):
        s = Settings()
        assert s.api_host == "0.0.0.0"
        assert s.api_port == 8000
        assert s.app_debug is False

    def test_ebay_app_id_from_env(self):
        s = Settings()
        assert s.ebay_app_id == "fake-app-id"

    def test_database_url_contains_user(self):
        s = Settings()
        url = s.database_url
        assert "test" in url  # DATABASE_USER=test

    def test_public_config_excludes_secrets(self):
        s = Settings()
        pub = s.public_config
        # Flatten all keys to check secrets are not present at any level
        all_text = str(pub)
        assert "fake-app-id" not in all_text
        assert "database_password" not in pub
        assert "api_token" not in pub

    def test_public_config_contains_app_title(self):
        s = Settings()
        pub = s.public_config
        assert "app" in pub
        assert "title" in pub["app"]

    def test_get_settings_returns_same_instance(self):
        """lru_cache must return the same object."""
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_auth_enabled_defaults_false(self):
        s = Settings()
        assert s.auth_enabled is False
