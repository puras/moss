from flask import Blueprint

uc_bp = Blueprint('ucenter', __name__, url_prefix='/uc')

# 导入用户资源
from app.api.v1.ucenter.user_resource import user_bp
from app.api.v1.ucenter.role_resource import role_bp

uc_bp.register_blueprint(user_bp)
uc_bp.register_blueprint(role_bp)