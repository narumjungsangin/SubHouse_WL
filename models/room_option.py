from . import db

class RoomOption(db.Model):
    """방 옵션 모델"""
    __tablename__ = 'room_options'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False, index=True)
    option_name = db.Column(db.String(100), nullable=False)
    
    # 관계 설정
    contract = db.relationship('Contract', back_populates='room_options')
    
    def __repr__(self):
        return f'<RoomOption {self.id}: {self.option_name}>'
    
    def to_dict(self):
        """방 옵션 데이터를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'option_name': self.option_name
        }
