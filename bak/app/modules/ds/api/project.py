from flask import Blueprint, jsonify, request

from bak.app.lib.db.project import get_projects, create_project
from bak.app.utils.async_utils import async_route

proj_bp = Blueprint('project', __name__, url_prefix='/projects')

@proj_bp.route('', methods=['GET'])
@async_route
async def get_list():
    projects = await get_projects()
    return jsonify(projects), 200

@proj_bp.route('', methods=['POST'])
@async_route
async def create():
    params = request.get_json()
    if not params or not params.get('name'):
        return jsonify({'message': 'Missing name'}), 400
    proj = await create_project(params)
    return jsonify(proj), 201