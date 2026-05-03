from __future__ import annotations

from alembic import op


revision = "215235d6district"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS District (
            district_id TEXT NOT NULL PRIMARY KEY DEFAULT (lower(hex(randomblob(16))) || '-' || substr(lower(hex(randomblob(16))), 1, 4) || '-' || substr(lower(hex(randomblob(16))), 1, 4) || '-' || substr(lower(hex(randomblob(16))), 1, 4) || '-' || substr(lower(hex(randomblob(16))), 1, 12)),
            city_id      TEXT NOT NULL,
            name         TEXT NOT NULL,
            code         TEXT NULL,
            type         TEXT NOT NULL CHECK (type IN ('urban','suburban','industrial','rural')),
            status       TEXT NOT NULL CHECK (status IN ('active','merged','deprecated')),
            CONSTRAINT fk_district_city
                FOREIGN KEY (city_id) REFERENCES cities(CityId) ON DELETE RESTRICT
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_district_city_id ON District(city_id);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_district_status ON District(status);"
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_district_type ON District(type);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS District")
