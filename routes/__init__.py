def init_app(app):
    """애플리케이션에 모든 라우트 등록"""
    from .main import main_bp
    from .auth import auth_bp, init_login_manager, init_oauth
    from .contract import contract_bp

    # 블루프린트 등록
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(contract_bp)

    # 인증 관련 초기화
    init_login_manager(app)
    init_oauth(app)
