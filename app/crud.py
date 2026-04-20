from datetime import datetime

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, joinedload

from app import models, schemas


def list_stations(db: Session) -> list[models.Station]:
    stmt = select(models.Station).order_by(models.Station.city, models.Station.name)
    return list(db.scalars(stmt).all())


def get_station(db: Session, station_id: int) -> models.Station | None:
    stmt = (
        select(models.Station)
        .options(joinedload(models.Station.observations))
        .where(models.Station.id == station_id)
    )
    return db.scalars(stmt).unique().first()


def get_station_by_name(db: Session, name: str) -> models.Station | None:
    stmt = select(models.Station).where(func.lower(models.Station.name) == name.lower())
    return db.scalar(stmt)


def create_station(db: Session, station_in: schemas.StationCreate) -> models.Station:
    station = models.Station(**station_in.model_dump())
    db.add(station)
    db.commit()
    db.refresh(station)
    return station


def update_station(db: Session, station: models.Station, station_in: schemas.StationUpdate) -> models.Station:
    for field, value in station_in.model_dump(exclude_unset=True).items():
        setattr(station, field, value)
    db.commit()
    db.refresh(station)
    return station


def delete_station(db: Session, station: models.Station) -> None:
    db.delete(station)
    db.commit()


def list_observations(db: Session, city: str | None = None, station_id: int | None = None) -> list[models.Observation]:
    stmt = select(models.Observation).order_by(desc(models.Observation.observed_at))
    if city:
        stmt = stmt.join(models.Station).where(func.lower(models.Station.city) == city.lower())
    if station_id:
        stmt = stmt.where(models.Observation.station_id == station_id)
    return list(db.scalars(stmt).all())


def get_observation(db: Session, observation_id: int) -> models.Observation | None:
    stmt = select(models.Observation).where(models.Observation.id == observation_id)
    return db.scalar(stmt)


def create_observation(db: Session, observation_in: schemas.ObservationCreate) -> models.Observation:
    observation = models.Observation(**observation_in.model_dump())
    db.add(observation)
    db.commit()
    db.refresh(observation)
    return observation


def update_observation(
    db: Session,
    observation: models.Observation,
    observation_in: schemas.ObservationUpdate,
) -> models.Observation:
    for field, value in observation_in.model_dump(exclude_unset=True).items():
        setattr(observation, field, value)
    db.commit()
    db.refresh(observation)
    return observation


def delete_observation(db: Session, observation: models.Observation) -> None:
    db.delete(observation)
    db.commit()


def get_city_analytics(db: Session, city: str) -> schemas.CityAnalytics | None:
    stmt = (
        select(
            models.Station.city.label("city"),
            func.count(models.Observation.id).label("observation_count"),
            func.avg(models.Observation.temperature_c).label("average_temperature_c"),
            func.avg(models.Observation.pm25).label("average_pm25"),
            func.avg(models.Observation.pm10).label("average_pm10"),
            func.avg(models.Observation.no2).label("average_no2"),
            func.avg(models.Observation.o3).label("average_o3"),
            func.avg(models.Observation.aqi).label("average_aqi"),
            func.max(models.Observation.aqi).label("max_aqi"),
            func.max(models.Observation.temperature_c).label("hottest_temperature_c"),
            func.max(models.Observation.observed_at).label("latest_observation_at"),
        )
        .join(models.Observation, models.Observation.station_id == models.Station.id)
        .where(func.lower(models.Station.city) == city.lower())
        .group_by(models.Station.city)
    )
    row = db.execute(stmt).mappings().first()
    return schemas.CityAnalytics(**row) if row else None


def get_latest_risk_summary(db: Session) -> list[schemas.RiskSummary]:
    latest_per_station = (
        select(
            models.Observation.station_id,
            func.max(models.Observation.observed_at).label("latest_observed_at"),
        )
        .group_by(models.Observation.station_id)
        .subquery()
    )

    stmt = (
        select(
            models.Station.id.label("station_id"),
            models.Station.name.label("station_name"),
            models.Station.city.label("city"),
            models.Observation.aqi.label("latest_aqi"),
            models.Observation.pm25.label("latest_pm25"),
            models.Observation.observed_at.label("observed_at"),
        )
        .join(latest_per_station, latest_per_station.c.station_id == models.Station.id)
        .join(
            models.Observation,
            (models.Observation.station_id == models.Station.id)
            & (models.Observation.observed_at == latest_per_station.c.latest_observed_at),
        )
        .order_by(desc(models.Observation.aqi), desc(models.Observation.pm25))
    )

    results: list[schemas.RiskSummary] = []
    for row in db.execute(stmt).mappings():
        aqi = row["latest_aqi"]
        if aqi >= 151:
            risk = "unhealthy"
        elif aqi >= 101:
            risk = "unhealthy_for_sensitive_groups"
        elif aqi >= 51:
            risk = "moderate"
        else:
            risk = "good"
        results.append(schemas.RiskSummary(**row, risk_level=risk))
    return results


def seed_demo_data(db: Session) -> schemas.SeedSummary:
    if db.scalar(select(func.count(models.Station.id))) > 0:
        return schemas.SeedSummary(stations_created=0, observations_created=0)

    stations = [
        models.Station(
            name="Leeds City Centre Monitor",
            city="Leeds",
            country="United Kingdom",
            latitude=53.7997,
            longitude=-1.5492,
            environment_type="urban",
            description="High-footfall roadside station used for central city monitoring.",
        ),
        models.Station(
            name="Manchester Piccadilly Monitor",
            city="Manchester",
            country="United Kingdom",
            latitude=53.4808,
            longitude=-2.2426,
            environment_type="urban",
            description="Transport-adjacent station for commuter and roadside analysis.",
        ),
        models.Station(
            name="Birmingham Eastside Monitor",
            city="Birmingham",
            country="United Kingdom",
            latitude=52.4862,
            longitude=-1.8904,
            environment_type="urban_background",
            description="Mixed-use district station for air quality and climate trend comparisons.",
        ),
    ]
    db.add_all(stations)
    db.flush()

    sample_rows = [
        (stations[0].id, datetime(2026, 4, 18, 9, 0), 14.2, 65.0, 12.1, 19.4, 24.0, 31.4, 48, "Morning baseline."),
        (stations[0].id, datetime(2026, 4, 18, 15, 0), 18.7, 53.0, 18.3, 27.9, 32.7, 46.5, 72, "Warmer afternoon with higher traffic emissions."),
        (stations[0].id, datetime(2026, 4, 19, 9, 0), 12.8, 71.0, 25.6, 36.2, 40.2, 28.5, 102, "Particulate spike after still overnight conditions."),
        (stations[1].id, datetime(2026, 4, 18, 9, 0), 13.5, 68.0, 15.0, 22.7, 26.1, 29.8, 55, "Moderate roadside pollution."),
        (stations[1].id, datetime(2026, 4, 18, 18, 0), 16.1, 58.0, 21.4, 30.5, 37.8, 35.6, 88, "Rush-hour pollution increase."),
        (stations[1].id, datetime(2026, 4, 19, 9, 0), 11.9, 74.0, 27.9, 39.8, 42.1, 24.9, 109, "Poor dispersal conditions raised AQI."),
        (stations[2].id, datetime(2026, 4, 18, 9, 0), 12.4, 70.0, 9.4, 15.8, 19.7, 33.2, 40, "Background site with relatively low pollution."),
        (stations[2].id, datetime(2026, 4, 18, 16, 0), 17.6, 54.0, 13.3, 20.1, 24.4, 41.0, 57, "Afternoon ozone increase."),
        (stations[2].id, datetime(2026, 4, 19, 10, 0), 13.1, 66.0, 16.8, 24.9, 28.2, 30.7, 69, "Stable urban background conditions."),
    ]

    observations = [
        models.Observation(
            station_id=station_id,
            observed_at=observed_at,
            temperature_c=temperature_c,
            humidity_pct=humidity_pct,
            pm25=pm25,
            pm10=pm10,
            no2=no2,
            o3=o3,
            aqi=aqi,
            notes=notes,
        )
        for station_id, observed_at, temperature_c, humidity_pct, pm25, pm10, no2, o3, aqi, notes in sample_rows
    ]
    db.add_all(observations)
    db.commit()
    return schemas.SeedSummary(stations_created=len(stations), observations_created=len(observations))
