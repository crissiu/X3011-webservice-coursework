from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
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


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["docs_url"] == "/docs"


def test_seed_and_analytics_flow():
    seed_response = client.post("/api/seed/reset")
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
    create_response = client.post("/api/stations", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()

    duplicate_response = client.post("/api/stations", json=payload)
    assert duplicate_response.status_code == 409

    update_response = client.put(
        f"/api/stations/{created['id']}",
        json={"description": "Updated station description."},
    )
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Updated station description."

    delete_response = client.delete(f"/api/stations/{created['id']}")
    assert delete_response.status_code == 204


def test_openweather_aqi_mapping():
    assert openweather_aqi_to_project_aqi(1) == 25
    assert openweather_aqi_to_project_aqi(3) == 125
    assert openweather_aqi_to_project_aqi(5) == 250
