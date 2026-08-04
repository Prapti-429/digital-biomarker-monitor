import os
import pathlib

# Ensure alembic/versions exists
pathlib.Path("alembic/versions").mkdir(parents=True, exist_ok=True)

# 1. Write alembic.ini
ini_content = """[alembic]
script_location = alembic
file_template = %%(year)d_%%(month)02d_%%(day)02d_%%(hour)02d%%(minute)02d-%%(rev)s_%%(slug)s
prepend_sys_path = .
timezone = UTC
truncate_slug_length = 40
sqlalchemy.url = postgresql+psycopg://postgres:postgres@localhost:5432/digital_biomarker_db

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

pathlib.Path("alembic.ini").write_text(ini_content, encoding="utf-8")

# 2. Write alembic/script.py.mako
mako_content = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma_joins_quoted}
Create Date: ${create_date}

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}

def upgrade() -> None:
    ${upgrades if upgrades else "pass"}

def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''

pathlib.Path("alembic/script.py.mako").write_text(mako_content, encoding="utf-8")

print("✅ Alembic configuration files generated successfully!")