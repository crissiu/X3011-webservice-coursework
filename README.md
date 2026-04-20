# Urban Climate and Air Quality Analytics API

An individual Web Services and Web Data coursework project implementing a data-driven FastAPI service for city-level urban climate and air quality monitoring.

The API supports CRUD operations for monitoring stations and environmental observations, plus analytical endpoints for city summaries and pollution risk ranking.

## Technology Stack

- FastAPI for the HTTP API and automatic OpenAPI documentation.
- SQLAlchemy for database access and ORM models.
- SQLite for local development, with a simple path to PostgreSQL if deployed later.
- Pydantic for request and response validation.
- Pytest and FastAPI TestClient for automated verification.

## Quick Start

Install dependencies:

```powershell
python -m pip install -r requirements.txt
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
- `GET /api/observations` - list observations, optionally filtered by city or station.
- `POST /api/observations` - create an environmental observation.
- `GET /api/analytics/cities/{city}` - city-level climate and pollution summary.
- `GET /api/analytics/risk-summary` - latest AQI risk ranking across stations.

## Coursework Deliverables

- Source code: this repository.
- API documentation: available from `/docs`; this will also be exported to PDF for submission.
- Technical report: to be written as a maximum 5-page PDF.
- Presentation slides: to be prepared for the 5-minute oral demonstration.
- GenAI declaration: to be included in the technical report appendix with selected conversation logs.

## Dataset Plan

The first implementation includes a small internal demonstration dataset so the API can be run and tested immediately. The final coursework version should cite and, where practical, import public air quality or climate data from sources such as DEFRA UK-AIR, data.gov.uk, OpenAQ, or OpenWeatherMap.
