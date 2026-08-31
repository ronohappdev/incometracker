"""Add benchmark salary history and adjustments."""

import sqlalchemy as sa
from alembic import op

revision = "0002_benchmark_history"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "benchmark_salary_history",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "benchmark_profile_id",
            sa.String(36),
            sa.ForeignKey("benchmark_profiles.id"),
            nullable=False,
        ),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("monthly_income", sa.Numeric(14, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("monthly_income > 0", name="ck_salary_history_monthly_income_positive"),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_salary_history_date_order",
        ),
    )
    op.create_index(
        "ix_benchmark_salary_history_benchmark_profile_id",
        "benchmark_salary_history",
        ["benchmark_profile_id"],
    )
    op.create_table(
        "benchmark_adjustments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "benchmark_profile_id",
            sa.String(36),
            sa.ForeignKey("benchmark_profiles.id"),
            nullable=False,
        ),
        sa.Column("adjustment_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("adjustment_type", sa.String(40), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("amount != 0", name="ck_benchmark_adjustment_amount_nonzero"),
    )
    op.create_index(
        "ix_benchmark_adjustments_benchmark_profile_id",
        "benchmark_adjustments",
        ["benchmark_profile_id"],
    )
    op.create_index(
        "ix_benchmark_adjustments_adjustment_date",
        "benchmark_adjustments",
        ["adjustment_date"],
    )


def downgrade():
    op.drop_table("benchmark_adjustments")
    op.drop_table("benchmark_salary_history")
