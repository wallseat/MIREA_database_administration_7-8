"""add unique

Revision ID: ecf95befe18f
Revises: f245daf5f54f
Create Date: 2023-05-03 20:28:20.909071

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "ecf95befe18f"
down_revision = "f245daf5f54f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(
        op.f("uq__user__email"),
        "user",
        ["email"],
        schema="shopper",
    )
    op.create_unique_constraint(
        op.f("uq__user__username"),
        "user",
        ["username"],
        schema="shopper",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        op.f("uq__user__username"),
        "user",
        schema="shopper",
        type_="unique",
    )
    op.drop_constraint(
        op.f("uq__user__email"),
        "user",
        schema="shopper",
        type_="unique",
    )
    # ### end Alembic commands ###
