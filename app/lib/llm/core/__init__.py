import http.client
import json
from typing import Dict, Any, Coroutine, Union
from urllib.parse import urlparse

from app.lib.llm.core.ollama import OllamaAPI


class LLMClient:
    """LLM 客户端类"""

    def __init__(self, config: Dict[str, str] = None):
        """
        创建 LLM 客户端实例
        Args:
            config: 配置信息
                provider: 提供商名称，如 'openai', 'ollama', 'zhipu' 等
                endpoint: API 端点，如 'https://api.openai.com/v1/'
                api_key: API 密钥（如果需要）
                model: 模型名称，如 'gpt-3.5-turbo', 'llama2' 等
        """
        config = config or {}
        self.provider = config.get('provider', 'openai')
        self.endpoint = config.get('endpoint', '')
        self.api_key = config.get('apiKey', '')
        self.model = config.get('model', '')
        self.client = None

        # 对于 Ollama，使用专门的客户端
        if self.provider.lower() == 'ollama':
            url = urlparse(self.endpoint)
            self.client = OllamaAPI({
                "host": url.hostname,
                "port": url.port or 11434,
                "model": self.model
            })


    async def chat(self, prompt: Union[str, list[dict]], options: dict = None) -> dict:
        """
        生成对话响应
        Args:
            prompt: 用户输入的提示词或对话历史
            options: 可选参数
        Returns:
            模型响应
        """
        options = options or {}
        messages = prompt if isinstance(prompt, list) else [{'role': 'user', 'content': prompt}]

        # 根据不同提供商调用不同的 API
        provider = self.provider.lower()
        if provider == 'ollama':
            return await self._chat_ollama(messages, options)
        elif provider in ['openai', 'siliconflow', 'deepseek']:  # 兼容 OpenAI 接口
            return await self._chat_openai(messages, options)
        elif provider == 'zhipu':  # 智谱 AI
            return await self._chat_zhipu(messages, options)
        else:
            # 默认尝试 OpenAI 兼容接口
            return await self._chat_openai(messages, options)

    async def get_models(self) -> list[dict[str, Any]] | None:
        """
        获取模型列表（仅支持 Ollama）
        Returns:
            模型列表
        """
        if self.provider.lower() == 'ollama':
            return await self.client.get_models()
        else:
            raise Exception('当前提供商不支持获取模型列表')

    async def _chat_ollama(self, messages: list[dict], options: dict) -> dict:
        """调用 Ollama API"""
        try:
            last_message = messages[-1]
            prompt = last_message['content']

            return await self.client.chat(prompt, {
                **options,
                'model': self.model or self.client.model
            })
        except Exception as error:
            print('Ollama API 调用出错:', str(error))
            raise

    async def _chat_ollama_stream(self, messages: list[dict], options: dict):
        """调用 Ollama 流式 API"""
        try:
            last_message = messages[-1]
            prompt = last_message['content']

            async def stream_generator():
                async for data in self.client.chat_stream(prompt, {
                    **options,
                    'model': self.model or self.client.model
                }):
                    if data.get('response'):
                        yield data['response'].encode()
                    if data.get('done'):
                        break

            return stream_generator()
        except Exception as error:
            print('Ollama 流式 API 调用出错:', str(error))
            raise

    async def _chat_openai(self, messages: list[dict], options: dict) -> dict:
        """调用 OpenAI 兼容的 API"""
        try:
            url = urlparse(self.endpoint)
            path = url.path
            if '/chat/completions' not in path:
                path = f"{path.rstrip('/')}/chat/completions"

            request_options = {
                'temperature': options.get('temperature', 0.7),
                'top_p': options.get('top_p', 0.9),
                'max_tokens': options.get('max_tokens', 2048),
                'model': self.model,
                'messages': messages
            }

            return await self._make_http_request(
                url.geturl(),
                method='POST',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                },
                body=json.dumps(request_options)
            )
        except Exception as error:
            print('OpenAI 兼容 API 调用出错:', str(error))
            raise

    async def _chat_openai_stream(self, messages: list[dict], options: dict):
        """调用 OpenAI 兼容的流式 API"""
        try:
            url = urlparse(self.endpoint)
            path = url.path
            if '/chat/completions' not in path:
                path = f"{path.rstrip('/')}/chat/completions"

            request_options = {
                'temperature': options.get('temperature', 0.7),
                'top_p': options.get('top_p', 0.9),
                'max_tokens': options.get('max_tokens', 2048),
                'model': self.model,
                'messages': messages,
                'stream': True
            }

            async def stream_generator():
                conn = (http.client.HTTPSConnection(url.hostname, url.port or 443)
                        if url.scheme == 'https' else
                        http.client.HTTPConnection(url.hostname, url.port or 80))

                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}',
                    'Accept': 'text/event-stream'
                }

                try:
                    conn.request('POST', path, json.dumps(request_options), headers)
                    response = conn.getresponse()

                    if response.status != 200:
                        raise Exception(f'HTTP error! status: {response.status}')

                    while True:
                        chunk = response.read1()
                        if not chunk:
                            break

                        text = chunk.decode()
                        for line in text.split('\n'):
                            if line.startswith('data: '):
                                data = line[6:]
                                if data == '[DONE]':
                                    return
                                try:
                                    parsed = json.loads(data)
                                    content = parsed.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                    if content:
                                        yield content.encode()
                                except json.JSONDecodeError:
                                    print('解析 SSE 数据失败')

                finally:
                    conn.close()

            return stream_generator()
        except Exception as error:
            print('OpenAI 兼容流式 API 调用出错:', str(error))
            raise

    async def _chat_zhipu(self, messages: list[dict], options: dict) -> dict:
        """调用智谱 AI API"""
        try:
            zhipu_messages = [
                {
                    'role': 'assistant' if msg['role'] == 'assistant' else 'user',
                    'content': msg['content']
                }
                for msg in messages
            ]

            request_options = {
                'temperature': options.get('temperature', 0.7),
                'top_p': options.get('top_p', 0.9),
                'max_tokens': options.get('max_tokens', 2048),
                'model': self.model,
                'messages': zhipu_messages
            }

            return await self._make_http_request(
                self.endpoint,
                method='POST',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                },
                body=json.dumps(request_options)
            )
        except Exception as error:
            print('智谱 AI API 调用出错:', str(error))
            raise

    async def _chat_zhipu_stream(self, messages: list[dict], options: dict):
        """调用智谱 AI 流式 API"""
        try:
            zhipu_messages = [
                {
                    'role': 'assistant' if msg['role'] == 'assistant' else 'user',
                    'content': msg['content']
                }
                for msg in messages
            ]

            request_options = {
                'temperature': options.get('temperature', 0.7),
                'top_p': options.get('top_p', 0.9),
                'max_tokens': options.get('max_tokens', 2048),
                'model': self.model,
                'messages': zhipu_messages,
                'stream': True
            }

            async def stream_generator():
                url = urlparse(self.endpoint)
                conn = (http.client.HTTPSConnection(url.hostname, url.port or 443)
                        if url.scheme == 'https' else
                        http.client.HTTPConnection(url.hostname, url.port or 80))

                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}',
                    'Accept': 'text/event-stream'
                }

                try:
                    conn.request('POST', url.path, json.dumps(request_options), headers)
                    response = conn.getresponse()

                    if response.status != 200:
                        raise Exception(f'HTTP error! status: {response.status}')

                    while True:
                        chunk = response.read1()
                        if not chunk:
                            break

                        try:
                            data = json.loads(chunk)
                            if data.get('data'):
                                content = data['data'].get('content', '')
                                if content:
                                    yield content.encode()
                            if data.get('meta', {}).get('is_end'):
                                break
                        except json.JSONDecodeError:
                            print('处理智谱 AI 流数据出错')

                finally:
                    conn.close()

            return stream_generator()
        except Exception as error:
            print('智谱 AI 流式 API 调用出错:', str(error))
            raise

    async def _make_http_request(self, url: str, method: str, headers: dict, body: str = None) -> dict:
        """发送 HTTP 请求"""
        url_parts = urlparse(url)
        is_https = url_parts.scheme == 'https'
        conn = (http.client.HTTPSConnection(url_parts.hostname, url_parts.port or 443)
                if is_https else
                http.client.HTTPConnection(url_parts.hostname, url_parts.port or 80))

        try:
            conn.request(method, url_parts.path, body, headers)
            response = conn.getresponse()
            data = response.read().decode()

            if 200 <= response.status < 300:
                return json.loads(data)
            else:
                raise Exception(f'请求失败，状态码: {response.status}, 响应: {data}')
        except json.JSONDecodeError:
            raise Exception('响应解析失败')
        finally:
            conn.close()