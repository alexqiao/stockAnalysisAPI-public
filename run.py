from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import engine, Base
from app.api.main_api_router import router
from app.api.admin_router import router as admin_router
from app.web.routes import router as web_router
import uvicorn

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="股票分析API",
    description="基于新闻和AI的股票分析系统",
    version="1.0.0"
)

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
    uvicorn.run("run:app", host="0.0.0.0", port=port, reload=True)
