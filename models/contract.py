from datetime import datetime
from sqlalchemy import Index
from . import db

class Contract(db.Model):
    """계약 모델"""
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location = db.Column(db.String(200), nullable=False, index=True)
    house_name = db.Column(db.String(100))
    latitude = db.Column(db.Float)  # 위도 정보
    longitude = db.Column(db.Float)  # 경도 정보
    room_count = db.Column(db.Integer)
    bathroom_count = db.Column(db.Float)
    roommate_allowed = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    monthly_rent_usd = db.Column(db.Float, index=True)  # 달러
    deposit_usd = db.Column(db.Float, nullable=True)  # 달러
    # transaction_type = db.Column(db.String(50)) # 월세/전세/매매
    posted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    modified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    modified_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    contract_status = db.Column(db.String(20), default='active')  # active/completed/cancelled
    is_deleted = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, nullable=True)  # 매물 설명
    seller_kakao = db.Column(db.String(20), nullable=True)  # 카카오톡 아이디
    seller_phone = db.Column(db.String(20), nullable=True)  # 전화번호
    seller_instagram = db.Column(db.String(20), nullable=True)  # 인스타그램 아이디
    build_year = db.Column(db.Integer)  # 건축 연도
    size_sqft = db.Column(db.Float)  # 면적 (평방피트)
    
    # 관계 설정
    poster = db.relationship('User', foreign_keys=[posted_by], back_populates='posted_contracts')
    modifier = db.relationship('User', foreign_keys=[modified_by], back_populates='modified_contracts')
    photos = db.relationship('ContractPhoto', back_populates='contract', cascade='all, delete-orphan')
    likes = db.relationship('Like', back_populates='contract', cascade='all, delete-orphan')
    room_options = db.relationship('RoomOption', back_populates='contract', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_location_rent', 'location', 'monthly_rent_usd'),
        db.Index('idx_posted_status', 'posted_at', 'contract_status'),
    )
    
    def __repr__(self):
        return f'<Contract {self.id}: {self.house_name}>'
    
    def to_dict(self):
        """계약 데이터를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'location': self.location,
            'house_name': self.house_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'room_count': self.room_count,
            'bathroom_count': self.bathroom_count,
            'build_year': self.build_year,
            'roommate_allowed': self.roommate_allowed,
            'size_sqft': self.size_sqft,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'monthly_rent_usd': self.monthly_rent_usd,
            'deposit_usd': self.deposit_usd,
            'posted_by': self.posted_by,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'modified_by': self.modified_by,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
            'contract_status': self.contract_status,
            'is_deleted': self.is_deleted,
            'view_count': self.view_count
        }
