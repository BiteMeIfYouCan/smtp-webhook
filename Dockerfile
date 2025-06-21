FROM python:3.11-alpine

WORKDIR /opt/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py entrypoint.sh ./
RUN chmod +x entrypoint.sh

# 挂载配置目录
VOLUME /config
EXPOSE 8080
ENTRYPOINT ["./entrypoint.sh"]
