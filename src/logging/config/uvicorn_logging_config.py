import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime

from src.core.settings import settings
from src.logging.formatter.formatter_strategies import FormatterFactory


class UvicornLoggingConfig:
    """
    uvicorn.access / uvicorn.error 로그를 도메인 로그 스타일처럼 남기는 설정자입니다.
    logs/{env}/uvicorn/access-YYYY-MM-DD.log 형식으로 기록합니다.
    """

    def __init__(self):
        # 현재 실행 환경 (예: dev, staging, production)
        self.env = settings.APP_ENV
        # 로그 파일 저장 경로: logs/{env}/uvicorn/
        self.log_root = Path(settings.LOG_DIR) / self.env / "uvicorn"
        self.log_root.mkdir(parents=True, exist_ok=True)  # 디렉터리 미존재 시 생성
        # 로그 레벨 (예: INFO, DEBUG 등)
        self.log_level = settings.LOG_LEVEL.upper()
        # 로그 포맷터 설정 (uvicorn 로그는 항상 text 포맷 사용)
        self.formatter = FormatterFactory.create("text").get_formatter()

    def configure(self):
        # 오늘 날짜 문자열 (로그 파일명에 포함)
        today = datetime.now().strftime("%Y-%m-%d")

        # access / error 로그 파일 경로 정의
        access_log_path = self.log_root / f"access-{today}.log"
        error_log_path = self.log_root / f"error-{today}.log"

        # ------------------------------
        # uvicorn.access 로그 설정
        # ------------------------------
        access_logger = logging.getLogger("uvicorn.access")
        access_logger.setLevel(self.log_level)     # 로그 레벨 설정
        access_logger.propagate = False            # 상위 로거로 로그 전파 방지

        # 이미 파일 핸들러가 붙어있지 않다면 추가
        if not self._has_file_handler(access_logger):
            access_handler = TimedRotatingFileHandler(
                filename=access_log_path,         # 로그 파일 경로
                when="midnight",                  # 자정마다 로그 회전
                interval=1,                       # 1일 단위
                backupCount=30,                   # 최대 30개 백업 파일 보관
                encoding="utf-8"
            )
            access_handler.setFormatter(self.formatter)  # 포맷터 적용
            access_logger.addHandler(access_handler)     # 핸들러 추가

        # ------------------------------
        # uvicorn.error 로그 설정
        # ------------------------------
        error_logger = logging.getLogger("uvicorn.error")
        error_logger.setLevel("ERROR")
        error_logger.propagate = False

        if not self._has_file_handler(error_logger):
            error_handler = TimedRotatingFileHandler(
                filename=error_log_path,
                when="midnight",
                interval=1,
                backupCount=30,
                encoding="utf-8"
            )
            error_handler.setFormatter(self.formatter)
            error_logger.addHandler(error_handler)

    @staticmethod
    def _has_file_handler(logger: logging.Logger) -> bool:
        """
        주어진 로거에 이미 FileHandler가 존재하는지 확인하여
        중복 핸들러 등록을 방지함.
        """
        return any(isinstance(h, logging.FileHandler) for h in logger.handlers)
