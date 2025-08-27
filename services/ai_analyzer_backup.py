import requests
import json
import os
from typing import Dict, Optional
import re

class AIAnalyzer:
    def __init__(self, model_name: str = None):
        # 使用环境变量配置，如果没有设置则使用默认值
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen2:14b")
        self.ollama_url = f"{self.ollama_base_url}/api/chat"
    
    def analyze_stock_news(self, symbol: str, news_data: Dict, price_data: Optional[Dict] = None) -> Dict:
        """使用本地Ollama模型分析股票新闻"""
        
        news_text = "\n".join([
            f"- Title: {news['title']}\n  Summary: {news['summary']}"
            for news in news_data.get("news", [])
        ])
        
        price_info = "No price data available."
        if price_data:
            price_info = f"""
- Latest Price: ${price_data['close']}
- Open: ${price_data['open']}
- High: ${price_data['high']}
- Low: ${price_data['low']}
- Volume: {price_data['volume']}
"""
        # 使用更简单的英文提示词，提供JSON模板
        user_prompt = f"""
Analyze this stock data and return ONLY valid JSON:

Stock: {symbol}
Price: {price_info}
News: {news_text}

Return this exact JSON structure:
{{
  "overall_sentiment": "positive/negative/neutral",
  "key_points": ["point1", "point2", "point3"],
  "technical_analysis": "analysis here",
  "recommendation": "buy/hold/sell",
  "risk_level": "low/medium/high",
  "summary": "summary here",
  "reasoning": "reasoning here"
}}

Only return the JSON, nothing else.
"""
        # --- 2. 关键修改：为Ollama API构建一个更现代的payload ---
        # 使用 messages 格式，并设定 system prompt 来定义AI的角色
        payload = {
            "model": self.model_name,
            "stream": False,
            "format": "json", # 保持json格式强制
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
            # 3. 添加 options 来控制生成行为
            "options": {
                "temperature": 0.5 # 稍降低温度，让输出更稳定和可预测
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=120) # 延长超时时间
            response.raise_for_status()
            
            result = response.json()
            # 在新的 messages API 格式中，响应内容在 message.content 中
            raw_response_text = result.get("message", {}).get("content", "")

            # 打印原始响应用于调试
            print(f"Raw AI response: {raw_response_text}")
            
            # 由于我们强制了 format: "json"，可以直接尝试解析
            # 如果模型仍然返回了非JSON内容，这个解析会失败
            if not raw_response_text.strip():
                 raise ValueError("AI model returned an empty response.")

            analysis = json.loads(raw_response_text)
            
            # 增加一个检查，确保返回的不是空JSON
            if not analysis:
                # 如果返回空JSON，尝试重新生成或使用默认分析
                print("警告: 模型返回了空JSON，尝试重新生成...")
                # 这里可以添加重试逻辑或返回默认分析
                analysis = {
                    "overall_sentiment": "neutral",
                    "key_points": ["Insufficient data for detailed analysis"],
                    "technical_analysis": "Not enough data for technical analysis",
                    "recommendation": "hold",
                    "risk_level": "medium",
                    "summary": "Analysis could not be completed due to insufficient response from AI model",
                    "reasoning": "The AI model returned an empty analysis. Please try again or check the model configuration."
                }

            return {
                "symbol": symbol,
                "analysis": analysis
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始响应内容: {raw_response_text}")
            # 尝试修复不完整的JSON
            try:
                # 如果JSON不完整，尝试添加缺失的部分
                if raw_response_text.startswith('{') and not raw_response_text.endswith('}'):
                    fixed_json = raw_response_text + '}'
                    analysis = json.loads(fixed_json)
                    return {
                        "symbol": symbol,
                        "analysis": analysis
                    }
            except:
                pass
            return {
                "symbol": symbol,
                "analysis": {},
                "error": f"JSON解析错误: {str(e)}"
            }
        except Exception as e:
            print(f"Error analyzing stock {symbol}: {e}")
            raw_text = locals().get('raw_response_text', 'No response from AI')
            print(f"Raw AI response that caused error:\n---\n{raw_text}\n---")
            return {
                "symbol": symbol,
                "analysis": {},
                "error": str(e)
            }
