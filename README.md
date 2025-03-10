MOSS
----

在AI，特别是大模型领域的各种尝试内容

# 为Huggingface增加代理

修改源码：

```
/miniconda3/envs/unsloth-env/lib/python3.12/site-packages/huggingface_hub
```

在头部增加

```python
import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
```

## 安装Unsloth

```
pip install unsloth
pip uninstall unsloth -y && pip install --upgrade --no-cache-dir --no-deps git+https://github.com/unslothai/unsloth.git
```

## Ollama创建本地模型

```
ollama create [model_name] --file /YOUR/PATH/TO/Modelfile
#  示例
ollama create DeepSeek-R1-Distill-Qwen-1.5B_f16 --file ./dist/DeepSeek-R1-Distill-Qwen-1.5B_f16.mf
ollama create DeepSeek-R1-Distill-Qwen-1.5B-ming --file ./dist/DeepSeek-R1-Distill-Qwen-1.5B-ming.mf
```