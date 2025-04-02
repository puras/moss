from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 导入认证资源
from bak.app.api.v1.auth import auth