from flask import Blueprint

from app.api.v1.ds.project import proj_bp
from app.api.v1.llm.chat import chat_bp
from app.api.v1.llm.model import mb_bp

ds_bp = Blueprint('ds', __name__, url_prefix='/ds')

ds_bp.register_blueprint(proj_bp)