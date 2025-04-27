from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 기본 환경 설정
    APP_ENV: str = "development"  # development, production 구분용
    LOG_FORMAT: str = "json"      # "text" 또는 "json"
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    LOG_TO_CONSOLE: bool = True

    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DB: str = "rms"
    SLOW_QUERY_THRESHOLD: float = 2.0

    # JWT 관련 설정
    JWT_SECRET: str = "your_jwt_secret_here"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1
    JWT_REFRESH_EXPIRATION_MINUTES: int = 1440

    class Config:
        # 순서대로 로드되며, 이후 파일의 값이 우선합니다.
        env_file = [
            "src/env/.env.common",
            "src/env/.env.dev",  # 개발 서버일 경우 사용됨
            # 운영 시에는 여기 대신 .env.prod를 추가할 예정
        ]


settings = Settings()
