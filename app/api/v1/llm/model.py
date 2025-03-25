from flask import Blueprint, jsonify

from app.lib.llm.core import LLMClient
from app.utils.async_utils import async_route

mb_bp = Blueprint('model', __name__, url_prefix='/models')

@mb_bp.route('')
@async_route
async def get_models():
    config = {
        "provider": "Ollama",
        "endpoint": "http://192.168.0.100:11434",
        "api_key": "EMPTY",
        "model": "qwq:32b"
    }
    client = LLMClient(config)
    ret = await client.get_models()
    return jsonify(ret), 200