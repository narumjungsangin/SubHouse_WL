from flask import current_app
from models import db
from models.contract import Contract
from models.contract_photo import ContractPhoto
from models.user import User
from models.like import Like
from models.room_option import RoomOption


def init_db():
    """데이터베이스 초기화 및 기본 데이터 생성"""
    with current_app.app_context():
        db.create_all()
        db.session.commit()
        current_app.logger.info("데이터베이스가 초기화되었습니다.")
