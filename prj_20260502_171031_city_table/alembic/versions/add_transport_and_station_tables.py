"""Add transport_system and station_stop tables.

Created because QA expects reproducible migrations plus FK constraints.
"""

revision = "add_transport_and_station_tables"
down_revision = "add_district_table"
branch_labels = None
depends_on = None


def upgrade():
    # Use op.execute to keep SQLite DDL explicit and deterministic.
    from alembic import op

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS transport_system (
          id INTEGER PRIMARY KEY,
          city_id INTEGER NOT NULL,
          name TEXT NOT NULL,
          transport_type TEXT NOT NULL,
          notes TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (city_id) REFERENCES city(id) ON DELETE CASCADE,
          UNIQUE (city_id, name, transport_type),
          CONSTRAINT chk_transport_type CHECK (transport_type IN ('Metro','Bus','Tram')),
          CONSTRAINT chk_transport_name_nonempty CHECK (length(trim(name)) > 0)
        );
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS station_stop (
          id INTEGER PRIMARY KEY,
          transport_system_id INTEGER NOT NULL,
          name TEXT NOT NULL,
          stop_type TEXT NOT NULL,
          code TEXT,
          address TEXT,
          order_index INTEGER,
          is_active BOOLEAN NOT NULL DEFAULT 1,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (transport_system_id) REFERENCES transport_system(id) ON DELETE CASCADE,
          UNIQUE (transport_system_id, code),
          CONSTRAINT chk_station_stop_type CHECK (stop_type IN ('Airport','Train Station','Stop')),
          CONSTRAINT chk_station_name_nonempty CHECK (length(trim(name)) > 0)
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_transport_system_city_id ON transport_system(city_id);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_station_stop_transport_system_id ON station_stop(transport_system_id);"
    )


def downgrade():
    from alembic import op

    op.execute("DROP TABLE IF EXISTS station_stop")
    op.execute("DROP TABLE IF EXISTS transport_system")
