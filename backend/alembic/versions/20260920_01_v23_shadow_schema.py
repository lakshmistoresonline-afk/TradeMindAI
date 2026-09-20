"""v23 shadow schema

Revision ID: 20260920_01
Revises: 20260919_01
Create Date: 2026-09-20 10:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20260920_01'
down_revision: Union[str, None] = '20260919_01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Create signal_shadow_decisions table
    op.create_table(
        'signal_shadow_decisions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('signal_id', sa.String(), index=True),
        sa.Column('candidate_id', sa.String(), index=True),
        sa.Column('current_engine', sa.String()),
        sa.Column('shadow_engine', sa.String()),
        sa.Column('current_decision', sa.String()),
        sa.Column('shadow_decision', sa.String()),
        sa.Column('current_probability', sa.Float()),
        sa.Column('shadow_probability', sa.Float()),
        sa.Column('current_ev', sa.Float()),
        sa.Column('shadow_ev', sa.Float()),
        sa.Column('current_entry', sa.Float()),
        sa.Column('shadow_entry', sa.Float()),
        sa.Column('current_stop', sa.Float()),
        sa.Column('shadow_stop', sa.Float()),
        sa.Column('current_target', sa.Float()),
        sa.Column('shadow_target', sa.Float()),
        sa.Column('current_regime', sa.String()),
        sa.Column('shadow_regime', sa.String()),
        sa.Column('gate_result', sa.JSON()),
        sa.Column('block_reason', sa.String()),
        sa.Column('rsi_result', sa.Float()),
        sa.Column('data_status', sa.String()),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('evaluation_timestamp', sa.DateTime(timezone=True)),
        sa.Column('record_hash', sa.String())
    )

    # 2. Add instrumentation columns to live_signals
    op.add_column('live_signals', sa.Column('candidate_timestamp', sa.DateTime(timezone=True), nullable=True))
    op.add_column('live_signals', sa.Column('published_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('live_signals', sa.Column('price_at_signal', sa.Float(), nullable=True))
    op.add_column('live_signals', sa.Column('price_at_publish', sa.Float(), nullable=True))
    op.add_column('live_signals', sa.Column('price_at_activation', sa.Float(), nullable=True))
    op.add_column('live_signals', sa.Column('regime_timestamp', sa.DateTime(timezone=True), nullable=True))
    op.add_column('live_signals', sa.Column('regime_source', sa.String(), nullable=True))
    op.add_column('live_signals', sa.Column('regime_confidence', sa.Float(), nullable=True))
    op.add_column('live_signals', sa.Column('regime_available', sa.Boolean(), server_default='false'))

def downgrade() -> None:
    op.drop_column('live_signals', 'regime_available')
    op.drop_column('live_signals', 'regime_confidence')
    op.drop_column('live_signals', 'regime_source')
    op.drop_column('live_signals', 'regime_timestamp')
    op.drop_column('live_signals', 'price_at_activation')
    op.drop_column('live_signals', 'price_at_publish')
    op.drop_column('live_signals', 'price_at_signal')
    op.drop_column('live_signals', 'published_at')
    op.drop_column('live_signals', 'candidate_timestamp')
    op.drop_table('signal_shadow_decisions')
