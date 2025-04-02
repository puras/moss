from flask import Blueprint, jsonify

from bak.app.lib.llm.core import LLMClient
from bak.app.utils.async_utils import async_route

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('', methods=['POST'])
@async_route
async def do_chat():
    config = {
        "provider": "Ollama",
        "endpoint": "http://192.168.0.100:11434",
        "api_key": "EMPTY",
        "model": "qwq:32b"
    }
    client = LLMClient(config)
    ret = await client.chat("""以下是描述任务的指令，以及提供进一步上下文的输入。
请写出一个适当完成请求的回答。
在回答之前，请仔细思考问题，并创建一个逻辑连贯的思考过程，以确保回答准确无误。

### 指令：
你是一位精通卜卦、星象和运势预测的算命大师。
请回答以下算命问题。

### 问题：
1992年闰四月初九巳时生人，女，想了解健康运势""")
    print(ret)
    return jsonify(ret), 200