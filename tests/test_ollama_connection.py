import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_ollama_connection():
    """测试Ollama服务连接"""
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
    
    print(f"测试Ollama连接...")
    print(f"OLLAMA_BASE_URL: {ollama_base_url}")
    print(f"OLLAMA_MODEL: {ollama_model}")
    
    # 测试基础连接
    try:
        # 测试API端点
        tags_url = f"{ollama_base_url}/api/tags"
        print(f"测试连接: {tags_url}")
        
        response = requests.get(tags_url, timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            available_models = [m.get("name") for m in models]
            print(f"✓ Ollama服务运行正常")
            print(f"可用模型: {available_models}")
            
            if ollama_model in available_models:
                print(f"✓ 配置的模型 '{ollama_model}' 可用")
                return True
            else:
                print(f"✗ 配置的模型 '{ollama_model}' 不可用")
                print(f"请检查您的Ollama模型列表，可用模型: {available_models}")
                return False
        else:
            print(f"✗ Ollama服务响应异常: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到Ollama服务")
        print("请确保Ollama正在运行，可以尝试在终端运行: ollama serve")
        return False
    except requests.exceptions.Timeout:
        print("✗ 连接Ollama服务超时")
        return False
    except Exception as e:
        print(f"✗ 连接Ollama服务时出错: {e}")
        return False

def test_chat_endpoint():
    """测试聊天API端点"""
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
    
    chat_url = f"{ollama_base_url}/api/chat"
    print(f"\n测试聊天API端点: {chat_url}")
    
    try:
        # 发送一个简单的测试消息
        payload = {
            "model": ollama_model,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, are you working?"
                }
            ],
            "stream": False
        }
        
        response = requests.post(chat_url, json=payload, timeout=30)
        print(f"聊天API响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ 聊天API工作正常")
            print(f"响应: {result.get('message', {}).get('content', 'No content')}")
            return True
        else:
            print(f"✗ 聊天API响应异常: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 测试聊天API时出错: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Ollama连接测试工具")
    print("=" * 50)
    
    connection_ok = test_ollama_connection()
    
    if connection_ok:
        print("\n" + "="*30)
        print("开始测试聊天API...")
        chat_ok = test_chat_endpoint()
        
        if chat_ok:
            print("\n✅ 所有测试通过！Ollama服务配置正确。")
        else:
            print("\n❌ 聊天API测试失败，请检查Ollama服务配置。")
    else:
        print("\n❌ Ollama连接测试失败，请先解决连接问题。")
