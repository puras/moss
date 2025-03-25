from flask import Blueprint

from app.utils.response import R

tp_bp=Blueprint('templates', __name__, url_prefix='/templates')

@tp_bp.route('', methods=['GET'])
def get_list():
    return R.ok()

@tp_bp.route('/<int:temp_id>', methods=['GET'])
def get_one(temp_id):
    return R.ok()

@tp_bp.route('', methods=['POST'])
def create():
    return R.ok()

@tp_bp.route('/<int:temp_id>/update', methods=['POST'])
def update(temp_id):
    return R.ok()

@tp_bp.route('/<int:temp_id>/delete', methods=['POST'])
def delete(temp_id):
    return R.ok()