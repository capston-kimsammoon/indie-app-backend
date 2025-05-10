# import os
# import sys
# from dotenv import load_dotenv
# from logging.config import fileConfig

# # 프로젝트 루트를 sys.path에 추가 (절대 경로 사용)
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# from sqlalchemy import engine_from_config, pool
# from alembic import context
# from app.database import Base

# # .env 파일 로드
# load_dotenv()

# # .env 파일에서 데이터베이스 연결 정보 불러오기
# DB_HOST = os.getenv('DB_HOST', 'localhost')
# DB_PORT = os.getenv('DB_PORT', '3306')
# DB_USER = os.getenv('DB_USER', 'root')
# DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
# DB_NAME = os.getenv('DB_NAME', 'mydatabase')

# # Alembic config 가져오기
# config = context.config

# # sqlalchemy.url을 동적으로 설정
# config.set_main_option('sqlalchemy.url', f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# # 모델 Base 객체 불러오기
# target_metadata = Base.metadata

# # Logging 설정
# # if config.config_file_name is not None:
#     # fileConfig(config.config_file_name)

# # 'offline' 모드에서 실행하는 함수
# def run_migrations_offline() -> None:
#     """Run migrations in 'offline' mode."""
#     context.configure(
#         url=config.get_main_option("sqlalchemy.url"),
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#     )

#     with context.begin_transaction():
#         context.run_migrations()


# # 'online' 모드에서 실행하는 함수
# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode."""
#     connectable = engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )

#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection, target_metadata=target_metadata
#         )

#         with context.begin_transaction():
#             context.run_migrations()


# # 'offline' 또는 'online' 모드로 구분하여 실행
# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()
