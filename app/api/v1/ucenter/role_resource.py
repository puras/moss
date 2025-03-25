from flask import Blueprint

role_bp = Blueprint('roles', __name__, url_prefix='/roles')

@role_bp.route('', methods=['GET'])
def get_roles():
    return 'Hello'