from pathlib import Path
import re
import inspect

class LoggingRouterProvider:
    """
    라우터 기반 로깅 서비스에 제공되는 유틸리티 클래스입니다.

    기능:
    - 요청 URL 경로에서 도메인 이름을 추출
    - 핸들러 함수의 이름을 추출
    - 라우터 디렉터리 기준으로 도메인의 유효성을 검증
    """

    def __init__(self, version: str = "v1", marker: str = "src"):
        """
        초기화 시 라우터 디렉토리 경로와 도메인 목록을 설정합니다.

        Args:
            version (str): API 버전. 기본값은 "v1"
            marker (str): 루트 디렉토리를 찾기 위한 기준 디렉토리 이름. 기본값은 "src"
        """
        self.root_dir = self._search_for_root_directory(marker)
        self.base_path = self.root_dir / "routers" / version
        self.router_domains = self._load_router_domains()

    @staticmethod
    def _search_for_root_directory(marker: str) -> Path:
        """
        루트 디렉토리를 탐색하여 지정된 마커(marker) 디렉토리를 찾습니다.
        (현재 파일 위치로부터 위로 올라가며 'src' 폴더를 찾는다.)

        Args:
            marker (str): 찾고자 하는 디렉토리 이름. 기본값은 'src'.

        Returns:
            Path: 찾은 디렉토리의 경로(Path 객체).

        Raises:
            RuntimeError: 지정한 디렉토리를 루트까지 탐색했음에도 찾지 못한 경우 예외를 발생시킵니다.
        """
        path = Path(__file__).resolve()
        while path != path.parent:
            if (path / marker).is_dir():
                return path / marker
            path = path.parent
        raise RuntimeError(f"'{marker}' 디렉토리를 찾을 수 없습니다.")

    def _load_router_domains(self) -> set[str]:
        """
        라우터 디렉토리에서 유효한 도메인(폴더) 목록을 로드합니다.

        라우터 구조: /routers/v1/ 하위의 디렉터리명이 도메인 이름이 됩니다.

        Returns:
            set[str]: 라우터 디렉토리 하위 폴더명 집합
        """
        return {
            p.name.replace("-", "_")  # 하이픈(-)은 언더스코어(_)로 변환
            for p in self.base_path.iterdir()
            if p.is_dir()
        }

    def extract_domain_from_path(self, path: str) -> str:
        """
        URL 경로에서 도메인을 추출하고, 실제 라우터 디렉터리와 일치하는지 확인합니다.

        예: "/v1/employee" → "employee"

        Args:
            path (str): 요청 URL 경로

        Returns:
            str: 추출된 도메인 (유효하지 않으면 "general" 반환)
        """
        DOMAIN_REGEX = re.compile(r"^/v1/([a-zA-Z0-9_-]+)")
        match = DOMAIN_REGEX.match(path)
        if match:
            raw = match.group(1).replace("-", "_")
            # _history 접미사가 있으면 원래 도메인으로 치환하여 확인
            if raw.endswith("_history"):
                base = raw.removesuffix("_history")
                if base in self.router_domains:
                    return raw
            return raw if raw in self.router_domains else "general"
        return "general"

    @staticmethod
    def resolve_handler_name(endpoint) -> str:
        """
        핸들러 함수(뷰 함수)의 이름을 추출합니다.

        Args:
            endpoint (Callable): FastAPI endpoint 함수

        Returns:
            str: 함수 이름 (정상 추출 불가 시 "unnamed_handler" 반환)
        """
        try:
            # 일반적인 함수의 경우
            if hasattr(endpoint, "__name__") and endpoint.__name__ != "<lambda>":
                return endpoint.__name__

            # 익명 함수 또는 래핑된 함수의 경우, 소스 코드 라인에서 직접 추출 시도
            if inspect.isfunction(endpoint):
                lines, _ = inspect.getsourcelines(endpoint)
                for line in lines:
                    if line.strip().startswith("def "):
                        return line.strip().split("(")[0].replace("def", "").strip()
        except Exception:
            pass

        return "unnamed_handler"
