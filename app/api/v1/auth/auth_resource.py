from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.api.v1.auth import auth_bp
from app.services.ucenter.user_service import authenticate_user

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing email or password"}), 400
    
    user = authenticate_user(data['email'], data['password'])
    
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401
    
    # 创建访问令牌和刷新令牌
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
# @jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({"access_token": access_token}), 200