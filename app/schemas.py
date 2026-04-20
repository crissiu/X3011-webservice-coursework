from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    city: str = Field(..., min_length=2, max_length=80)
    country: str = Field(default="United Kingdom", min_length=2, max_length=80)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    environment_type: str = Field(default="urban", min_length=3, max_length=40)
    description: str | None = None

    @field_validator("name", "city", "country", "environment_type", mode="before")
    @classmethod
    def normalize_text(cls, value: str):
        return value.strip()


class StationCreate(StationBase):
    pass


class StationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    city: str | None = Field(default=None, min_length=2, max_length=80)
    country: str | None = Field(default=None, min_length=2, max_length=80)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    environment_type: str | None = Field(default=None, min_length=3, max_length=40)
    description: str | None = None

    @field_validator("name", "city", "country", "environment_type", mode="before")
    @classmethod
    def normalize_text(cls, value: str | None):
        if value is None:
            return value
        return value.strip()


class ObservationBase(BaseModel):
    observed_at: datetime
    temperature_c: float = Field(..., ge=-50, le=70)
    humidity_pct: float = Field(..., ge=0, le=100)
    pm25: float = Field(..., ge=0)
    pm10: float = Field(..., ge=0)
    no2: float = Field(..., ge=0)
    o3: float = Field(..., ge=0)
    aqi: int = Field(..., ge=0, le=500)
    notes: str | None = None


class ObservationCreate(ObservationBase):
    station_id: int = Field(..., gt=0)


class ObservationUpdate(BaseModel):
    station_id: int | None = Field(default=None, gt=0)
    observed_at: datetime | None = None
    temperature_c: float | None = Field(default=None, ge=-50, le=70)
    humidity_pct: float | None = Field(default=None, ge=0, le=100)
    pm25: float | None = Field(default=None, ge=0)
    pm10: float | None = Field(default=None, ge=0)
    no2: float | None = Field(default=None, ge=0)
    o3: float | None = Field(default=None, ge=0)
    aqi: int | None = Field(default=None, ge=0, le=500)
    notes: str | None = None


class ObservationRead(ObservationBase):
    id: int
    station_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StationRead(StationBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StationDetail(StationRead):
    observations: list[ObservationRead] = Field(default_factory=list)


class CityAnalytics(BaseModel):
    city: str
    observation_count: int
    average_temperature_c: float
    average_pm25: float
    average_pm10: float
    average_no2: float
    average_o3: float
    average_aqi: float
    max_aqi: int
    hottest_temperature_c: float
    latest_observation_at: datetime | None = None


class RiskSummary(BaseModel):
    station_id: int
    station_name: str
    city: str
    latest_aqi: int
    latest_pm25: float
    observed_at: datetime
    risk_level: str


class SeedSummary(BaseModel):
    stations_created: int
    observations_created: int
