"""initial schema

Revision ID: 20260919_01
Revises:
Create Date: 2026-09-19 13:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20260919_01'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. pulse_executions
    op.create_table(
        'pulse_executions',
        sa.Column('execution_id', sa.String(), primary_key=True),
        sa.Column('started_at', sa.DateTime(timezone=True), index=True),
        sa.Column('finished_at', sa.DateTime(timezone=True)),
        sa.Column('duration_ms', sa.Integer()),
        sa.Column('market_status', sa.String()),
        sa.Column('status', sa.String())
    )

    # 2. live_signals (Complete V2.2 Schema)
    op.create_table(
        'live_signals',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('symbol', sa.String(), index=True),
        sa.Column('direction', sa.String()),
        sa.Column('status', sa.String()),
        sa.Column('entry_price', sa.Float()),
        sa.Column('target_price', sa.Float()),
        sa.Column('stop_price', sa.Float()),
        sa.Column('conviction', sa.Float()),
        sa.Column('timestamp', sa.DateTime(timezone=True)),
        sa.Column('strategy_version', sa.String()),
        sa.Column('realized_mae', sa.Float()),
        sa.Column('realized_mfe', sa.Float()),
        sa.Column('timeframe', sa.String()),
        sa.Column('regime', sa.String()),
        sa.Column('expected_value', sa.Float()),
        sa.Column('calibrated_probability', sa.Float()),
        sa.Column('deployment_sha', sa.String(), nullable=True)
    )

    # 3. shadow_signals (Complete V2.2 Schema)
    op.create_table(
        'shadow_signals',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('symbol', sa.String(), index=True),
        sa.Column('direction', sa.String()),
        sa.Column('status', sa.String()),
        sa.Column('entry_price', sa.Float()),
        sa.Column('target_price', sa.Float()),
        sa.Column('stop_price', sa.Float()),
        sa.Column('strategy_version', sa.String()),
        sa.Column('timestamp', sa.DateTime(timezone=True)),
        sa.Column('realized_mae', sa.Float()),
        sa.Column('realized_mfe', sa.Float()),
        sa.Column('signal_type', sa.String()),
        sa.Column('regime', sa.String()),
        sa.Column('expected_value', sa.Float()),
        sa.Column('calibrated_probability', sa.Float()),
        sa.Column('deployment_sha', sa.String(), nullable=True)
    )

def downgrade() -> None:
    op.drop_table('shadow_signals')
    op.drop_table('live_signals')
    op.drop_table('pulse_executions')
