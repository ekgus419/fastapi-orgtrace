"""
BaseRepository는 직접 인스턴스화해서 사용하지 않고,
구체적인 Repository(예: UserRepository)가 상속받아 사용하는 추상적인 기본 클래스이기 때문에,
providers_info에 따로 등록하지 않는다.
Providers_info에는 실제 DI 컨테이너를 통해 인스턴스를 생성할 구체적인 클래스들만 등록한다.
"""

DEPENDENCY_REGISTRY_CONFIG = {
    "user_repository": {
        "module": "src.repository.user.user_repository",   # 모듈 경로
        "class": "UserRepository",                         # 클래스명
        "dependencies": {
        },
    },
    "user_service": {
        "module": "src.service.user.user_service",
        "class": "UserService",
        "dependencies": {
            "user_repository": "user_repository",          # 의존성: 자동 등록된 user_repository provider 참조
        },
    },
    "auth_service": {
        "module": "src.service.auth.auth_service",
        "class": "AuthService",
        "dependencies": {
            "user_repository": "user_repository"
        },
    },
    "employee_repository": {
        "module": "src.repository.employee.employee_repository",
        "class": "EmployeeRepository",
        "dependencies": {
        },
    },
    "employee_service": {
        "module": "src.service.employee.employee_service",
        "class": "EmployeeService",
        "dependencies": {
            "employee_repository": "employee_repository"
        },
    },
    "position_repository": {
        "module": "src.repository.position.position_repository",
        "class": "PositionRepository",
        "dependencies": {
        },
    },
    "position_service": {
        "module": "src.service.position.position_service",
        "class": "PositionService",
        "dependencies": {
            "position_repository": "position_repository"
        },
    },
    "rank_repository": {
        "module": "src.repository.rank.rank_repository",
        "class": "RankRepository",
        "dependencies": {
        },
    },
    "rank_service": {
        "module": "src.service.rank.rank_service",
        "class": "RankService",
        "dependencies": {
            "rank_repository": "rank_repository"
        },
    },
    "organization_repository": {
        "module": "src.repository.organization.organization_repository",
        "class": "OrganizationRepository",
        "dependencies": {
        },
    },
    "organization_service": {
        "module": "src.service.organization.organization_service",
        "class": "OrganizationService",
        "dependencies": {
            "organization_repository": "organization_repository",
            "employee_repository": "employee_repository"
        },
    },
    "employee_history_repository": {
        "module": "src.repository.employee.employee_history_repository",
        "class": "EmployeeHistoryRepository",
        "dependencies": {
        },
    },
    "employee_history_service": {
        "module": "src.service.employee.employee_history_service",
        "class": "EmployeeHistoryService",
        "dependencies": {
            "employee_history_repository": "employee_history_repository",
        },
    },
    "organization_history_repository": {
        "module": "src.repository.organization.organization_history_repository",
        "class": "OrganizationHistoryRepository",
        "dependencies": {
        },
    },
    "organization_history_service": {
        "module": "src.service.organization.organization_history_service",
        "class": "OrganizationHistoryService",
        "dependencies": {
            "organization_history_repository": "organization_history_repository",
        },
    },
}
