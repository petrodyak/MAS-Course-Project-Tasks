from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="City Table API")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
