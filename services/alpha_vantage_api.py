import requests
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import certifi

load_dotenv()

class AlphaVantageAPI:
    def __init__(self):
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY not found in environment variables")
        self.base_url = "https://www.alphavantage.co/query"
        # 2. 创建一个可复用的 Session 对象
        self.session = requests.Session()
    
    def get_stock_news(self, symbol: str) -> Optional[Dict]:
        """获取股票新闻"""
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": symbol,
            "apikey": self.api_key,
            "limit": 10
        }
        
        try:
            # 3. 使用 session 对象发送请求，并显式指定 verify 路径
            response = self.session.get(
                self.base_url, 
                params=params, 
                verify=certifi.where() # <--- 关键修改
            )

            response.raise_for_status()
            data = response.json()
            
            if "feed" in data:
                return {
                    "symbol": symbol,
                    "news": [
                        {
                            "title": item.get("title", ""),
                            "summary": item.get("summary", ""),
                            "url": item.get("url", ""),
                            "time_published": item.get("time_published", ""),
                            "source": item.get("source", ""),
                            "sentiment": item.get("overall_sentiment_score", 0)
                        }
                        for item in data["feed"][:5]
                    ]
                }
            return None
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return None
    
    def get_daily_prices(self, symbol: str) -> Optional[Dict]:
        """获取日K数据"""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key,
            "outputsize": "compact"
        }
        
        try:
            # 3. 使用 session 对象发送请求，并显式指定 verify 路径
            response = self.session.get(
                self.base_url, 
                params=params, 
                verify=certifi.where() # <--- 关键修改
            )
            response.raise_for_status()
            data = response.json()
            
            if "Time Series (Daily)" in data:
                daily_data = data["Time Series (Daily)"]
                latest_date = max(daily_data.keys())
                latest_data = daily_data[latest_date]
                
                return {
                    "symbol": symbol,
                    "date": latest_date,
                    "open": float(latest_data["1. open"]),
                    "high": float(latest_data["2. high"]),
                    "low": float(latest_data["3. low"]),
                    "close": float(latest_data["4. close"]),
                    "volume": int(latest_data["5. volume"])
                }
            return None
        except Exception as e:
            print(f"Error fetching prices for {symbol}: {e}")
            return None
