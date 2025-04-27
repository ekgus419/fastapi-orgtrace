from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.settings import settings
from src.logging.extensions.sql_query_logging import SqlQueryLogging

DATABASE_URL = (
    f"mysql+mysqldb://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
    f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=10,     # 풀 크기 10
    max_overflow=20,  # 최대 오버플로우 20
    pool_timeout=30,  # 타임아웃 30초
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 슬로우 쿼리 및 일반 쿼리 로깅 리스너 등록
sql_logger = SqlQueryLogging()
sql_logger.register_listeners(engine)
sql_logger.register_session_listeners(SessionLocal)
