import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime
import sys

from src.core.settings import settings
from src.logging.formatter.formatter_strategies import FormatterFactory


class LoggingConfig:
    """
    환경별로 도메인 기반 로거를 생성하고,
    설정에 따라 콘솔/파일 핸들러를 분리해 적용하는 로깅 설정 클래스입니다.
    """

    def __init__(self):
        # 현재 실행 환경 (예: dev, prod 등)
        self.env = settings.APP_ENV
        # 로그 레벨을 대문자로 표준화하여 설정
        self.log_level = settings.LOG_LEVEL.upper()
        # 로그 파일이 저장될 루트 디렉터리
        self.log_root = Path(settings.LOG_DIR) / self.env
        # 파일 로그 포매터 (json, text 등 전략 기반)
        self.formatter = FormatterFactory.create(settings.LOG_FORMAT).get_formatter()
        # 콘솔 출력 포매터
        self.console_formatter = FormatterFactory.create_console().get_formatter()
        # 이미 생성된 로거 캐시
        self._loggers: dict[str, logging.Logger] = {}

    def get_logger(self, name: str, level: int | None = None, subdir: bool = True) -> logging.Logger:
        """
        도메인 이름을 기준으로 로거를 반환하거나 새로 생성합니다.

        Args:
            name (str): 로거의 이름 (보통 도메인명)
            level (int | None): 로그 레벨 (지정하지 않으면 기본 설정값 사용)
            subdir (bool): 해당 도메인용 하위 디렉터리 생성 여부

        Returns:
            logging.Logger: 설정된 로거 인스턴스
        """
        # 이미 캐싱된 로거가 있다면 재사용
        if name in self._loggers:
            return self._loggers[name]

        # 신규 로거 설정 및 등록
        logger = self._setup_logger(name, level or self.log_level, subdir)
        self._loggers[name] = logger
        return logger

    def _setup_logger(self, name: str, level: int | str, subdir: bool) -> logging.Logger:
        """
        로거에 파일 핸들러 및 콘솔 핸들러를 구성하는 내부 메서드입니다.

        Args:
            name (str): 로거 이름
            level (int | str): 로그 레벨
            subdir (bool): 하위 폴더 생성 여부

        Returns:
            logging.Logger: 구성된 로거 객체
        """
        # 날짜별 로그 파일 이름 지정
        today = datetime.now().strftime("%Y-%m-%d")

        # _history 접미사가 있으면 원래 도메인으로 치환하여 확인
        dir_name = name
        if name.endswith("_history"):
            dir_name = name.replace("_history", "")

        # 디렉토리 기준은 dir_name, 파일명은 원래 name
        log_dir = self.log_root / dir_name if subdir else self.log_root

        # 로그 저장 디렉터리 생성
        log_dir.mkdir(parents=True, exist_ok=True)

        # 로그 파일 경로
        log_file = log_dir / f"{name}-{today}.log"

        # ------------------------------
        # 로그 설정
        # ------------------------------
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False # 루트 로거로 로그가 전파되지 않도록 설정

        # 파일 핸들러 (매일 새 로그파일 생성, 최대 30일 보관)
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )

        file_handler.setFormatter(self.formatter)
        logger.addHandler(file_handler)

        # 콘솔 핸들러 추가 (설정값에 따라)
        if settings.LOG_TO_CONSOLE:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(self.console_formatter)
            logger.addHandler(console_handler)

        return logger
