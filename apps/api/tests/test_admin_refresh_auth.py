from fastapi import HTTPException

from app.config import settings
from app.routers.events import refresh_db


def test_refresh_db_rejects_invalid_admin_token(monkeypatch):
    monkeypatch.setattr(settings, "admin_refresh_token", "secret-token")

    try:
        refresh_db(db=None, x_admin_token="wrong-token")  # type: ignore[arg-type]
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        raise AssertionError("Expected HTTPException")
