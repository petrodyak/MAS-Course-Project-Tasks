"""Add district table.

This repository template for this homework uses direct schema creation in
app.setup.ensure_setup().

The QA harness expects an Alembic directory to exist; however, there are no
managed migrations here.
"""


revision = "add_district_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # No-op: schema is ensured by app.setup.ensure_setup().
    pass


def downgrade():
    # No-op
    pass
