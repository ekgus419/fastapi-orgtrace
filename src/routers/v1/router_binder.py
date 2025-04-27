from fastapi import FastAPI

from src.routers.v1.auth.auth_router import router as auth_router
from src.routers.v1.user.user_router import router as user_router
from src.routers.v1.rank.rank_router import router as rank_router
from src.routers.v1.position.position_router import router as position_router
from src.routers.v1.employee.employee_router import router as employee_router
from src.routers.v1.employee.employee_history_router import router as employee_history_router
from src.routers.v1.organization.organization_router import router as organization_router
from src.routers.v1.organization.organization_history_router import router as organization_history_router
from src.routers.v1.test_router import router as test_router

def register_routers(app: FastAPI):
    """
    v1 API 라우터를 FastAPI 앱에 등록합니다.
    각 도메인(인증, 사용자, 조직 등)에 대한 라우터를 지정된 prefix와 함께 앱에 바인딩합니다.

    Args:
        app: 라우터를 등록할 FastAPI 애플리케이션 인스턴스
    """
    app.include_router(test_router,                 prefix="/v1/test",                 tags=["debug"])
    app.include_router(auth_router,                 prefix="/v1/auth",                 tags=["auth"])
    app.include_router(user_router,                 prefix="/v1/user",                 tags=["user"])
    app.include_router(rank_router,                 prefix="/v1/rank",                 tags=["rank"])
    app.include_router(position_router,             prefix="/v1/position",             tags=["position"])
    app.include_router(employee_router,             prefix="/v1/employee",             tags=["employee"])
    app.include_router(organization_router,         prefix="/v1/organization",         tags=["organization"])
    app.include_router(employee_history_router,     prefix="/v1/employee-history",     tags=["employee-history"])
    app.include_router(organization_history_router, prefix="/v1/organization-history", tags=["organization-history"])
