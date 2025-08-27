import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def debug_ai_analyzer():
    """调试AI分析器的问题"""
    ollama_url = "http://localhost:11434/api/chat"
    model_name = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
    
    print("=" * 50)
    print("调试AI分析器")
    print("=" * 50)
    
    # 测试数据
    test_symbol = "TSLA"
    test_news_data = {
        "news": [
            {
                "title": "Tesla announces new battery technology",
                "summary": "Tesla has unveiled a new battery technology that promises longer range and faster charging."
            },
            {
                "title": "Tesla stock rises on positive earnings report",
                "summary": "Tesla shares increased by 5% following better-than-expected quarterly earnings."
            }
        ]
    }
    
    test_price_data = {
        "close": 250.50,
        "open": 245.30,
        "high": 252.10,
        "low": 244.80,
        "volume": 12500000
    }
    
    news_text = "\n".join([
        f"- Title: {news['title']}\n  Summary: {news['summary']}"
        for news in test_news_data.get("news", [])
    ])
    
    price_info = f"""
- Latest Price: ${test_price_data['close']}
- Open: ${test_price_data['open']}
- High: ${test_price_data['high']}
- Low: ${test_price_data['low']}
- Volume: {test_price_data['volume']}
"""
    
    user_prompt = f"""
Analyze the following stock data and return ONLY a JSON object:

Stock Symbol: {test_symbol}

Price Data:
{price_info}

News Summary:
{news_text}

Return a JSON object with these fields:
- overall_sentiment (positive/negative/neutral)
- key_points (array of strings)
- technical_analysis (string)
- recommendation (buy/hold/sell)
- risk_level (low/medium/high)
- summary (string)
- reasoning (string)

Return ONLY the JSON object, no other text.
"""
    
    print("完整的提示词:")
    print(user_prompt)
    print("-" * 50)
    
    # 构建payload
    payload = {
        "model": model_name,
        "stream": False,
        "format": "json",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert financial analyst. Your goal is to provide a detailed, data-driven stock analysis based on the user's input. You must respond ONLY with a single, complete, and valid JSON object."
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "options": {
            "temperature": 0.5
        }
    }
    
    print("发送的Payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("-" * 50)
    
    try:
        print("发送请求到Ollama...")
        response = requests.post(ollama_url, json=payload, timeout=120)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("完整响应:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            raw_response_text = result.get("message", {}).get("content", "")
            print(f"\n原始响应文本: {repr(raw_response_text)}")
            
            if raw_response_text.strip():
                try:
                    analysis = json.loads(raw_response_text)
                    print("✅ JSON解析成功!")
                    print(json.dumps(analysis, indent=2, ensure_ascii=False))
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析错误: {e}")
            else:
                print("❌ 模型返回了空响应")
                
        else:
            print(f"❌ 错误响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ai_analyzer()
