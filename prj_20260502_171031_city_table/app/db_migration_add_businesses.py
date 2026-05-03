from __future__ import annotations

"""Business schema migration helpers.

This repository mostly bootstraps schema via app.setup.ensure_setup().
We still provide an Alembic migration module expected by the task pipeline.
"""


BUSINESSES_DDL = """
CREATE TABLE IF NOT EXISTS businesses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  city_id INTEGER NOT NULL,
  description TEXT NULL,
  established_year TEXT NULL,
  CONSTRAINT fk_businesses_city_id FOREIGN KEY(city_id) REFERENCES city(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_businesses_city_id ON businesses(city_id);
"""
