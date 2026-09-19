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
    # 1. Create Pulse Executions table if not exists
    op.create_table(
        'pulse_executions',
        sa.Column('execution_id', sa.String(), primary_key=True),
        sa.Column('started_at', sa.DateTime(timezone=True), index=True),
        sa.Column('finished_at', sa.DateTime(timezone=True)),
        sa.Column('duration_ms', sa.Integer()),
        sa.Column('market_status', sa.String()),
        sa.Column('lock_acquired', sa.Boolean()),
        sa.Column('deployment_sha', sa.String()),
        sa.Column('signals_seen', sa.Integer()),
        sa.Column('signals_processed', sa.Integer()),
        sa.Column('signals_updated', sa.Integer()),
        sa.Column('signals_skipped', sa.Integer()),
        sa.Column('signals_failed', sa.Integer()),
        sa.Column('fresh_count', sa.Integer()),
        sa.Column('aging_count', sa.Integer()),
        sa.Column('stale_count', sa.Integer()),
        sa.Column('unavailable_count', sa.Integer()),
        sa.Column('lifecycle_transitions', sa.Integer()),
        sa.Column('error_count', sa.Integer()),
        sa.Column('last_error', sa.String()),
        sa.Column('status', sa.String())
    )

    # 2. Add deployment_sha to signals
    op.add_column('live_signals', sa.Column('deployment_sha', sa.String(), nullable=True))
    op.add_column('shadow_signals', sa.Column('deployment_sha', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('shadow_signals', 'deployment_sha')
    op.drop_column('live_signals', 'deployment_sha')
    op.drop_table('pulse_executions')
