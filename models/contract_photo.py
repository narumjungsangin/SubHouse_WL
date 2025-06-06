from . import db

class ContractPhoto(db.Model):
    """계약 사진 모델"""
    __tablename__ = 'contract_photos'
    
    seq = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_id = db.Column(db.String(255), nullable=False)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False, index=True)
    
    # 관계 설정
    contract = db.relationship('Contract', back_populates='photos')
    
    def __repr__(self):
        return f'<ContractPhoto {self.seq}: {self.file_id}>'
    
    def to_dict(self):
        """계약 사진 데이터를 딕셔너리로 변환"""
        return {
            'seq': self.seq,
            'file_id': self.file_id,
            'contract_id': self.contract_id
        }
