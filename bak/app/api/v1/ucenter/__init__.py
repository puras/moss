from flask import Blueprint

uc_bp = Blueprint('ucenter', __name__, url_prefix='/uc')

# 导入用户资源
from bak.app.api.v1.ucenter.user import user_bp
from bak.app.api.v1.ucenter.role import role_bp

uc_bp.register_blueprint(user_bp)
uc_bp.register_blueprint(role_bp)