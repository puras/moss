from flask import Blueprint

from app.utils.response import R

role_bp = Blueprint('roles', __name__, url_prefix='/roles')

@role_bp.route('', methods=['GET'])
def get_roles():
    item = {
        "name": "hello",
        "description": "hello",
        "created_by": "puras"
    }
    return R.bad_request(item, {"what": "wahaha"})