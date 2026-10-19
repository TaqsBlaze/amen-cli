"""Framework-specific database and migration templates."""


def get_database_templates(
    app_name: str, framework: str, database: str
) -> dict[str, str]:
    """Return database files keyed by their paths relative to the project root."""
    if framework not in {"flask", "fastapi"}:
        raise ValueError(f"Unsupported framework: {framework}")
    if database not in {"sqlite3", "mysql"}:
        raise ValueError(f"Unsupported database: {database}")

    default_url = (
        f"sqlite:///instance/{app_name}.db"
        if database == "sqlite3"
        else f"mysql+pymysql://root@localhost:3306/{app_name}"
    )
    database_content = f'''"""Database configuration for {app_name}."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
url = make_url(os.getenv("DATABASE_URL", {default_url!r}))

# Keep relative SQLite locations independent of the working directory.
if url.get_backend_name() == "sqlite" and url.database not in (None, "", ":memory:"):
    database_path = Path(url.database)
    if not database_path.is_absolute():
        database_path = PROJECT_ROOT / database_path
    database_path.parent.mkdir(parents=True, exist_ok=True)
    url = url.set(database=database_path.as_posix())

DATABASE_URL = url.render_as_string(hide_password=False)
'''
    if framework == "fastapi":
        database_content += '''
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Base class shared by application models and migration metadata."""


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if url.get_backend_name() == "sqlite" else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    """Yield a request-scoped database session and always close it."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
'''
        base_import = f"from {app_name}.database import Base"
    else:
        base_import = f"from {app_name} import db\n\nBase = db.Model"

    model_content = f'''"""Application database models."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

{base_import}


def utc_now():
    """Compute a fresh UTC timestamp for each inserted row."""
    return datetime.now(timezone.utc)


class Users(Base):
    """A starter user record; passwords must contain application-generated hashes."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(100), nullable=False, index=True)
    lastname = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    role = Column(String(255), nullable=False, default="user", index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True))
'''
    files = {
        f"{app_name}/database.py": database_content,
        f"{app_name}/models/models.py": model_content,
        f"{app_name}/models/__init__.py": "from .models import Users\n",
    }
    if framework == "fastapi":
        files.update(_get_alembic_templates(app_name))
    return files


def _get_alembic_templates(app_name: str) -> dict[str, str]:
    env_content = f'''"""Use application configuration and model metadata for migrations."""

from alembic import context

from {app_name}.database import Base, DATABASE_URL, engine
from {app_name}.models import Users


def run_migrations_offline():
    """Render migrations as SQL without opening a database connection."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=Base.metadata,
        literal_binds=True,
        render_as_batch=engine.dialect.name == "sqlite",
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Apply migrations using the application's engine and registered models."""
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            render_as_batch=engine.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
    return {
        "alembic.ini": (
            "[alembic]\n"
            "script_location = %(here)s/migrations\n"
            "prepend_sys_path = %(here)s\n"
            "path_separator = os\n"
        ),
        "migrations/env.py": env_content,
        "migrations/versions/.gitkeep": "",
        "migrations/script.py.mako": '''"""${message}"""

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    """Apply this revision."""
    ${upgrades if upgrades else "pass"}


def downgrade():
    """Revert this revision."""
    ${downgrades if downgrades else "pass"}
''',
    }
