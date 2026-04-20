from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Urban Climate and Air Quality Analytics API"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./urban_climate.db"
    openweather_api_key: str | None = None
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
    openweather_geo_url: str = "https://api.openweathermap.org/geo/1.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
