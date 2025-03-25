from app.models.ucenter.user import User
from app.extensions import db

def get_all_users():
    return User.query.all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def create_user(account, email, password):
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(account=account).first():
        raise ValueError("Account already exists")
    
    if User.query.filter_by(email=email).first():
        raise ValueError("Email already exists")
    
    user = User(account=account, email=email)
    user.password = password
    
    db.session.add(user)
    db.session.commit()
    
    return user

def authenticate_user(email, password):
    user = get_user_by_email(email)
    
    if user and user.verify_password(password):
        return user
    
    return None