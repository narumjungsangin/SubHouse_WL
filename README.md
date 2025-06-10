# SubHouse 프로젝트

Flask, SQLAlchemy, 및 Docker를 사용하여 구축된 부동산 계약 정보 관리 및 공유 웹 애플리케이션입니다.

## 주요 기능

- **사용자 인증**: 이메일 기반 회원가입, 로그인, 로그아웃 및 Google OAuth를 통한 소셜 로그인을 지원합니다.
- **부동산 계약 관리**: 매물(계약) 정보를 등록, 조회, 수정 및 삭제할 수 있는 CRUD 기능을 제공합니다.
- **사진 관리**: 각 매물에 여러 장의 사진을 업로드하고 관리할 수 있습니다.
- **'좋아요' 기능**: 사용자는 관심 있는 매물에 '좋아요'를 표시하여 위시리스트를 관리할 수 있습니다.
- **다국어 지원**: 한국어(기본)와 영어를 지원하며, Flask-Babel을 통해 확장 가능합니다.

## 기술 스택

- **백엔드**: Flask, SQLAlchemy, Flask-Migrate, Flask-Login
- **데이터베이스**: SQLite (개발용), PostgreSQL (프로덕션용 권장)
- **인증**: WTForms, Flask-WTF, Authlib (for Google OAuth)
- **국제화**: Flask-Babel
- **컨테이너화**: Docker, Docker Compose
- **프론트엔드**: Jinja2 템플릿, (필요시 Htmx, Tailwind CSS 등 사용 가능)

## 프로젝트 구조

```
SubHouse_WL/
├── app.py               # 애플리케이션 팩토리 및 엔트리 포인트
├── config.py            # 설정 파일
├── requirements.txt     # Python 의존성 목록
├── Dockerfile           # Docker 이미지 구성
├── docker-compose.yml   # Docker Compose 설정
├── .env                 # 환경 변수 파일
│
├── models/              # 데이터베이스 모델 (SQLAlchemy)
│   ├── user.py          # 사용자 모델
│   ├── contract.py      # 계약(매물) 모델
│   ├── contract_photo.py# 계약 사진 모델
│   ├── like.py          # '좋아요' 모델
│   └── room_option.py   # 방 옵션 모델
│
├── routes/              # 라우트 및 뷰 (Flask Blueprints)
│   ├── auth.py          # 인증 관련 라우트 (로그인, 로그아웃 등)
│   ├── contract.py      # 계약 정보 관리 라우트
│   └── main.py          # 메인 페이지 라우트
│
├── static/              # 정적 파일 (CSS, JS, 이미지)
├── templates/           # Jinja2 템플릿 파일
├── translations/        # 다국어 번역 파일 (i18n)
├── utils/               # 유틸리티 함수
│   └── database.py      # 데이터베이스 초기화 유틸
│
└── init_db.py           # 데이터베이스 초기화 스크립트
```

## 설치 및 실행 방법

### 로컬 개발 환경

1.  **저장소 복제**
    ```bash
    git clone <repository-url>
    cd SubHouse_WL
    ```

2.  **가상 환경 생성 및 활성화**
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate
    
    # macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **의존성 설치**
    ```bash
    pip install -r requirements.txt
    ```

4.  **환경 변수 설정 (`.env` 파일 생성)**
    `.env.example` 파일을 참고하여 `.env` 파일을 생성하고 아래 내용을 채워주세요.
    ```ini
    # Google Maps API (필요시)
    GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_API_KEY

    # Google OAuth 2.0 Client
    GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET

    # Flask 설정
    SECRET_KEY=a_very_secret_key_for_flask_session
    FLASK_ENV=development
    ```

5.  **데이터베이스 초기화**
    ```bash
    # 데이터베이스 테이블 생성
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    
    # (선택) 초기 데이터 추가
    python init_db.py
    ```

6.  **애플리케이션 실행**
    ```bash
    flask run
    ```

7.  **웹 브라우저에서 접속**
    [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Docker 환경

1.  **환경 변수 설정**
    로컬 환경과 동일하게 `.env` 파일을 설정합니다.

2.  **Docker 컨테이너 빌드 및 실행**
    ```bash
    docker-compose up --build
    ```

3.  **애플리케이션 접속**
    [http://localhost:5000](http://localhost:5000)

## 국제화 (i18n) 명령어

번역 작업은 `pybabel` 명령어를 사용합니다. 모든 명령어는 가상 환경이 활성화된 상태에서 실행해야 합니다.

1.  **번역 문자열 추출**: 코드와 템플릿에서 번역할 문자열을 찾아 `messages.pot` 파일을 생성/업데이트합니다.
    ```bash
    pybabel extract -F babel.cfg -o messages.pot .
    ```

2.  **번역 파일 업데이트**: `messages.pot` 파일의 내용으로 각 언어의 `.po` 파일을 업데이트합니다.
    ```bash
    pybabel update -i messages.pot -d translations
    ```

3.  **번역 파일 컴파일**: 번역된 `.po` 파일을 애플리케이션이 사용할 `.mo` 파일로 컴파일합니다.
    ```bash
    pybabel compile -d translations
    ```

## 기여 방법

이 프로젝트에 기여하고 싶으시다면, 다음 절차를 따라주세요.

1.  이 저장소를 **Fork** 하세요.
2.  새로운 기능이나 버그 수정을 위한 **Branch**를 생성하세요 (`git checkout -b feature/amazing-feature`).
3.  변경 사항을 **Commit** 하세요 (`git commit -m 'Add some amazing feature'`).
4.  Branch를 원격 저장소에 **Push** 하세요 (`git push origin feature/amazing-feature`).
5.  **Pull Request**를 생성하여 변경 사항을 제안해주세요.

## 라이센스

이 프로젝트는 [MIT License](LICENSE)를 따릅니다.

