# Deployment Guide

This project is prepared for deployment as a FastAPI web service on Render.

## Recommended Platform

Render is recommended for this coursework because it supports FastAPI directly, installs dependencies from `requirements.txt`, and runs Uvicorn with the platform-provided `PORT` environment variable.

## Required Environment Variables

Set these in the hosting dashboard:

```text
PYTHON_VERSION=3.12.10
APP_API_KEY=coursework-local-key
OPENWEATHER_API_KEY=your_openweathermap_api_key
```

Do not commit real API keys to GitHub.

## Render Deployment Steps

1. Push the latest code to GitHub.
2. Log in to Render.
3. Create a new Web Service from the GitHub repository.
4. Use the detected `render.yaml` settings.
5. Add the required environment variables.
6. Deploy the service.

Render should use:

```text
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The repository includes `.python-version` and `render.yaml` settings to pin deployment to Python `3.12.10`. This avoids Python 3.14 dependency wheel issues with packages such as `pydantic-core`.

## Post-Deployment Test Flow

After deployment, open:

```text
https://your-service-name.onrender.com/docs
```

Test public endpoints:

```text
GET /
POST /api/stations/from-openweather?city=Yuxi
GET /api/observations?city=Yuxi&data_source=openweather
GET /api/analytics/cities/Yuxi?data_source=openweather
GET /api/analytics/compare?cities=Leeds,Yuxi&data_source=openweather
```

For protected manual write or reset endpoints, click `Authorize` in Swagger UI and enter the value of `APP_API_KEY`.

## Limitation

The current deployment uses SQLite for simplicity and coursework demonstration. On some cloud platforms, local SQLite files may not persist across service restarts or redeployments. For a production version, migrate to managed PostgreSQL and add database migrations with Alembic.
