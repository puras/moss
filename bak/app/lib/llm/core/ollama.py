import http.client
import json
from typing import Dict, Any, List, Callable, Union


class OllamaAPI:
    def __init__(self, config: Dict[str, Any] = None):
        config = config or {}
        self.host = config.get('host', '127.0.0.1')
        self.port = config.get('port', 11434)
        self.model = config.get('model', 'llama2')
        self.base_url = f"http://{self.host}:{self.port}"

    async def get_models(self) -> list[dict[str, Any]]:
        """
        获取本地可用的模型列表
        Returns:
            返回模型列表
        """
        try:
            response = await self._make_request('/api/tags', {
                'method': 'GET',
                'headers': {
                    'Content-Type': 'application/json'
                }
            })

            # 处理响应，提取模型名称
            if response and response.get('model'):
                return [{
                    'name': model['name'],
                    'modified_at': model['modified_at'],
                    'size': model['size']
                } for model in response['model']]

            return []
        except Exception as error:
            print('获取 Ollama 模型列表出错:', str(error))
            raise

    async def chat(self, prompt: str, options: dict[str, Any] = None) -> dict[str, Any]:
        """
        生成对话响应
        Args:
            prompt: 用户输入的提示词
            options: 可选参数
                temperature: 温度参数(0-1)
                top_p: top_p参数(0-1)
                top_k: top_k参数
                stream: 是否使用流式响应
        Returns:
            返回模型响应
        """
        default_options = {
            'model': self.model,
            'prompt': prompt,
            'stream': False,
            'temperature': 0.7,
            'top_p': 0.9,
            'top_k': 40,
            'num_predict': 4096,
            'max_tokens': 8192,
        }

        request_options = {**default_options, **(options or {})}

        try:
            return await self._make_request('/api/generate', {
                'method': 'POST',
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(request_options)
            })
        except Exception as error:
            print('Ollama API 调用出错:', str(error))
            raise

    async def chat_stream(self, prompt: str, on_data: Callable[[dict], None], options: dict[str, Any] = None):
        """
        流式生成对话响应
        Args:
            prompt: 用户输入的提示词
            on_data: 处理每个数据块的回调函数
            options: 可选参数
        """
        request_options = {
            **(options or {}),
            'model': self.model,
            'prompt': prompt,
            'stream': True
        }

        try:
            await self._make_stream_request('/api/generate', {
                'method': 'POST',
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(request_options)
            }, on_data)
        except Exception as error:
            print('Ollama 流式API调用出错:', str(error))
            raise

    async def _make_request(self, path: str, options: dict[str, Any]) -> dict[str, Any] | None:
        """发送HTTP请求"""
        conn = http.client.HTTPConnection(self.host, self.port)
        try:
            conn.request(
                options['method'],
                path,
                options.get('body'),
                options.get('headers', {})
            )
            response = conn.getresponse()
            data = response.read().decode()

            try:
                return json.loads(data)
            except json.JSONDecodeError:
                raise Exception('响应解析失败')
        finally:
            conn.close()

    async def _make_stream_request(self, path: str, options: dict[str, Any], on_data: Callable[[dict], None]):
        """发送流式HTTP请求"""
        conn = http.client.HTTPConnection(self.host, self.port)
        try:
            conn.request(
                options['method'],
                path,
                options.get('body'),
                options.get('headers', {})
            )
            response = conn.getresponse()

            while True:
                chunk = response.read1()
                if not chunk:
                    break

                try:
                    data = json.loads(chunk)
                    on_data(data)
                except json.JSONDecodeError:
                    print('数据块解析失败')

        finally:
            conn.close()