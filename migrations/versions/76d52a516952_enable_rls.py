"""enable rls

Revision ID: 76d52a516952
Revises: 4a711c3aa865
Create Date: 2026-09-23 18:34:53.403019

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '76d52a516952'
down_revision: Union[str, None] = '4a711c3aa865'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table in ("documents",):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"""
            CREATE POLICY tenant_isolation ON {table}
            USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
            WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid)
        """)

def downgrade() -> None:
    for table in ("documents",):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")