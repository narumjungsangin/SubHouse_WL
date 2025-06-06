import os
import logging
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from models import init_app as init_models
from routes import init_app as init_routes
from config import get_config
from utils.database import init_db

# CSRF 보호 설정
csrf = CSRFProtect()

def create_app(config_name=None):
    """애플리케이션 팩토리 함수"""
    # 앱 인스턴스 생성
    app = Flask(__name__)
    
    # 설정 로드
    config_obj = get_config()
    app.config.from_object(config_obj)
    
    # 로깅 설정
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # 데이터베이스 초기화
    init_models(app)
    
    # CSRF 보호 초기화
    csrf.init_app(app)
    
    # 라우트 초기화
    init_routes(app)
    
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
