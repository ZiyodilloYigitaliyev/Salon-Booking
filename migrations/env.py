# migrations/env.py
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# --- SQLAlchemy metadata ---
from app.db.base import Base  # Base.metadata ga barcha modellaring ulangan bo'lsin
# Masalan, modellaringni yonma-yon import qilib, registratsiya qilib qo'y:
# from app.models import student, teacher, attendance  # noqa: F401

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _normalize_db_url(url: str) -> str:
    """Heroku URL'ini SQLAlchemy 2.x va prod uchun moslashtirish."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    if "sslmode=" not in url:
        url += ("&" if "?" in url else "?") + "sslmode=require"
    return url


# --- DATABASE_URL ni ENV dan o'qish va normallashtirish ---
db_url = os.getenv("DATABASE_URL", "")
if not db_url:
    raise RuntimeError("DATABASE_URL topilmadi. Heroku Config Vars ni tekshiring.")

db_url = _normalize_db_url(db_url)
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    """Offline rejim: connection ochmasdan skript generatsiya qiladi."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Online rejim: real connection bilan migration bajaradi."""
    # Heroku/RDS uchun xavfsizroq sozlamalar
    engine_opts = dict(
        pool_pre_ping=True,         # o'lik connectionlarni tozalaydi
        poolclass=pool.NullPool,    # Heroku ephemeral, pool siz ham yashaysan
    )

    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        **engine_opts,
    )

    with connectable.connect() as connection:
        # (ixtiyoriy) vaqt cheklovlari — katta lock'larda osilib qolmasin
        try:
            connection.exec_driver_sql("SET statement_timeout = '120s'")
            connection.exec_driver_sql("SET lock_timeout = '15s'")
        except Exception:
            # Ba'zi managed RDS'larda SET ruxsati bo'lmasligi mumkin — e'tibor bermaymiz
            pass

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
