from __future__ import annotations

from fastapi import FastAPI

from app.city_business_controller import CityBusinessController

app = FastAPI(title="City Table API")


def _get_controller() -> CityBusinessController:
    # For this homework-style project we keep db_path in artifacts/data paths.
    # The test suite operates directly on sqlite.
    from pathlib import Path

    db_path = Path(__file__).resolve().parents[1] / "data" / "app.db"
    return CityBusinessController(str(db_path))


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/cities/{city_id}/businesses")
def post_business(city_id: int, payload: dict) -> dict:
    controller = _get_controller()
    return controller.post_business_for_city(
        city_id=city_id,
        name=payload["name"],
        type=payload["type"],
        description=payload.get("description"),
        established_year=payload.get("established_year"),
    )


@app.get("/cities/{city_id}/businesses")
def get_businesses(city_id: int) -> list[dict]:
    controller = _get_controller()
    return controller.get_businesses_for_city(city_id)
