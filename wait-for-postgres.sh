#!/bin/bash
# wait-for-postgres.sh (ULTIMATE DEBUGGING version)

set -e

echo "--- [DEBUG] SCRIPT STARTED ---"
echo "--- [DEBUG] Verifying DATABASE_URL variable..."

# 检查环境变量是否存在且不为空
if [ -z "$DATABASE_URL" ]; then
  echo "--- [FATAL] DATABASE_URL environment variable is NOT SET or IS EMPTY. Aborting. ---"
  exit 1
else
  # 打印出脚本接收到的完整 URL，让我们检查它是否正确
  echo "--- [DEBUG] Received DATABASE_URL: '$DATABASE_URL'"
fi

# 尝试解析主机和端口
# 使用更健壮的 awk 命令代替 sed，以更好地处理特殊字符
host=$(echo "$DATABASE_URL" | awk -F'[@:/]' '{print $6}')
port=$(echo "$DATABASE_URL" | awk -F'[:/]' '{print $5}')

echo "--- [DEBUG] Parsed HOST: '$host'"
echo "--- [DEBUG] Parsed PORT: '$port'"

# 检查解析结果是否为空
if [ -z "$host" ] || [ -z "$port" ]; then
  echo "--- [FATAL] Failed to parse HOST or PORT from DATABASE_URL. Please check the URL format. ---"
  exit 1
fi

echo "--- [INFO] Waiting for database at $host:$port..."

# 设置一个超时时间（例如60秒），防止无限循环
timeout=60
start_time=$(date +%s)

# 循环检查连接
while ! (</dev/tcp/$host/$port) &>/dev/null; do
  current_time=$(date +%s)
  elapsed_time=$((current_time - start_time))

  if [ $elapsed_time -ge $timeout ]; then
    echo "--- [FATAL] Timeout reached. Could not connect to database after ${timeout} seconds. ---"
    exit 1
  fi

  echo "Postgres is unavailable - sleeping for 2 seconds..."
  sleep 2
done

echo "--- [SUCCESS] PostgreSQL is ready. Proceeding to launch application. ---"

# 执行传递给脚本的命令 (uvicorn...)
exec "$@"