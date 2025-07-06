from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    bot_token: str = Field(alias="BOT_TOKEN")
    artifacts_token: str = Field(alias="ARTIFACTS_TOKEN")
