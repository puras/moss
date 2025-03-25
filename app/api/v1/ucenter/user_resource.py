from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required
from app.services.ucenter.user_service import get_user_by_id, create_user, get_all_users
# 更新导入路径
from app.api.v1.ucenter.schemas import UserSchema

user_bp = Blueprint('users', __name__, url_prefix='/users')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@user_bp.route('', methods=['GET'])
# @jwt_required()
def get_users():
    users = get_all_users()
    return jsonify(users_schema.dump(users)), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
# @jwt_required()
def get_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(user_schema.dump(user)), 200

@user_bp.route('', methods=['POST'])
def register_user():
    data = request.get_json()
    
    # 验证数据
    errors = user_schema.validate(data)
    if errors:
        return jsonify({"message": "Validation error", "errors": errors}), 400
    
    # 创建用户
    try:
        user = create_user(
            account=data['account'],
            email=data['email'],
            password=data['password']
        )
        return jsonify(user_schema.dump(user)), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400