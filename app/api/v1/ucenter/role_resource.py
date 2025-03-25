from flask import Blueprint, jsonify

role_bp = Blueprint('roles', __name__, url_prefix='/roles')

@role_bp.route('', methods=['GET'])
def get_roles():
    item = {
        "name": "hello",
        "description": "hello",
        "created_by": "puras"
    }
    return jsonify(item), 200