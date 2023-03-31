"""create user table

Revision ID: 5cc015257e8b
Revises: 
Create Date: 2022-08-03 01:55:41.590039

"""
from uuid import uuid4
from alembic import op
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5cc015257e8b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create student table
    op.create_table(
        "student",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("department", sa.String(200)),
        sa.Column("year", sa.Integer),
    )

    # Create teacher table
    op.create_table(
        "teacher",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("department", sa.String(200)),
        sa.Column("subject", sa.Integer),
    )


def downgrade() -> None:
    op.drop_table("student")
    op.drop_table("teacher")
