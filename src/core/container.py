import importlib
from dependency_injector import containers, providers
from src.config.dependency_registry_config import DEPENDENCY_REGISTRY_CONFIG
from src.logging.config.logging_config import LoggingConfig
from src.logging.config.uvicorn_logging_config import UvicornLoggingConfig


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["src.routers"])
    logger_config = providers.Singleton(LoggingConfig)
    uvicorn_logger_config = providers.Singleton(UvicornLoggingConfig)


def auto_register_dependencies(container_cls: type):
    """
    DEPENDENCY_REGISTRY_CONFIG에 정의된 provider들을 동적으로 컨테이너 클래스에 등록합니다.
    Args:
         container_cls: 의존성을 등록할 컨테이너 클래스
    """
    for provider_name, config in DEPENDENCY_REGISTRY_CONFIG.items():
        module_name = config["module"]
        class_name = config["class"]
        dependencies = config.get("dependencies", {})

        # 모듈 동적 임포트 및 클래스 획득
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)

        # 의존성 매핑 (설정 파일에 정의된 의존성을 컨테이너의 provider로 치환)
        dep_kwargs = {}
        for dep_param, dep_provider_name in dependencies.items():
            dep_kwargs[dep_param] = getattr(container_cls, dep_provider_name)

        # Factory provider 생성 후 컨테이너 클래스에 등록
        provider = providers.Factory(cls, **dep_kwargs)
        setattr(container_cls, provider_name, provider)


# Container 클래스에 provider들을 자동 등록
auto_register_dependencies(Container)

# Container 인스턴스 생성 (wiring 및 override 시 사용)
container = Container()
