"""add cascade delete to token foreign keys

Revision ID: eb030e9e4708
Revises: d1f59698ef84
Create Date: 2026-08-26 17:19:36.030078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb030e9e4708'
down_revision = 'd1f59698ef84'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('email_verification_tokens', schema=None) as batch_op:
        batch_op.drop_constraint('email_verification_tokens_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'email_verification_tokens_user_id_fkey', 'users', ['user_id'], ['id'], ondelete='CASCADE'
        )
    with op.batch_alter_table('password_reset_tokens', schema=None) as batch_op:
        batch_op.drop_constraint('password_reset_tokens_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'password_reset_tokens_user_id_fkey', 'users', ['user_id'], ['id'], ondelete='CASCADE'
        )


def downgrade():
    with op.batch_alter_table('password_reset_tokens', schema=None) as batch_op:
        batch_op.drop_constraint('password_reset_tokens_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'password_reset_tokens_user_id_fkey', 'users', ['user_id'], ['id']
        )
    with op.batch_alter_table('email_verification_tokens', schema=None) as batch_op:
        batch_op.drop_constraint('email_verification_tokens_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'email_verification_tokens_user_id_fkey', 'users', ['user_id'], ['id']
        )