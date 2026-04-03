from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT / "product" / "backend" / "supabase" / ".env"


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "Indian Specialty Coffee Sourcing Platform"
    app_version: str = "0.2.0"
    log_level: str = "INFO"
    supabase_db_url: str
    session_cookie: str = "coffee_session"
    session_max_age: int = 60 * 60 * 24 * 14
    host: str = "127.0.0.1"
    port: int = 8000
    root_path: str = ""
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    trusted_hosts: str = "localhost,127.0.0.1,testserver"
    docs_enabled: bool = True
    secure_cookies: bool = False
    alert_email_to: str | None = None
    smtp_from_email: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    resend_api_key: str | None = None
    resend_from_email: str | None = None
    resend_reply_to: str | None = None

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def trusted_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.trusted_hosts.split(",") if host.strip()]


settings = Settings()
