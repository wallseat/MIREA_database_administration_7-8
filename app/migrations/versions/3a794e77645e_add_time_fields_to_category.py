"""add time fields to category

Revision ID: 3a794e77645e
Revises: ecf95befe18f
Create Date: 2023-05-13 13:18:22.736975

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3a794e77645e"
down_revision = "ecf95befe18f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "category",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        schema="shopper",
    )
    op.add_column(
        "category",
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        schema="shopper",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("category", "updated_at", schema="shopper")
    op.drop_column("category", "created_at", schema="shopper")
    # ### end Alembic commands ###
