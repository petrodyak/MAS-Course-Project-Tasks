"""Initial schema: rooms, shelves, books

Revision ID: 001
Revises:
Create Date: 2026-05-04 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rooms",
        sa.Column("room_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("room_name", sa.String(length=255), nullable=False),
        sa.Column("room_description", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("room_id"),
    )
    op.create_table(
        "shelves",
        sa.Column("shelf_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("shelf_name", sa.String(length=255), nullable=False),
        sa.Column("shelf_code", sa.String(length=255), nullable=False),
        sa.Column("shelf_description", sa.Text(), nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.room_id"]),
        sa.PrimaryKeyConstraint("shelf_id"),
    )
    op.create_table(
        "books",
        sa.Column("book_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("book_title", sa.String(length=255), nullable=False),
        sa.Column("book_author", sa.String(length=255), nullable=False),
        sa.Column("book_isbn", sa.String(length=32), nullable=False),
        sa.Column("book_genre", sa.String(length=100), nullable=False),
        sa.Column("book_publication_year", sa.Integer(), nullable=False),
        sa.Column("book_language", sa.String(length=50), nullable=False),
        sa.Column("book_status", sa.String(length=50), nullable=False),
        sa.Column("shelf_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["shelf_id"], ["shelves.shelf_id"]),
        sa.PrimaryKeyConstraint("book_id"),
    )


def downgrade() -> None:
    op.drop_table("books")
    op.drop_table("shelves")
    op.drop_table("rooms")
