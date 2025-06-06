# SubHouse 프로젝트

Flask, SQLAlchemy, Htmx, Tailwind CSS 및 Docker를 사용하여 구축된 위치 기반 메시지 공유 웹 애플리케이션입니다.

## 기술 스택

- **백엔드**: Flask, SQLAlchemy, Flask-Migrate
- **프론트엔드**: Htmx, Tailwind CSS
- **데이터베이스**: SQLite
- **API**: Google Maps API
- **컨테이너화**: Docker, Docker Compose

## 프로젝트 구조

```
SubHouse/
├── models/              # 데이터베이스 모델
│   ├── __init__.py
│   ├── location.py      # 위치 모델
│   └── message.py       # 메시지 모델
├── routes/              # 라우트 및 뷰
│   ├── __init__.py
│   ├── main.py          # 메인 페이지 라우트
│   └── maps.py          # 지도 관련 라우트
├── templates/           # 템플릿 파일
│   ├── index.html       # 메인 페이지
│   ├── maps.html        # 지도 페이지
│   └── partials/        # 부분 템플릿
│       ├── message.html
│       └── location.html
├── utils/               # 유틸리티 함수
│   ├── __init__.py
│   └── database.py      # 데이터베이스 초기화
├── .env                 # 환경 변수
├── app.py               # 애플리케이션 엔트리 포인트
├── config.py            # 설정 파일
├── init_db.py           # 데이터베이스 초기화 스크립트
├── requirements.txt     # 의존성 목록
├── Dockerfile           # Docker 이미지 구성
└── docker-compose.yml   # Docker Compose 설정
```

## 설치 및 실행 방법

### 로컬 개발 환경

1. 저장소 복제
   ```
   git clone <repository-url>
   cd SubHouse
   ```

2. 가상 환경 설정
   ```
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   ```

3. 의존성 설치
   ```
   pip install -r requirements.txt
   ```

4. 환경 변수 설정
   ```
   # .env 파일 생성
   # Google Maps API 키 (아래 값을 실제 API 키로 변경하세요)
   GOOGLE_MAPS_API_KEY=

   # Google OAuth 사용자 인증 정보 (아래 값을 실제 클라이언트 ID와 비밀번호로 변경하세요)
   # 아래에 실제 Google Cloud Console에서 가져온 정확한 정보를 입력해야 합니다
   GOOGLE_CLIENT_ID=
   GOOGLE_CLIENT_SECRET=

   # Flask 설정
   SECRET_KEY=
   FLASK_ENV=

   ```

5. 데이터베이스 초기화
   ```
   python init_db.py
   ```

6. 애플리케이션 실행
   ```
   python app.py
   ```

7. 웹 브라우저에서 접속
   ```
   http://127.0.0.1:5000
   ```

### Docker 환경

1. Docker 컨테이너 빌드 및 실행
   ```
   docker-compose up --build
   ```

2. 애플리케이션 접속
   ```
   http://localhost:5000
   ```

## 기능

- **메시지 관리**: 텍스트 메시지 추가 및 조회
- **위치 관리**: 위치 정보 추가 및 지도에 표시
- **지도 시각화**: Google Maps API를 사용한 위치 시각화
- **실시간 UI 업데이트**: Htmx를 사용한 페이지 부분 업데이트

## 개발 정보

- **Htmx 통합**: 비동기 폼 제출 및 UI 업데이트
- **모듈화된 구조**: Flask Blueprint를 사용한 코드 모듈화
- **Docker 지원**: 개발 및 배포 환경의 일관성 보장

## 라이센스

MIT License
