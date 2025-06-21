#!/bin/sh
CONFIG=/config/config.yaml
if [ ! -f "$CONFIG" ]; then
  echo "FATAL: $CONFIG 不存在，容器退出"
  ls -l /config
  exit 1
fi
exec python /opt/app/app.py
