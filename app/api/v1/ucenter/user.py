from flask import request, Blueprint
from flask_jwt_extended import jwt_required
from app.services.ucenter.user import get_user_by_id, create_user, get_all_users
# 更新导入路径
from app.api.v1.ucenter.schemas import UserSchema
from app.utils.response import R

user_bp = Blueprint('users', __name__, url_prefix='/users')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@user_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    users = get_all_users()
    return R.ok(users_schema.dump(users))

@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return R.not_found("User not found")

    return R.ok(user_schema.dump(user))

@user_bp.route('', methods=['POST'])
def register_user():
    data = request.get_json()
    
    # 验证数据
    errors = user_schema.validate(data)
    if errors:
        return R.bad_request("Validation error", {"errors": errors})
    
    # 创建用户
    try:
        user = create_user(
            account=data['account'],
            email=data['email'],
            password=data['password']
        )
        return R.ok(user_schema.dump(user), code=201)
    except ValueError as e:
        return R.fail(str(e))