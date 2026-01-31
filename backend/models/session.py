from . import db, BaseModel

class UserSession(BaseModel):
    """User session tracking model."""
    __tablename__ = 'user_sessions'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(500), nullable=False, unique=True, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    device_info = db.Column(db.String(200), nullable=True)
    login_time = db.Column(db.DateTime, default=db.func.now())
    logout_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'device_info': self.device_info,
            'login_time': self.login_time.isoformat(),
            'logout_time': self.logout_time.isoformat() if self.logout_time else None,
            'is_active': self.is_active
        }