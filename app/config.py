from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Urban Climate and Air Quality Analytics API"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./urban_climate.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
