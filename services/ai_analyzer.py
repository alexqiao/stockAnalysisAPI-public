import requests
import json
import os
from typing import Dict, Optional
import re
from config import Config

class AIAnalyzer:
    def __init__(self, model_name: str = None):
        self.config = Config()
        self.model_type = self.config.AI_MODEL_TYPE.lower()
        
        if self.model_type == "ollama":
            # Ollama配置
            self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen3:14b")
            self.ollama_url = f"{self.ollama_base_url}/api/chat"
        elif self.model_type == "deepseek":
            # DeepSeek配置
            self.deepseek_api_key = self.config.DEEPSEEK_API_KEY
            self.deepseek_api_url = self.config.DEEPSEEK_API_URL
            self.model_name = model_name or self.config.DEEPSEEK_MODEL
        else:
            raise ValueError(f"Unsupported AI model type: {self.model_type}")
    def extract_json_from_qwen_output(self,text: str) -> dict or None:
        """
        使用正则表达式从Qwen模型输出中提取JSON内容。
        Args:
            text: 包含<think>和JSON部分的字符串。
        Returns:
            如果找到并成功解析，返回Python字典；否则返回None。
        """
        # 匹配以 `{` 开头，以 `}` 结尾的JSON对象，并使用非贪婪模式 `*?`
        # 以确保只匹配第一个完整的JSON对象，而非整个字符串。
        # re.DOTALL 标志允许 `.` 匹配换行符，这在多行JSON中非常重要。
        match = re.search(r'\{.*\}', text, re.DOTALL)
        
        if match:
            json_string = match.group(0)
            try:
                # 使用json模块将提取的字符串解析为Python字典
                json_data = json.loads(json_string)
                return json_data
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                return None
        else:
            print("未找到JSON内容。")
            return None

    
    def analyze_stock_news(self, symbol: str, news_data: Dict, price_data: Optional[Dict] = None) -> Dict:
        """
        Analyzes stock news using a local Ollama model with robust error handling.
        """
        
        news_text = "\n".join([
            f"- Title: {news['title']}\n  Summary: {news['summary']}"
            for news in news_data.get("news", [])
        ])
        
        price_info = "No price data available."
        if price_data:
            price_info = f"""
- Latest Price: ${price_data.get('close', 'N/A')}
- Open: ${price_data.get('open', 'N/A')}
- High: ${price_data.get('high', 'N/A')}
- Low: ${price_data.get('low', 'N/A')}
- Volume: {price_data.get('volume', 'N/A')}
"""
        
        # A slightly improved and clearer prompt for the model
        user_prompt = f"""
You are an expert financial analyst. Your task is to analyze the provided stock data for {symbol}.
Based on the news and price information, generate a comprehensive analysis.

**Input Data:**
- **Price Information:**
{price_info}
- **Recent News Articles:**
{news_text}

**Your Task:**
Respond with a single, valid JSON object that contains your complete analysis. The JSON object must have the following keys:
- "overall_sentiment": (string) Must be one of "positive", "negative", or "neutral".
- "key_points": (array of strings) A list of the most important takeaways from the news.
- "technical_analysis": (string) A brief analysis based on the provided price data.
- "recommendation": (string) Your investment recommendation. Must be one of "buy", "hold", or "sell".
- "risk_level": (string) The perceived investment risk. Must be one of "low", "medium", or "high".
- "summary": (string) A concise summary of your overall analysis.
- "reasoning": (string) A clear explanation for your recommendation and summary.

Do not include any text, explanations, or code formatting marks like ```json before or after the JSON object.
"""

        # 根据模型类型选择不同的API调用方式
        if self.model_type == "ollama":
            payload = {
                "model": self.model_name,
                "stream": False,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful financial analysis assistant that responds only with a single, valid JSON object."
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
            
            try:
                response = requests.post(self.ollama_url, json=payload, timeout=120)
                response.raise_for_status()
                
                result = response.json()
                raw_response_text = result.get("message", {}).get("content", "").strip()
                
                print(f"Raw AI response from Ollama: {raw_response_text}")
                
            except requests.exceptions.RequestException as e:
                error_message = f"Could not connect to Ollama service: {e}"
                print(f"Error analyzing stock {symbol}: {error_message}")
                return {"symbol": symbol, "analysis": {}, "error": error_message}
                
        elif self.model_type == "deepseek":
            if not self.deepseek_api_key:
                error_message = "DeepSeek API key is not configured"
                print(f"Error: {error_message}")
                return {"symbol": symbol, "analysis": {}, "error": error_message}
                
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful financial analysis assistant that responds only with a single, valid JSON object."
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "temperature": 0.5,
                "response_format": {"type": "json_object"}
            }
            
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            try:
                response = requests.post(self.deepseek_api_url, json=payload, headers=headers, timeout=120)
                response.raise_for_status()
                
                result = response.json()
                raw_response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                
                print(f"Raw AI response from DeepSeek: {raw_response_text}")
                
            except requests.exceptions.RequestException as e:
                error_message = f"Could not connect to DeepSeek API: {e}"
                print(f"Error analyzing stock {symbol}: {error_message}")
                return {"symbol": symbol, "analysis": {}, "error": error_message}
        
        else:
            error_message = f"Unsupported AI model type: {self.model_type}"
            print(f"Error: {error_message}")
            return {"symbol": symbol, "analysis": {}, "error": error_message}

        # 处理AI响应（通用逻辑）
        # Gracefully handle empty or malformed responses from the AI model
        if not raw_response_text:
            error_message = "AI model returned an empty response. This could be due to high server load, a model configuration issue, or an overly restrictive prompt."
            print(f"Warning: {error_message}")
            return {"symbol": symbol, "analysis": {}, "error": error_message}

        try:
            # 对于DeepSeek，由于使用了response_format=json_object，可以直接解析JSON
            if self.model_type == "deepseek":
                analysis = json.loads(raw_response_text)
            else:
                # 对于Ollama，使用原有的JSON提取逻辑
                extracted_json = self.extract_json_from_qwen_output(raw_response_text)
                extracted_json = json.dumps(extracted_json, indent=2, ensure_ascii=False)
                analysis = json.loads(extracted_json)
            
            if not isinstance(analysis, dict) or not analysis:
                error_message = "AI model returned valid JSON, but it was empty or not an object."
                print(f"Warning: {error_message}")
                return {"symbol": symbol, "analysis": {}, "error": error_message}

            return {"symbol": symbol, "analysis": analysis}
        
        except json.JSONDecodeError as e:
            error_message = f"Failed to parse JSON from AI model. Error: {e}"
            print(f"Error: {error_message}\nRaw Response was: {raw_response_text}")
            return {"symbol": symbol, "analysis": {}, "error": error_message}
            
        except Exception as e:
            error_message = f"An unexpected error occurred during AI analysis: {e}"
            print(f"Error analyzing stock {symbol}: {error_message}")
            return {"symbol": symbol, "analysis": {}, "error": error_message}
