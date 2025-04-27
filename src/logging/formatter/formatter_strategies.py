from abc import ABC, abstractmethod
from src.logging.formatter.json_log_formatter import get_json_log_formatter
from src.logging.formatter.text_log_formatter import get_text_log_formatter
from src.logging.formatter.console_log_formatter import get_console_log_formatter


class FormatterStrategy(ABC):
    """
    로그 포매터 공통 전략 인터페이스입니다.
    모든 포매터 전략 클래스는 get_formatter 메서드를 구현해야 합니다.
    """

    @abstractmethod
    def get_formatter(self):
        """
        실제 포매터 인스턴스를 반환합니다.

        Returns:
            logging.Formatter: 포매터 객체
        """
        pass

class JsonFormatterStrategy(FormatterStrategy):
    """
    JSON 형식의 로그 포매터를 반환하는 전략 클래스입니다.
    """

    def get_formatter(self):
        return get_json_log_formatter()

class TextFormatterStrategy(FormatterStrategy):
    """
    텍스트 형식의 로그 포매터를 반환하는 전략 클래스입니다.
    """

    def get_formatter(self):
        return get_text_log_formatter()

class ConsoleFormatterStrategy(FormatterStrategy):
    """
    콘솔 로그 출력용 포매터를 반환하는 전략 클래스입니다.
    """

    def get_formatter(self):
        return get_console_log_formatter()

class FormatterFactory:
    """
    로그 포매터 전략 객체를 생성하는 팩토리 클래스입니다.
    format_type 값에 따라 알맞은 전략 인스턴스를 반환합니다.
    """

    @staticmethod
    def create(format_type: str) -> FormatterStrategy:
        """
        파일용 포매터 전략을 생성합니다.

        Args:
            format_type (str): 사용할 포맷 형식 ("json", "text")

        Returns:
            FormatterStrategy: 선택된 포맷 전략 인스턴스 (기본: TextFormatterStrategy)
        """
        return {
            "json": JsonFormatterStrategy(),
            "text": TextFormatterStrategy(),
        }.get(format_type.lower(), TextFormatterStrategy())

    @staticmethod
    def create_console() -> FormatterStrategy:
        """
        콘솔 로그 출력을 위한 포매터 전략 인스턴스를 생성합니다.

        Returns:
            FormatterStrategy: 콘솔 포맷 전략 인스턴스
        """
        return ConsoleFormatterStrategy()
