from . import db, BaseModel
from werkzeug.security import generate_password_hash, check_password_hash

class User(BaseModel):
    """User model for storing user details."""
    __tablename__ = 'users'
    
    # Basic Info
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Profile
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # male, female, other
    blood_group = db.Column(db.String(5), nullable=True)
    height = db.Column(db.Float, nullable=True)  # in cm
    weight = db.Column(db.Float, nullable=True)  # in kg
    
    # Medical
    allergies = db.Column(db.Text, nullable=True)
    chronic_conditions = db.Column(db.Text, nullable=True)
    current_medications = db.Column(db.Text, nullable=True)
    
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)
    emergency_contact_relation = db.Column(db.String(50), nullable=True)
    
    # Account Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    diagnoses = db.relationship('Diagnosis', backref='user', lazy=True)
    rash_analyses = db.relationship('RashAnalysis', backref='user', lazy=True)
    audio_analyses = db.relationship('AudioAnalysis', backref='user', lazy=True)
    sessions = db.relationship('UserSession', backref='user', lazy=True)
    
    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone_number': self.phone_number,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'blood_group': self.blood_group,
            'height': self.height,
            'weight': self.weight,
            'allergies': self.allergies,
            'chronic_conditions': self.chronic_conditions,
            'current_medications': self.current_medications,
            'emergency_contact': {
                'name': self.emergency_contact_name,
                'phone': self.emergency_contact_phone,
                'relation': self.emergency_contact_relation
            } if self.emergency_contact_name else None,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }