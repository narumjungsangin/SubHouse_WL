from datetime import datetime
from flask_login import UserMixin
from . import db

class User(db.Model, UserMixin):
    """사용자 모델"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)  # 구글 OAuth ID
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    major = db.Column(db.String(100))
    grade = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    profile_picture = db.Column(db.String(500))  # 프로필 사진 URL
    nationality = db.Column(db.String(50))
    phone_number = db.Column(db.String(50))
    account_status = db.Column(db.String(20), default='active')  # active/inactive/suspended
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    posted_contracts = db.relationship('Contract', foreign_keys='Contract.posted_by', back_populates='poster')
    modified_contracts = db.relationship('Contract', foreign_keys='Contract.modified_by', back_populates='modifier')
    likes = db.relationship('Like', back_populates='user')
    
    __table_args__ = (
        db.Index('idx_user_email', 'email'),
        db.Index('idx_user_google_id', 'google_id'),
    )
    
    def __repr__(self):
        return f'<User {self.id}: {self.name}>'
    
    def to_dict(self):
        """사용자 데이터를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'google_id': self.google_id,
            'email': self.email,
            'name': self.name,
            'major': self.major,
            'grade': self.grade,
            'gender': self.gender,
            'profile_picture': self.profile_picture,
            'nationality': self.nationality,
            'phone_number': self.phone_number,
            'account_status': self.account_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
