"""Add push_tokens table

Revision ID: 002_add_push_tokens
Revises: 001_initial_migration
Create Date: 2025-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_push_tokens'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create push_tokens table
    op.create_table(
        'push_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(500), nullable=False),
        sa.Column('platform', sa.String(20), nullable=False),
        sa.Column('device_id', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes
    op.create_index('idx_push_token_user_active', 'push_tokens', ['user_id', 'is_active'])
    op.create_index('idx_push_token_platform', 'push_tokens', ['platform'])
    op.create_index('ix_push_tokens_id', 'push_tokens', ['id'])
    op.create_index('ix_push_tokens_user_id', 'push_tokens', ['user_id'])
    op.create_index('ix_push_tokens_token', 'push_tokens', ['token'], unique=True)
    op.create_index('ix_push_tokens_is_active', 'push_tokens', ['is_active'])
    op.create_index('ix_push_tokens_created_at', 'push_tokens', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_push_tokens_created_at', table_name='push_tokens')
    op.drop_index('ix_push_tokens_is_active', table_name='push_tokens')
    op.drop_index('ix_push_tokens_token', table_name='push_tokens')
    op.drop_index('ix_push_tokens_user_id', table_name='push_tokens')
    op.drop_index('ix_push_tokens_id', table_name='push_tokens')
    op.drop_index('idx_push_token_platform', table_name='push_tokens')
    op.drop_index('idx_push_token_user_active', table_name='push_tokens')

    # Drop table
    op.drop_table('push_tokens')
