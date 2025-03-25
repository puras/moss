from flask import Blueprint

from app.api.v1.llm.chat import chat_bp
from app.api.v1.llm.model import mb_bp

llm_bp = Blueprint('llm', __name__, url_prefix='/llm')

llm_bp.register_blueprint(mb_bp)
llm_bp.register_blueprint(chat_bp)