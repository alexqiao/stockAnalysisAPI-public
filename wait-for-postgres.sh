#!/bin/bash
# wait-for-postgres.sh (version 2, no `nc` required)

set -e

# 从 DATABASE_URL 中提取主机和端口
# 格式: postgresql://user:password@host:port/dbname
host=$(echo $DATABASE_URL | sed -e 's,.*@\(.*\):.*,\1,')
port=$(echo $DATABASE_URL | sed -e 's,.*@.*:\(.*\)/.*,\1,')

echo "Waiting for postgres at $host:$port..."

# 使用 bash 内置的 /dev/tcp 功能检查端口
# 这避免了对 `nc` (netcat) 的依赖
# `&>/dev/null` 将标准输出和标准错误都重定向到 null，保持日志干净
while ! (</dev/tcp/$host/$port) &>/dev/null; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL started"

# 执行传递给此脚本的命令 (例如: uvicorn run:app ...)
exec "$@"