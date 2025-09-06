from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import engine, Base
from app.api.main_api_router import router
from app.api.admin_router import router as admin_router
from app.web.routes import router as web_router
import uvicorn

# --- 关键修改 ---
# Base.metadata.create_all(bind=engine) # <--- 1. 我们将删除这一行

# 创建一个函数来执行数据库表的创建
def init_db():
    print("Application startup: Attempting to create database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables checked/created successfully.")
    except Exception as e:
        print(f"FATAL: Could not connect to the database to create tables: {e}")
        # 重新抛出异常，这将使应用在数据库无法访问时启动失败，这是正确的行为
        raise

# 创建FastAPI应用
app = FastAPI(
    title="股票分析API",
    description="基于新闻和AI的股票分析系统",
    version="1.0.0"
)

# --- 关键修改 ---
# 2. 将数据库初始化注册到 FastAPI 的 startup 事件中
@app.on_event("startup")
def on_startup():
    init_db()


# --- 从这里开始，您的其余代码保持不变 ---

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(web_router)

# 配置静态文件服务
app.mount("/static", StaticFiles(directory="app/static"), name="static")

if __name__ == "__main__":
    import sys
    port = 8000
    if len(sys.argv) > 1 and sys.argv[1] == "--port":
        try:
            port = int(sys.argv[2])
        except (IndexError, ValueError):
            print("Invalid port number, using default port 8000")
    # 注意：生产部署时不应使用 reload=True
    uvicorn.run("run:app", host="0.0.0.0", port=port, reload=True)