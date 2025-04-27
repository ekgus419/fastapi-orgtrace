from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.exception.token_exceptions import InvalidTokenScopeException
from src.provider.jwt_token_provider import JwtTokenProvider

"""
FastAPI의 dependency를 사용하여 요청마다 JWT를 검증
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/swagger-token")  # 로그인 엔드포인트 지정

def get_current_username(token: str = Depends(oauth2_scheme)) -> str:
    """
    Authorization 헤더에서 토큰을 추출한 후,
    JwtTokenProvider의 get_username_from_token을 호출하여 username을 반환합니다.
    """
    payload = JwtTokenProvider.validate_token(token)
    token_scope = payload.get("scope")
    if token_scope != "access":
        raise InvalidTokenScopeException()

    return JwtTokenProvider.get_username_from_token(token)
