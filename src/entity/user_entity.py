from sqlalchemy import Column, Integer, String, DateTime, func
from src.entity.base_entity import Base

class UserEntity(Base):
    __tablename__ = "users"

    seq      = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="회원 고유 순번")
    username = Column(String(50), unique=True, nullable=False, comment="회원 아이디")
    email    = Column(String(100), unique=True, nullable=False, comment="회원 이메일")
    password = Column(String(128), nullable=False, comment="회원 비밀번호")
    # Refresh Token 저장 컬럼: 로그아웃 시 값을 지워서 해당 토큰을 무효화
    current_refresh_token = Column(String(512), nullable=True, comment="유효한 Refresh Token")
    type       = Column(String(3), default='100', nullable=False, comment="회원 유형 (100: employee, 200: agency)")
    status     = Column(String(3), default='100', nullable=False, comment="회원 상태 (100: active, 200: inactive)")
    created_at = Column(DateTime, default=func.now(), comment="회원 생성일") # DB의 현재 시간 사용
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="회원 정보 수정일") # 업데이트 시 자동 반영
    deleted_at = Column(DateTime, nullable=True, comment="회원 삭제일 (삭제되지 않은 경우 NULL)")