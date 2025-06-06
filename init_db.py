import os
from app import app
from models import db
from utils.database import init_db

# 데이터베이스 파일이 있으면 삭제
with app.app_context():
    # 기존 데이터베이스 연결 해제
    db.session.remove()
    db.drop_all()
    
    # 데이터베이스 초기화
    db.create_all()
    
    # 기본 데이터 추가
    init_db()
    
    print("데이터베이스가 성공적으로 초기화되었습니다.")
