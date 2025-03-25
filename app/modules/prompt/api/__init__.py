from flask import Blueprint

from app.modules.prompt.api.template import tp_bp

prompt_bp = Blueprint('prompt', __name__, url_prefix='/prompt')

prompt_bp.register_blueprint(tp_bp)