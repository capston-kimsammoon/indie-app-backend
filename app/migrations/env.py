import os
import sys
from dotenv import load_dotenv
# from logging.config import fileConfig  # ← 사용 안 함

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
load_dotenv(os.path.join(BASE_DIR, '.env'))
load_dotenv(os.path.join(BASE_DIR, 'app', '.env'))  # app/.env 도 허용(있으면)

sys.path.insert(0, BASE_DIR)

from alembic import context
from sqlalchemy import engine_from_config, pool

from app import models  # noqa: F401  (메타데이터 로딩을 위해 import 유지)
from app.database import Base
from app.config import settings

DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_NAME = settings.DB_NAME
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD

config = context.config
config.set_main_option(
    "sqlalchemy.url",
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

# ✅ alembic.ini 로깅 설정이 없어서 fileConfig 호출을 제거/무시합니다.
# if config.config_file_name is not None:
#     try:
#         fileConfig(config.config_file_name)
#     except Exception:
#         pass  # 로깅 설정 없어도 진행

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
