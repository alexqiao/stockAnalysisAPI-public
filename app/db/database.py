from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
import os
from dotenv import load_dotenv

load_dotenv()

# Render 会通过环境变量提供一个 'postgresql://...' 格式的 URL
DATABASE_URL = os.getenv("DATABASE_URL")

# 移除针对 SQLite 的 'check_same_thread' 逻辑
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 不再需要在这里创建表，可以使用 Alembic 或首次启动时创建
# Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
