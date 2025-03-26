from flask import Blueprint

<<<<<<< HEAD
from app.api.v1.ds import ds_bp
from app.api.v1.llm import llm_bp
=======
from app.modules.prompt.api import prompt_bp
>>>>>>> refs/remotes/origin/main

# 创建API v1主蓝图
api_v1_bp = Blueprint('api_v1', __name__)

# 导入并注册各模块蓝图
from app.api.v1.ucenter import uc_bp
from app.api.v1.auth import auth_bp

api_v1_bp.register_blueprint(uc_bp)
api_v1_bp.register_blueprint(auth_bp)

<<<<<<< HEAD
api_v1_bp.register_blueprint(llm_bp)
api_v1_bp.register_blueprint(ds_bp)
=======
api_v1_bp.register_blueprint(prompt_bp)
>>>>>>> refs/remotes/origin/main
