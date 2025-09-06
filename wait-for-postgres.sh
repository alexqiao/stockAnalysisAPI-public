#!/bin/bash
# wait-for-postgres.sh (FINAL & CORRECTED version)

set -e

echo "--- [INFO] SCRIPT STARTED ---"

# 检查环境变量是否存在
if [ -z "$DATABASE_URL" ]; then
  echo "--- [FATAL] DATABASE_URL environment variable is NOT SET. Aborting. ---"
  exit 1
fi

# 使用健壮的 sed 命令来精确解析主机和端口
# sed -e 's,.*@\(.*\):.*,\1,'  -> 提取 @ 和最后一个 : 之间的内容 (主机)
# sed -e 's,.*:\(.*\)/.*,\1,' -> 提取最后一个 : 和 / 之间的内容 (端口)
host=$(echo "$DATABASE_URL" | sed -e 's,.*@\(.*\):.*,\1,')
port=$(echo "$DATABASE_URL" | sed -e 's,.*:\(.*\)/.*,\1,')

echo "--- [INFO] Parsed HOST: '$host'"
echo "--- [INFO] Parsed PORT: '$port'"

# 再次检查解析结果，确保它们不是空的
if [ -z "$host" ] || [ -z "$port" ]; then
  echo "--- [FATAL] Failed to parse HOST or PORT from DATABASE_URL. Please check the URL format. ---"
  exit 1
fi

echo "--- [INFO] Waiting for database connection at $host:$port..."

timeout=60
start_time=$(date +%s)

while ! (</dev/tcp/$host/$port) &>/dev/null; do
  current_time=$(date +%s)
  elapsed_time=$((current_time - start_time))

  if [ $elapsed_time -ge $timeout ]; then
    echo "--- [FATAL] Timeout reached. Could not connect to database after ${timeout} seconds. ---"
    exit 1
  fi
  
  # 减少日志的冗余，只在第一次打印
  if [ $elapsed_time -lt 2 ]; then
      echo "Database is not available yet. Waiting..."
  fi
  sleep 1
done

echo "--- [SUCCESS] Database connection established. Starting application... ---"

# 执行主命令
exec "$@"