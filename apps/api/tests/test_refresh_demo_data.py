import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Category, Event, Location
from app.refresh import refresh_demo_data


def test_refresh_demo_data_recreates_seed_data():
    engine = create_engine("sqlite://")
    if engine.dialect.name == "sqlite":
        pytest.skip("GeoAlchemy geometry tables require a spatial database such as Postgres/PostGIS; SQLite cannot execute RecoverGeometryColumn.")

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        count = refresh_demo_data(session)
        assert count > 0
        assert session.query(Event).count() > 0
        assert session.query(Category).count() > 0
        assert session.query(Location).count() > 0

        second_count = refresh_demo_data(session)
        assert second_count == count
