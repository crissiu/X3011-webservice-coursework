# Urban Climate and Air Quality Analytics API

An individual Web Services and Web Data coursework project implementing a data-driven FastAPI service for city-level urban climate and air quality monitoring.

The API supports CRUD operations for monitoring stations and environmental observations, plus analytical endpoints for city summaries and pollution risk ranking.

## Technology Stack

- FastAPI for the HTTP API and automatic OpenAPI documentation.
- SQLAlchemy for database access and ORM models.
- SQLite for local development, with a simple path to PostgreSQL if deployed later.
- Pydantic for request and response validation.
- OpenWeatherMap Current Weather Data and Air Pollution APIs for optional live data import.
- Pytest and FastAPI TestClient for automated verification.

## Quick Start

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Configure optional OpenWeatherMap import:

```powershell
copy .env.example .env
```

Then add your OpenWeatherMap API key to `.env`.

Protected write and import endpoints require an API key header:

```text
X-API-Key: coursework-local-key
```

Run the API:

```powershell
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Seed demonstration data:

```powershell
curl -X POST http://127.0.0.1:8000/api/seed
```

Reset demonstration data after manual testing:

```powershell
curl -X POST http://127.0.0.1:8000/api/seed/reset
```

Run tests:

```powershell
python -m pytest
```

## Core Endpoints

- `GET /api/stations` - list all monitoring stations.
- `POST /api/stations` - create a station.
- `GET /api/stations/{station_id}` - read one station with observations.
- `PUT /api/stations/{station_id}` - update station metadata.
- `DELETE /api/stations/{station_id}` - delete a station and its observations.
- `POST /api/stations/from-openweather?city=York` - create or update a real OpenWeatherMap station and store the current reading.
- `GET /api/observations` - list observations, optionally filtered by city or station.
- `POST /api/observations` - create an environmental observation.
- `GET /api/analytics/compare?cities=Leeds,Manchester,Birmingham&data_source=openweather` - compare multiple cities by AQI, PM2.5, and temperature.
- `GET /api/analytics/cities/{city}` - city-level climate and pollution summary.
- `GET /api/analytics/risk-summary` - latest AQI risk ranking across stations.
- `POST /api/import/openweather/current?city=Leeds` - import live weather and air pollution readings from OpenWeatherMap.
- `POST /api/import/openweather/batch?cities=Leeds,Manchester,Birmingham` - import live data for multiple cities.
- `POST /api/import/openweather/refresh?cities=Leeds,Manchester,Birmingham` - replace existing live OpenWeatherMap records with fresh imports.
- `POST /api/seed/reset` - restore the built-in demonstration dataset.

Use `data_source=openweather` on query endpoints to focus on live imported data:

- `GET /api/observations?city=Leeds&data_source=openweather`
- `GET /api/analytics/cities/Leeds?data_source=openweather`
- `GET /api/analytics/risk-summary?data_source=openweather`

Recommended live-data demonstration flow:

1. `POST /api/seed/reset`
2. `POST /api/import/openweather/refresh?cities=Leeds,Manchester,Birmingham`
3. `GET /api/observations?data_source=openweather`
4. `GET /api/analytics/cities/Leeds?data_source=openweather`
5. `GET /api/analytics/risk-summary?data_source=openweather`
6. `GET /api/analytics/compare?cities=Leeds,Manchester,Birmingham&data_source=openweather`

To add a new city from real data, run `POST /api/stations/from-openweather?city=York`, then query `GET /api/observations?city=York&data_source=openweather` and `GET /api/analytics/cities/York?data_source=openweather`.

## Coursework Deliverables

- Source code: this repository.
- API documentation: available from `/docs`; this will also be exported to PDF for submission.
- Technical report: to be written as a maximum 5-page PDF.
- Presentation slides: to be prepared for the 5-minute oral demonstration.
- GenAI declaration: to be included in the technical report appendix with selected conversation logs.

## Dataset Plan

The first implementation includes a small internal demonstration dataset so the API can be run and tested immediately. The project also supports optional live data import from OpenWeatherMap Current Weather Data and Air Pollution APIs when an API key is configured locally.
