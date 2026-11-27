
"""add agent key hash to servers

Revision ID: 0bb88ca707ba
Revises: 1ebef97417fa
"""

from alembic import op
import sqlalchemy as sa


revision = "0bb88ca707ba"
down_revision = "1ebef97417fa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "servers",
        sa.Column(
            "agent_key_hash",
            sa.String(length=64),
            nullable=True,
        ),
    )

    op.create_unique_constraint(
        "uq_servers_agent_key_hash",
        "servers",
        ["agent_key_hash"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_servers_agent_key_hash",
        "servers",
        type_="unique",
    )

    op.drop_column(
        "servers",
        "agent_key_hash",
    )
