# migrations/env.py
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# --- SQLAlchemy metadata ---
# Eslatma: barcha modellaring import bo'lsin, aks holda autogenerate topa olmaydi
from app.db.base import Base  # bu yerda Base metadata jamlanadi
# masalan: from app.models import student, teacher, attendance, ...  # noqa: F401

# Alembic Config obyektini o'qish (alembic.ini)
config = context.config

# Log konfiguratsiya (config.ini bo'lsa)
if config.config_file_name:
    fileConfig(config.config_file_name)

# Migrationlar uchun target metadata
target_metadata = Base.metadata

# --- DATABASE_URL ni ENV dan o'qish va normallashtirish ---
db_url = os.getenv("DATABASE_URL", "")
if db_url.startswith("postgres://"):
    # SQLAlchemy 2.x 'postgres' nomli dialektni tan olmaydi
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)

if not db_url:
    raise RuntimeError(
        "DATABASE_URL topilmadi. Heroku Config Vars ni tekshiring."
    )

# alembic.ini ichidagi sqlalchemy.url ustiga yozamiz
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    """
    Offline rejim: connection ochmasdan skript generatsiya qiladi.
    """
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,      # ustun turlarini ham solishtir
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Online rejim: real connection bilan migration bajaradi.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
