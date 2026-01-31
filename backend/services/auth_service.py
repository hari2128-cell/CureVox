# services/auth_service.py
from models import User
from extensions import db
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

def signup_demo(name, email, password):
    user = User.query.filter_by(email=email).first()
    if user:
        # generate token for existing
        token = create_access_token(identity=user.id)
        return token, user.to_dict()
    # create new user (store hashed password)
    hashed = generate_password_hash(password)
    user = User(name=name or "Demo", email=email, password=hashed)
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=user.id)
    return token, user.to_dict()

def login_demo(email, password):
    user = User.query.filter_by(email=email).first()
    if not user:
        return None, None
    if not check_password_hash(user.password, password):
        return None, None
    token = create_access_token(identity=user.id)
    return token, user.to_dict()
