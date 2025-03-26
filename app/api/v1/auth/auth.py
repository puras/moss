from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.api.v1.auth import auth_bp
from app.services.ucenter.user import authenticate_user
from app.utils.response import R


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('passwd'):
        return R.fail(400, "Missing email or password")
    
    user = authenticate_user(data['email'], data['passwd'])
    
    if not user:
        return R.fail(401, "Invalid credentials")
    
    # 创建访问令牌和刷新令牌
    user_id = str(user.id)
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    
    return R.ok({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id
    })

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        print(current_user_id)
        access_token = create_access_token(identity=current_user_id)

        return R.ok({"access_token": access_token})
    except ValueError as e:
        print("=--------3")
        print(e)
        return R.fail(str(e))
