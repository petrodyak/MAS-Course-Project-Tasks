"""Add businesses table.

Creates `businesses` with FK to `city(id)` and NOT NULL city_id.
"""

revision = "add_businesses_table"
down_revision = "add_transport_and_station_tables"
branch_labels = None
depends_on = None


def upgrade():
    from alembic import op

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS businesses (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          type TEXT NOT NULL,
          city_id INTEGER NOT NULL,
          description TEXT NULL,
          established_year TEXT NULL,
          CONSTRAINT fk_businesses_city_id FOREIGN KEY(city_id) REFERENCES city(id) ON DELETE CASCADE
        );
        """
    )

    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_businesses_city_id ON businesses(city_id);"
    )


def downgrade():
    from alembic import op

    op.execute("DROP TABLE IF EXISTS businesses")
