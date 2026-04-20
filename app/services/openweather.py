from datetime import UTC, datetime

import httpx
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.config import settings


class OpenWeatherError(RuntimeError):
    pass


def openweather_aqi_to_project_aqi(openweather_aqi: int) -> int:
    # OpenWeather uses 1-5 qualitative AQI. The project stores a 0-500 style score.
    mapping = {
        1: 25,
        2: 75,
        3: 125,
        4: 175,
        5: 250,
    }
    return mapping.get(openweather_aqi, 0)


def import_current_weather_for_city(db: Session, city: str) -> schemas.OpenWeatherImportResult:
    if not settings.openweather_api_key:
        raise OpenWeatherError("OPENWEATHER_API_KEY is not configured")

    geocoding_url = f"{settings.openweather_geo_url}/direct"
    weather_url = f"{settings.openweather_base_url}/weather"
    air_url = f"{settings.openweather_base_url}/air_pollution"

    with httpx.Client(timeout=15.0) as client:
        geocoding_response = client.get(
            geocoding_url,
            params={
                "q": city,
                "limit": 1,
                "appid": settings.openweather_api_key,
            },
        )
        _raise_for_openweather_error(geocoding_response, "geocoding")
        geocoding = geocoding_response.json()
        if not geocoding:
            raise OpenWeatherError(f"OpenWeatherMap could not find coordinates for city: {city}")

        location = geocoding[0]
        latitude = location.get("lat")
        longitude = location.get("lon")
        if latitude is None or longitude is None:
            raise OpenWeatherError("OpenWeatherMap geocoding response did not include coordinates")

        weather_response = client.get(
            weather_url,
            params={
                "lat": latitude,
                "lon": longitude,
                "appid": settings.openweather_api_key,
                "units": "metric",
            },
        )
        _raise_for_openweather_error(weather_response, "current weather")
        weather = weather_response.json()

        air_response = client.get(
            air_url,
            params={
                "lat": latitude,
                "lon": longitude,
                "appid": settings.openweather_api_key,
            },
        )
        _raise_for_openweather_error(air_response, "air pollution")
        air = air_response.json()

    air_items = air.get("list") or []
    if not air_items:
        raise OpenWeatherError("OpenWeatherMap air pollution response did not include measurements")

    air_reading = air_items[0]
    components = air_reading.get("components") or {}
    openweather_aqi = int((air_reading.get("main") or {}).get("aqi", 0))
    resolved_city = location.get("name") or weather.get("name") or city
    station_name = f"{resolved_city} OpenWeatherMap Station"
    country = location.get("country") or (weather.get("sys") or {}).get("country", "Unknown")
    observed_at = datetime.fromtimestamp(int(weather.get("dt")), UTC)

    station = crud.get_station_by_city_and_name(db, resolved_city, station_name)
    if station is None:
        station = models.Station(
            name=station_name,
            city=resolved_city,
            country=country,
            latitude=float(latitude),
            longitude=float(longitude),
            environment_type="external_api",
            description="Station generated from OpenWeatherMap current weather and air pollution data.",
        )
        db.add(station)
        db.commit()
        db.refresh(station)

    observation = models.Observation(
        station_id=station.id,
        observed_at=observed_at,
        temperature_c=float((weather.get("main") or {}).get("temp")),
        humidity_pct=float((weather.get("main") or {}).get("humidity")),
        pm25=float(components.get("pm2_5", 0)),
        pm10=float(components.get("pm10", 0)),
        no2=float(components.get("no2", 0)),
        o3=float(components.get("o3", 0)),
        aqi=openweather_aqi_to_project_aqi(openweather_aqi),
        notes=(
            "Imported from OpenWeatherMap current weather and air pollution APIs. "
            f"OpenWeather AQI scale value: {openweather_aqi}."
        ),
    )
    db.add(observation)
    db.commit()
    db.refresh(observation)

    return schemas.OpenWeatherImportResult(
        station_id=station.id,
        station_name=station.name,
        observation_id=observation.id,
        city=station.city,
        country=station.country,
        observed_at=observation.observed_at,
        temperature_c=observation.temperature_c,
        humidity_pct=observation.humidity_pct,
        pm25=observation.pm25,
        pm10=observation.pm10,
        no2=observation.no2,
        o3=observation.o3,
        openweather_aqi=openweather_aqi,
        project_aqi=observation.aqi,
        source="OpenWeatherMap Current Weather Data and Air Pollution API",
    )


def _raise_for_openweather_error(response: httpx.Response, dataset_name: str) -> None:
    if response.is_success:
        return
    try:
        detail = response.json().get("message", response.text)
    except ValueError:
        detail = response.text
    raise OpenWeatherError(f"OpenWeatherMap {dataset_name} request failed: {detail}")
