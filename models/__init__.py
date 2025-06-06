from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def init_app(app):
    """애플리케이션에 데이터베이스 초기화"""
    db.init_app(app)
    migrate.init_app(app, db)

    # 모델 임포트
    from .user import User
    from .contract import Contract
    from .contract_photo import ContractPhoto
    from .like import Like
    from .room_option import RoomOption

    return db
