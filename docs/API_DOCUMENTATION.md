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

Expected response: `200 OK`

## Analytics

### City Analytics

`GET /api/analytics/cities/{city}`

Returns observation count, average pollutant levels, average AQI, maximum AQI, hottest temperature, and the latest observation timestamp.

Expected response: `200 OK`

### Risk Summary

`GET /api/analytics/risk-summary`

Returns the latest AQI status for each station ordered by risk.

Expected response: `200 OK`

## Error Codes

- `404 Not Found` - requested station, observation, or analytics result does not exist.
- `409 Conflict` - station name already exists.
- `422 Unprocessable Entity` - request body or parameters fail validation.

## Demo Data Reset

If manual testing changes the built-in demo records, restore the default Leeds, Manchester, and Birmingham dataset with:

```text
POST /api/seed/reset
```
