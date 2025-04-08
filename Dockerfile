# 使用Python 3.12基础镜像
FROM python:3.12-slim

# 其余配置保持不变
WORKDIR /work

COPY . /work/

RUN rm .env && mv .env.prod .env && chmod +x /work/start.sh && pip install --no-cache-dir -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

ARG PORT=8000
EXPOSE ${PORT}

CMD ["/work/start.sh"]