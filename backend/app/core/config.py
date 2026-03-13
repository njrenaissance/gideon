from importlib.metadata import version
from typing import Any, Literal

from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class OtelSettings(BaseSettings):
    """OpenTelemetry sub-config (OPENCASE_OTEL_ prefix)."""

    enabled: bool = False
    exporter: Literal["console", "otlp"] = "console"
    endpoint: str = "http://localhost:4318"
    service_name: str = "opencase-api"
    sample_rate: float = 1.0

    model_config = SettingsConfigDict(env_prefix="OPENCASE_OTEL_")


class Settings(BaseSettings):
    """Application settings with layered loading.

    Priority (highest wins):
      1. Environment variables (OPENCASE_ prefix)
      2. .env file
      3. config.json file
      4. Hard-coded defaults
    """

    app_name: str = "OpenCase"
    app_version: str = version("opencase")
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_output: Literal["stdout", "stderr"] = "stdout"
    deployment_mode: str = "airgapped"
    otel: OtelSettings = OtelSettings()

    model_config = SettingsConfigDict(
        env_prefix="OPENCASE_",
        env_file=".env",
        env_file_encoding="utf-8",
        json_file="config.json",
        json_file_encoding="utf-8",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003 — no secrets dir used
        **kwargs: Any,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
            dotenv_settings,
            JsonConfigSettingsSource(settings_cls),
            init_settings,  # allows Settings(field=val) for testing
        )


settings = Settings()
