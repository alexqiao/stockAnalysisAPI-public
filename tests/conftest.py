"""测试配置和fixture"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from run import app
import os

# 使用SQLite内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def db():
    """创建测试数据库"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """创建测试客户端"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client):
    """创建认证头"""
    # 注册用户
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    client.post("/api/register", json=user_data)
    
    # 登录获取token
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/api/token", data=login_data)
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def mock_env_vars():
    """设置测试环境变量"""
    os.environ["ALPHA_VANTAGE_API_KEY"] = "test_api_key"
    os.environ["OLLAMA_API_URL"] = "http://localhost:11434"
    os.environ["SECRET_KEY"] = "test_secret_key"
    os.environ["ALGORITHM"] = "HS256"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
