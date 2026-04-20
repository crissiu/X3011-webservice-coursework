# API Documentation

Base URL for local development:

```text
http://127.0.0.1:8000
```

Interactive documentation is available at:

```text
/docs
```

OpenAPI schema is available at:

```text
/openapi.json
```

## Authentication

Manual write operations such as creating, updating, or deleting records require the `X-API-Key` request header. OpenWeatherMap city import endpoints are intentionally public so examiners can quickly query and import real city data without authorising first.

For local development, set `APP_API_KEY` in `.env`, then click `Authorize` in Swagger UI and enter that value.

## Stations

### Create Station

`POST /api/stations`

Request:

```json
{
  "name": "Leeds City Centre Monitor",
  "city": "Leeds",
  "country": "United Kingdom",
  "latitude": 53.7997,
  "longitude": -1.5492,
  "environment_type": "urban",
  "description": "Roadside station for city monitoring."
}
```

Expected response: `201 Created`

### List Stations

`GET /api/stations`

Expected response: `200 OK`

### Update Station

`PUT /api/stations/{station_id}`

Expected response: `200 OK`

### Delete Station

`DELETE /api/stations/{station_id}`

Expected response: `204 No Content`

### Create Station From OpenWeatherMap

`POST /api/stations/from-openweather?city=York`

Creates an OpenWeatherMap-backed station for the requested city if it does not already exist, calls OpenWeatherMap for current weather and air pollution data, and stores the result as an observation in the database.

Expected response: `201 Created`

Authentication: not required for this convenience endpoint.

Follow-up queries:

- `GET /api/observations?city=York&data_source=openweather`
- `GET /api/analytics/cities/York?data_source=openweather`

## Observations

### Create Observation

`POST /api/observations`

Request:

```json
{
  "station_id": 1,
  "observed_at": "2026-04-19T09:00:00",
  "temperature_c": 12.8,
  "humidity_pct": 71,
  "pm25": 25.6,
  "pm10": 36.2,
  "no2": 40.2,
  "o3": 28.5,
  "aqi": 102,
  "notes": "Particulate spike after still overnight conditions."
}
```

Expected response: `201 Created`

### List Observations

`GET /api/observations`

Optional query parameters:

- `city`
- `station_id`
- `data_source` - use `openweather` for live imported data or `demo` for built-in seed data.

Expected response: `200 OK`

## Analytics

### City Comparison

`GET /api/analytics/compare?cities=Leeds,Manchester,Birmingham&data_source=openweather`

Compares multiple cities using the same observation database used by the CRUD and import endpoints. The response identifies the city with the highest average AQI, highest PM2.5, highest temperature, and lowest average AQI.

Expected response: `200 OK`

### City Analytics

`GET /api/analytics/cities/{city}`

Returns observation count, average pollutant levels, average AQI, maximum AQI, hottest temperature, and the latest observation timestamp.

Expected response: `200 OK`

Use `GET /api/analytics/cities/Leeds?data_source=openweather` to calculate analytics from live OpenWeatherMap imports only.

### Risk Summary

`GET /api/analytics/risk-summary`

Returns the latest AQI status for each station ordered by risk.

Expected response: `200 OK`

Use `GET /api/analytics/risk-summary?data_source=openweather` to rank live OpenWeatherMap stations only.

## OpenWeatherMap Import

### Import Current Weather and Air Pollution

`POST /api/import/openweather/current?city=Leeds`

This endpoint calls OpenWeatherMap Geocoding API to resolve city coordinates, Current Weather Data for temperature and humidity, and Air Pollution API for PM2.5, PM10, NO2, O3, and OpenWeather AQI. The result is stored as a new observation in the local database.

Expected response: `201 Created`

Authentication: not required.

### Batch Import Current Data

`POST /api/import/openweather/batch?cities=Leeds,Manchester,Birmingham`

Imports live weather and air pollution observations for multiple cities and stores them in the same database tables used by the CRUD and analytics endpoints.

Expected response: `201 Created`

Authentication: not required.

### Refresh Live OpenWeatherMap Data

`POST /api/import/openweather/refresh?cities=Leeds,Manchester,Birmingham`

Imports fresh live data for the requested cities while preserving existing OpenWeatherMap-backed stations and historical observations. If OpenWeatherMap returns the same station and timestamp again, the existing observation is updated instead of duplicated.

Expected response: `201 Created`

Authentication: not required.

Notes:

- Requires `OPENWEATHER_API_KEY` in the local `.env` file.
- The API key must not be committed to GitHub.
- OpenWeatherMap AQI uses a 1-5 scale; this project maps it to an internal 0-500 style score for consistency with existing observations.

## Error Codes

- `401 Unauthorized` - protected write/import endpoint called without a valid `X-API-Key` header.
- `404 Not Found` - requested station, observation, or analytics result does not exist.
- `409 Conflict` - station name already exists.
- `422 Unprocessable Entity` - request body or parameters fail validation.
- `502 Bad Gateway` - external OpenWeatherMap import failed or API key is missing.

## Demo Data Reset

If manual testing changes the built-in demo records, restore the default Leeds, Manchester, and Birmingham dataset with:

```text
POST /api/seed/reset
```
