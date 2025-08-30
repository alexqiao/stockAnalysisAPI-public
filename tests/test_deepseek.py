#!/usr/bin/env python3
"""
DeepSeek API 连接测试脚本
用于测试DeepSeek API是否能够正常工作
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_deepseek_connection():
    """测试DeepSeek API连接"""
    
    # 获取配置
    api_key = os.getenv("DEEPSEEK_API_KEY")
    api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    if not api_key or api_key == "your_deepseek_api_key_here":
        print("❌ DeepSeek API密钥未配置或为默认值")
        print("请在.env文件中设置正确的DEEPSEEK_API_KEY")
        return False
    
    print(f"🔗 测试DeepSeek API连接...")
    print(f"API URL: {api_url}")
    print(f"Model: {model}")
    
    # 准备测试请求
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是一个有用的助手，请用中文回复。"
            },
            {
                "role": "user",
                "content": "你好，请回复'连接成功'来确认API连接正常。"
            }
        ],
        "temperature": 0.1,
        "max_tokens": 50
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("📡 发送测试请求...")
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        print(f"✅ DeepSeek API连接成功！")
        print(f"🤖 模型回复: {content}")
        print(f"📊 使用token数: {result.get('usage', {}).get('total_tokens', 'N/A')}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ DeepSeek API连接失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"HTTP状态码: {e.response.status_code}")
            print(f"错误响应: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        return False

def test_ai_model_selection():
    """测试AI模型选择配置"""
    
    model_type = os.getenv("AI_MODEL_TYPE", "ollama").lower()
    print(f"\n🤖 当前AI模型类型配置: {model_type}")
    
    if model_type == "deepseek":
        print("✅ 配置为使用DeepSeek在线模型")
    elif model_type == "ollama":
        print("✅ 配置为使用本地Ollama模型")
    else:
        print(f"❌ 未知的AI模型类型: {model_type}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("DeepSeek API 连接测试")
    print("=" * 50)
    
    # 测试模型选择配置
    config_ok = test_ai_model_selection()
    
    # 如果配置为DeepSeek，测试连接
    model_type = os.getenv("AI_MODEL_TYPE", "ollama").lower()
    if model_type == "deepseek":
        connection_ok = test_deepseek_connection()
        
        if connection_ok:
            print("\n🎉 所有测试通过！DeepSeek API配置正确。")
        else:
            print("\n💥 DeepSeek API连接测试失败，请检查配置。")
            sys.exit(1)
    else:
        print("\nℹ️  当前配置为使用Ollama模型，跳过DeepSeek连接测试。")
        print("如需测试DeepSeek，请在.env文件中设置 AI_MODEL_TYPE=deepseek")
