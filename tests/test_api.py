from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app import crud, models
from app.services.openweather import openweather_aqi_to_project_aqi


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)
client = TestClient(app)
API_HEADERS = {"X-API-Key": "coursework-local-key"}


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["docs_url"] == "/docs"


def test_seed_and_analytics_flow():
    seed_response = client.post("/api/seed/reset", headers=API_HEADERS)
    assert seed_response.status_code == 201

    stations_response = client.get("/api/stations")
    assert stations_response.status_code == 200
    stations = stations_response.json()
    assert len(stations) >= 3

    analytics_response = client.get("/api/analytics/cities/Leeds")
    assert analytics_response.status_code == 200
    analytics = analytics_response.json()
    assert analytics["city"] == "Leeds"
    assert analytics["observation_count"] >= 1

    city_filter_response = client.get("/api/observations?city=Leeds")
    assert city_filter_response.status_code == 200
    assert len(city_filter_response.json()) == 3

    demo_filter_response = client.get("/api/observations?city=Leeds&data_source=demo")
    assert demo_filter_response.status_code == 200
    assert len(demo_filter_response.json()) == 3

    openweather_filter_response = client.get("/api/observations?city=Leeds&data_source=openweather")
    assert openweather_filter_response.status_code == 200
    assert openweather_filter_response.json() == []

    comparison_response = client.get("/api/analytics/compare?cities=Leeds,Manchester,Birmingham&data_source=demo")
    assert comparison_response.status_code == 200
    comparison = comparison_response.json()
    assert comparison["cities_compared"] == 3
    assert comparison["highest_aqi_city"] in {"Leeds", "Manchester", "Birmingham"}


def test_create_update_delete_station():
    payload = {
        "name": "Liverpool Dockside Monitor",
        "city": "Liverpool",
        "country": "United Kingdom",
        "latitude": 53.4084,
        "longitude": -2.9916,
        "environment_type": "urban",
        "description": "Monitoring station near the waterfront.",
    }
    unauthorised_response = client.post("/api/stations", json=payload)
    assert unauthorised_response.status_code == 401

    create_response = client.post("/api/stations", json=payload, headers=API_HEADERS)
    assert create_response.status_code == 201
    created = create_response.json()

    duplicate_response = client.post("/api/stations", json=payload, headers=API_HEADERS)
    assert duplicate_response.status_code == 409

    update_response = client.put(
        f"/api/stations/{created['id']}",
        json={"description": "Updated station description."},
        headers=API_HEADERS,
    )
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Updated station description."

    delete_response = client.delete(f"/api/stations/{created['id']}", headers=API_HEADERS)
    assert delete_response.status_code == 204


def test_openweather_aqi_mapping():
    assert openweather_aqi_to_project_aqi(1) == 25
    assert openweather_aqi_to_project_aqi(3) == 125
    assert openweather_aqi_to_project_aqi(5) == 250


def test_openweather_refresh_endpoint_validates_city_list():
    response = client.post("/api/import/openweather/refresh?cities=,,", headers=API_HEADERS)
    assert response.status_code == 422


def test_openweather_station_create_route_is_documented():
    schema = app.openapi()
    assert "/api/stations/from-openweather" in schema["paths"]


def test_observation_lookup_by_station_and_time():
    db = TestingSessionLocal()
    try:
        station = models.Station(
            name="Deduplication Test Station",
            city="Test City",
            country="GB",
            latitude=1.0,
            longitude=1.0,
            environment_type="external_api",
        )
        db.add(station)
        db.commit()
        db.refresh(station)

        created = models.Observation(
            station_id=station.id,
            observed_at=__import__("datetime").datetime(2026, 4, 20, 12, 0),
            temperature_c=10,
            humidity_pct=50,
            pm25=1,
            pm10=2,
            no2=3,
            o3=4,
            aqi=25,
        )
        db.add(created)
        db.commit()

        found = crud.get_observation_by_station_and_time(db, station.id, created.observed_at)
        assert found is not None
        assert found.id == created.id
    finally:
        db.close()
