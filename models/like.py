from datetime import datetime
from . import db

class Like(db.Model):
    """좋아요 모델"""
    __tablename__ = 'likes'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), primary_key=True)
    liked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    user = db.relationship('User', back_populates='likes')
    contract = db.relationship('Contract', back_populates='likes')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'contract_id', name='unique_user_contract_like'),
        db.Index('idx_like_contract', 'contract_id'),
    )
    
    def __repr__(self):
        return f'<Like {self.user_id}:{self.contract_id}>'
    
    def to_dict(self):
        """좋아요 데이터를 딕셔너리로 변환"""
        return {
            'user_id': self.user_id,
            'contract_id': self.contract_id,
            'liked_at': self.liked_at.isoformat() if self.liked_at else None
        }
