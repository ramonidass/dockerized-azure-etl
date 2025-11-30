from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from pydantic import field_validator

env_path = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_path, extra="ignore")

    key: str
    base_url: str
    tether_wallet: str
    binance_wallet: str
    azure_storage_account: str = ""
    azure_storage_key: str = ""
    azure_container: str = ""

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v):
        from urllib.parse import urlparse

        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid base_url")
        return v


settings = Settings()
