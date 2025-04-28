# fastapi-orgtrace
```
📂 fastapi-rms/
 ├── .gitignore              # git 버전 관리 제외 파일
 ├── alembic.ini             # Alembic 마이그레이션 설정
 └── main.py                 # FastAPI 앱 시작점
 ├── README.md               # 프로젝트 설명
 ├── requirements.txt        # 의존성 패키지 목록
 ├── 📂 .github/             # 자동화 워크플로 및 PR 설정
 ├── 📂 .venv/               # 의존성 패키지 설치 경로
 ├── 📂 alembic/             # 데이터베이스 마이그레이션 도구
 ├── 📂 http/                # API 테스트
 ├── 📂 logs/                # 로그 파일 저장 지점
 ├── 📂 src/
 │   ├── 📂 config/          # dependency provider 설정 등
 │   ├── 📂 core/            # 핵심 인프라 구성요소 (DB, DI 컨테이너 등)
 │   ├── 📂 decorator/       # 공통 데코레이터 (예: 트랜잭션, 로그 기록 등)
 │   ├── 📂 domain/          # 도메인 모델 (비비즈니스 중심의 데이터 구조)
 │   ├── 📂 dto/             # 데이터 전달 객체 (Request/Response)
 │   ├── 📂 entity/          # 데이터베이스 모델 (DB 테이블과 매핑, ORM)
 │   ├── 📂 enum/            # 공통 Enum 클래스
 │   ├── 📂 env/             # .env 환경설정 파일들
 │   ├── 📂 exception/       # 커스텀 예외 정의
 │   ├── 📂 logging/         # 로깅 관련 유틸리티 및 설정
 │   ├── 📂 mapper/          # 엔티티 ↔ 도메인 변환
 │   ├── 📂 middleware/      # 미들웨어 모음
 │   ├── 📂 provider/        # 서비스 제공자 (TokenProvider, TimeProvider 등)
 │   ├── 📂 repository/      # 데이터 접근 레이어 (DAO, Repository)
 │   ├── 📂 routers/         # API 컨트롤러 (FastAPI 엔드포인트)
 │   ├── 📂 service/         # 비즈니스 로직 레이어 (Service)
 │   ├── 📂 tests/           # 테스트 코드
 │   └── 📂 utils/           # 유틸리티 함수
```
