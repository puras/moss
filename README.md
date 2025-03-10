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