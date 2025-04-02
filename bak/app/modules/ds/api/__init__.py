from flask import Blueprint

from bak.app.modules.ds.api.file import file_bp
from bak.app.modules.ds.api.project import proj_bp

ds_bp = Blueprint('ds', __name__, url_prefix='/ds')

ds_bp.register_blueprint(proj_bp)
ds_bp.register_blueprint(file_bp)