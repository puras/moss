# 使用Python 3.12基础镜像
FROM python:3.12-slim

# 其余配置保持不变
WORKDIR /work

COPY . /work/

RUN chmod +x /work/start.sh && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && pip install --no-cache-dir -r requirements.txt

ARG PORT=8000
EXPOSE ${PORT}

CMD ["/work/start.sh"]