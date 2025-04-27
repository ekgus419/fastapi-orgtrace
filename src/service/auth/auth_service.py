from src.dto.request.auth.login_request_dto import LoginRequestDto
from src.dto.request.auth.logout_request_dto import LogoutRequestDto
from src.dto.response.auth.token_response_dto import TokenResponseDto
from src.exception.token_exceptions import InvalidRefreshTokenSubjectMissingException, RefreshTokenLoggedOutException, \
    RefreshTokenMismatchException
from src.repository.user.user_repository import UserRepository
from src.utils.security import verify_password  # 평문 vs 해시 비교 함수
from src.provider.jwt_token_provider import JwtTokenProvider  # 토큰 생성/검증 유틸리티
from src.exception.auth_exceptions import UnauthorizedException
from src.exception.user_exceptions import UserNotFoundException
from src.service.base_service import BaseService
from src.decorator.transaction import Transactional  # 트랜잭션 데코레이터 추가
from sqlalchemy.orm import Session


class AuthService(BaseService):
    """
    회원 인증 및 JWT 토큰 관리를 담당하는 서비스 클래스.
    로그인, 토큰 재발급, 로그아웃 기능을 제공함.
    """

    def __init__(self, user_repository: UserRepository):
        """
        AuthService 생성자.

        Args:
            user_repository (UserRepository): 회원 데이터를 관리하는 리포지토리 인스턴스.
        """
        self.user_repository = user_repository

    def swagger_login(self, db: Session, username: str, password: str) -> str:
        """
        Swagger UI용 로그인 처리 (Access Token만 반환).

        Args:
            db (Session): 데이터베이스 세션.
            username (str): 로그인 아이디.
            password (str): 로그인 비밀번호.

        Returns:
            str: 발급된 Access Token.

        Raises:
            UserNotFoundException: 존재하지 않는 회원일 경우.
            UnauthorizedException: 비밀번호가 일치하지 않을 경우.
        """
        user_domain = self.user_repository.get_user_by_username(db, username)
        if not user_domain:
            raise UserNotFoundException()

        if not user_domain.password or not verify_password(password, user_domain.password):
            raise UnauthorizedException()

        return JwtTokenProvider.generate_access_token(user_domain.username)


    @Transactional
    def login(self, db: Session, payload: LoginRequestDto) -> TokenResponseDto:
        """
        회원 로그인 처리 및 JWT Access Token / Refresh Token 발급.

        Args:
            db (Session): 데이터베이스 세션.
            payload (LoginRequestDto): 로그인 요청 DTO (username, password).

        Returns:
            TokenResponseDto: 발급된 Access Token과 Refresh Token.

        Raises:
            UserNotFoundException: 존재하지 않는 회원일 경우.
            UnauthorizedException: 비밀번호가 일치하지 않을 경우.
        """
        username = payload.username
        password = payload.password

        user_domain = self.user_repository.get_user_by_username(db, username)
        if not user_domain:
            raise UserNotFoundException()

        if not user_domain.password or not verify_password(password, user_domain.password):
            raise UnauthorizedException()

        access_token = JwtTokenProvider.generate_access_token(user_domain.username)
        refresh_token = JwtTokenProvider.generate_refresh_token(user_domain.username)

        self.user_repository.update_refresh_token(db, user_domain.seq, refresh_token)

        return TokenResponseDto(access_token=access_token, refresh_token=refresh_token)

    def refresh_access_token(self, db: Session, refresh_token: str) -> TokenResponseDto:
        """
        Refresh Token을 사용하여 새로운 Access Token을 발급.

        Args:
            db (Session): 데이터베이스 세션.
            refresh_token (str): 기존에 발급받은 Refresh Token.

        Returns:
            TokenResponseDto: 새로 발급된 Access Token과 기존 Refresh Token.

        Raises:
            InvalidRefreshTokenSubjectMissingException: 토큰 payload에 sub가 없을 경우.
            UserNotFoundException: 회원이 존재하지 않을 경우.
            RefreshTokenLoggedOutException: 저장된 Refresh Token과 불일치할 경우.
        """

        # 토큰 검증 및 회원 아이디 추출
        payload = JwtTokenProvider.validate_token(refresh_token)
        username = payload.get("sub")

        if not username:
            raise InvalidRefreshTokenSubjectMissingException()

        # Entity 변환 없이 Domain 반환
        user_domain = self.user_repository.get_user_by_username(db, username)
        if not user_domain:
            raise UserNotFoundException()

        # 저장된 refresh token과 비교
        if user_domain.current_refresh_token != refresh_token:
            raise RefreshTokenLoggedOutException()

        # 새로운 Access Token 생성
        new_access_token = JwtTokenProvider.generate_access_token(user_domain.username)
        return TokenResponseDto(access_token=new_access_token, refresh_token=refresh_token)

    @Transactional
    def logout(self, db: Session, payload: LogoutRequestDto):
        """
        회원 로그아웃 처리 (Refresh Token 무효화).

        Args:
            db (Session): 데이터베이스 세션.
            payload (LogoutRequestDto): 로그아웃 요청 DTO (username, refresh_token).

        Returns:
            bool: 로그아웃 처리 성공 여부.

        Raises:
            UserNotFoundException: 존재하지 않는 회원일 경우.
            RefreshTokenMismatchException: 저장된 Refresh Token과 불일치할 경우.
        """
        # 로그아웃 시, 회원 테이블의 refresh token 값을 삭제하여 블랙리스트 효과
        # Entity 변환 없이 Domain 반환
        user_domain = self.user_repository.get_user_by_username(db, payload.username)

        if not user_domain:
            raise UserNotFoundException()

        # 저장된 refresh token과 비교하여 일치하는 경우에만 삭제
        if user_domain.current_refresh_token != payload.refresh_token:
            raise RefreshTokenMismatchException()

        return self.user_repository.update_refresh_token(db, user_domain.seq, None)
