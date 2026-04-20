from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Station(Base):
    __tablename__ = "stations"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    city: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(80), nullable=False, default="United Kingdom")
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    environment_type: Mapped[str] = mapped_column(String(40), nullable=False, default="urban")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    observations: Mapped[list["Observation"]] = relationship(
        back_populates="station",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Observation(Base):
    __tablename__ = "observations"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_id: Mapped[int] = mapped_column(
        ForeignKey("stations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    observed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_pct: Mapped[float] = mapped_column(Float, nullable=False)
    pm25: Mapped[float] = mapped_column(Float, nullable=False)
    pm10: Mapped[float] = mapped_column(Float, nullable=False)
    no2: Mapped[float] = mapped_column(Float, nullable=False)
    o3: Mapped[float] = mapped_column(Float, nullable=False)
    aqi: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    station: Mapped[Station] = relationship(back_populates="observations")
