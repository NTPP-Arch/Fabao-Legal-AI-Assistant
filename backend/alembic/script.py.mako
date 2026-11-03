"""Alembic 迁移脚本模板。"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """执行升级迁移。"""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """执行回滚迁移。"""
    ${downgrades if downgrades else "pass"}
