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


## 국제화 (Internationalization - i18n) 설정 및 사용법

이 프로젝트는 Flask-Babel을 사용하여 다국어 지원(한국어 기본, 영어 지원)을 구현합니다.

### 1. 주요 설정 파일 및 코드

*   **`app.py`**:
    *   Flask-Babel 확장 초기화 및 관련 설정이 포함됩니다.
    *   `LANGUAGES`: 지원하는 언어 목록 (예: `{'en': 'English', 'ko': '한국어'}`)
    *   `BABEL_DEFAULT_LOCALE`: 기본 언어 설정 (예: `'ko'`)
    *   `BABEL_TRANSLATION_DIRECTORIES`: 번역 파일이 위치할 디렉토리 (예: `'translations'`)
    *   `@babel.localeselector` 데코레이터를 사용한 `get_locale_for_babel` 함수: 사용자의 요청(URL 파라미터, 세션 등)에 따라 적절한 언어를 선택합니다.

*   **`babel.cfg`**:
    *   `pybabel extract` 명령어가 번역할 문자열을 추출할 파일들을 지정합니다.
    *   Python 파일 (예: `app.py`, `models.py`, `routes/**.py`) 및 Jinja2 템플릿 파일 (예: `templates/**.html`)을 포함해야 합니다.
    *   파일 인코딩은 UTF-8로 설정하는 것이 좋습니다 (`# -*- coding: utf-8 -*-` 주석 또는 `charset = utf-8` 옵션).

*   **템플릿 파일 (`*.html`)**:
    *   번역이 필요한 모든 사용자 표시 문자열은 `_()` 또는 `gettext()` 함수로 감싸야 합니다.
        *   예시: `<h1>{{ _('안녕하세요') }}</h1>`
        *   예시: `<input placeholder="{{ _('사용자 이름') }}">`

### 2. 번역 작업 흐름 및 PyBabel 명령어

번역 작업은 일반적으로 다음 단계를 따릅니다. 모든 `pybabel` 명령어는 **가상 환경이 활성화된 상태**에서 프로젝트 루트 디렉토리에서 실행해야 합니다.

1.  **가상 환경 활성화** (운영체제 및 쉘에 따라 다름):
    ```bash
    # 예시 (Windows PowerShell)
    .\.venv\Scripts\Activate.ps1
    # 예시 (Linux/macOS bash)
    source .venv/bin/activate
    ```

2.  **번역 문자열 추출 (`extract`)**:
    *   코드와 템플릿에서 `_()`로 감싸인 문자열을 찾아 `messages.pot` (Portable Object Template) 파일을 생성하거나 업데이트합니다.
    ```bash
    pybabel extract -F babel.cfg -o messages.pot .
    ```

3.  **새로운 언어 번역 파일 초기화 (`init`)** (새로운 언어를 추가할 때 *처음 한 번만* 실행):
    *   `messages.pot` 파일을 기반으로 특정 언어(예: 영어 'en')를 위한 `.po` (Portable Object) 파일을 생성합니다.
    ```bash
    # 예시: 영어(en) 번역 파일 생성
    pybabel init -i messages.pot -d translations -l en
    ```
    *   `-d translations`는 번역 파일이 저장될 기본 디렉토리입니다. `translations/en/LC_MESSAGES/messages.po` 파일이 생성됩니다.

4.  **기존 번역 파일 업데이트 (`update`)**:
    *   새로 추출된 `messages.pot` 파일의 내용을 기반으로 기존의 모든 언어별 `.po` 파일을 업데이트합니다. 새로운 문자열이 추가되거나 기존 문자열이 변경된 경우 반영됩니다.
    ```bash
    pybabel update -i messages.pot -d translations
    ```
    *   이후 각 언어의 `.po` 파일 (예: `translations/en/LC_MESSAGES/messages.po`)을 열어 번역되지 않은 `msgstr ""` 부분을 해당 언어로 번역합니다.

5.  **번역 파일 컴파일 (`compile`)**:
    *   번역된 `.po` 파일들을 Flask 애플리케이션이 사용할 수 있는 바이너리 형태의 `.mo` (Machine Object) 파일로 컴파일합니다.
    ```bash
    pybabel compile -d translations
    ```
    *   컴파일 후에는 Flask 개발 서버를 재시작해야 변경된 번역이 적용될 수 있습니다.

### 3. 주의사항 및 팁

*   **인코딩**: `babel.cfg`, `.po` 파일 등은 모두 UTF-8 인코딩으로 저장하는 것이 좋습니다.
*   **서버 재시작**: `.mo` 파일이 변경된 후에는 Flask 개발 서버를 재시작해야 번역이 적용됩니다.
*   **브라우저 캐시**: 번역이 제대로 반영되지 않는 것 같으면 브라우저 캐시를 삭제하거나 시크릿 모드에서 확인해 보세요.
*   **로그 확인**: `app.py`의 `get_locale_for_babel` 함수 내에 로깅을 추가하면 어떤 언어가 선택되고 있는지 디버깅하는 데 도움이 됩니다.

