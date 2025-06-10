import os
import logging
from flask import Flask, render_template, session, request, redirect, url_for # session, request, redirect, url_for 추가
from flask_login import current_user # current_user 추가
from flask_wtf.csrf import CSRFProtect
from models import init_app as init_models
from routes import init_app as init_routes
from config import get_config
from utils.database import init_db
from flask_babel import Babel # Babel 추가

# CSRF 보호 설정
csrf = CSRFProtect()

def create_app(config_name=None):
    """애플리케이션 팩토리 함수"""
    # 앱 인스턴스 생성
    app = Flask(__name__)
    
    # 설정 로드
    config_obj = get_config()
    app.config.from_object(config_obj)

    # 언어 설정 추가
    app.config['LANGUAGES'] = {
        'en': 'English',
        'ko': '한국어'
    }
    app.config['BABEL_DEFAULT_LOCALE'] = 'ko'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations' # 번역 파일 디렉토리
    
    # 로깅 설정
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # 데이터베이스 초기화
    init_models(app)
    
    # CSRF 보호 초기화
    csrf.init_app(app)

    # Babel 초기화
    babel = Babel() # Babel 객체 먼저 생성
    
    # 라우트 초기화
    init_routes(app) # Babel 초기화 전에 라우트 초기화 (라우트가 Babel에 의존하지 않는 경우)
    
    # Define the locale selector function
    def get_locale_for_babel():
        selected_locale = None
        # URL 파라미터에서 언어 가져오기 (예: /?lang=en)
        lang_from_url = request.args.get('lang')
        if lang_from_url and lang_from_url in app.config['LANGUAGES'].keys():
            session['language'] = lang_from_url
            selected_locale = lang_from_url
            app.logger.info(f"Locale selected from URL param: {selected_locale}")
            return selected_locale

        # 세션에 저장된 언어 사용
        if 'language' in session and session['language'] in app.config['LANGUAGES'].keys():
            selected_locale = session['language']
            app.logger.info(f"Locale selected from session: {selected_locale}")
            return selected_locale

         # If no URL parameter or session language is set, use the default locale.
        default_locale = app.config.get('BABEL_DEFAULT_LOCALE', 'ko') # This is already 'ko'
        app.logger.info(f"No URL param or session language, using default locale: {default_locale}")
        return default_locale

    # app과 연결하고 locale_selector 직접 등록
    babel.init_app(app, locale_selector=get_locale_for_babel)

    # 컨텍스트 프로세서 추가
    @app.context_processor
    def inject_language_vars():
        current_locale = get_locale_for_babel() # 현재 로케일 가져오기
        is_admin = current_user.is_authenticated and hasattr(current_user, 'email') and current_user.email == app.config.get('ADMIN_EMAIL')
        return dict(
            LANGUAGES=app.config['LANGUAGES'],
            CURRENT_LANGUAGE_CODE=current_locale,
            CURRENT_LANGUAGE_NAME=app.config['LANGUAGES'].get(current_locale),
            is_admin=is_admin
        )

    @app.route('/set_language/<language>')
    def set_language(language=None):
        if language and language in app.config['LANGUAGES'].keys():
            session['language'] = language
        # 이전 페이지로 리다이렉트, 없으면 홈으로
        return redirect(request.referrer or url_for('main.index'))

    # 데이터베이스 디렉토리 확인
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    return app

# 애플리케이션 생성
app = create_app()


# 직접 실행 시
if __name__ == '__main__':
    # 데이터베이스 초기화
    with app.app_context():
        from models import db
        db.drop_all()
        db.create_all()
        init_db()
        app.logger.info('데이터베이스가 초기화되었습니다.')
    
    # 디버그 모드 활성화 및 템플릿 캐시 비활성화
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
