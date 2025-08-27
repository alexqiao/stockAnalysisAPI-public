"""认证流程集成测试"""
import pytest

class TestAuthFlow:
    
    def test_user_registration_success(self, client):
        """测试用户注册成功"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123"
        }
        
        response = client.post("/api/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "password" not in data
    
    def test_user_registration_duplicate_username(self, client):
        """测试重复用户名注册"""
        user_data = {
            "username": "testuser",
            "email": "test1@example.com",
            "password": "testpass123"
        }
        
        # 第一次注册
        response1 = client.post("/api/register", json=user_data)
        assert response1.status_code == 200
        
        # 第二次注册相同用户名
        user_data["email"] = "test2@example.com"
        response2 = client.post("/api/register", json=user_data)
        
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Username already registered"
    
    def test_user_registration_duplicate_email(self, client):
        """测试重复邮箱注册"""
        user_data = {
            "username": "testuser1",
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        # 第一次注册
        response1 = client.post("/api/register", json=user_data)
        assert response1.status_code == 200
        
        # 第二次注册相同邮箱
        user_data["username"] = "testuser2"
        response2 = client.post("/api/register", json=user_data)
        
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Email already registered"
    
    def test_user_login_success(self, client):
        """测试用户登录成功"""
        # 先注册用户
        user_data = {
            "username": "loginuser",
            "email": "login@example.com",
            "password": "loginpass123"
        }
        client.post("/api/register", json=user_data)
        
        # 登录
        login_data = {
            "username": "loginuser",
            "password": "loginpass123"
        }
        response = client.post("/api/token", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_user_login_invalid_credentials(self, client):
        """测试无效凭据登录"""
        # 先注册用户
        user_data = {
            "username": "loginuser",
            "email": "login@example.com",
            "password": "loginpass123"
        }
        client.post("/api/register", json=user_data)
        
        # 使用错误密码登录
        login_data = {
            "username": "loginuser",
            "password": "wrongpassword"
        }
        response = client.post("/api/token", data=login_data)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"
    
    def test_user_login_nonexistent_user(self, client):
        """测试不存在的用户登录"""
        login_data = {
            "username": "nonexistent",
            "password": "somepassword"
        }
        response = client.post("/api/token", data=login_data)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"
    
    def test_get_current_user_success(self, client, auth_headers):
        """测试获取当前用户信息"""
        response = client.get("/api/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data
    
    def test_get_current_user_no_token(self, client):
        """测试无token访问用户信息"""
        response = client.get("/api/users/me")
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """测试无效token访问用户信息"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/users/me", headers=headers)
        
        assert response.status_code == 401
