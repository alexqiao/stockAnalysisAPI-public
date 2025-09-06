#!/bin/sh
# wait-for-postgres.sh

set -e

# 从 DATABASE_URL 中提取主机和端口
# 格式: postgresql://user:password@host:port/dbname
host=$(echo $DATABASE_URL | sed -e 's,.*@\(.*\):.*,\1,')
port=$(echo $DATABASE_URL | sed -e 's,.*@.*:\(.*\)/.*,\1,')

echo "Waiting for postgres at $host:$port..."

# 使用 nc (netcat) 检查端口是否打开
# -z 选项表示只扫描端口，不发送数据
# -w1 选项设置1秒超时
while ! nc -z $host $port; do
  sleep 1
done

echo "PostgreSQL started"

# 执行传递给此脚本的命令 (例如: uvicorn run:app ...)
exec "$@"