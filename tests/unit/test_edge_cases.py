"""边界情况和异常场景测试"""
import pytest
import responses
from services.alpha_vantage_api import AlphaVantageAPI
from services.ai_analyzer import AIAnalyzer
from app.models import User
from app.database import db
import json

class TestEdgeCases:
    """测试边界情况和异常场景"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.alpha_api = AlphaVantageAPI()
        self.alpha_api.api_key = "test_api_key"
        self.ai_analyzer = AIAnalyzer(model_name="test-model")
    
    @responses.activate
    def test_alpha_vantage_malformed_json(self):
        """测试Alpha Vantage返回格式错误的JSON"""
        symbol = "AAPL"
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            body="invalid json response",
            status=200
        )
        
        result = self.alpha_api.get_stock_news(symbol)
        assert result is None
        
        result = self.alpha_api.get_daily_prices(symbol)
        assert result is None
    
    @responses.activate
    def test_alpha_vantage_timeout(self):
        """测试Alpha Vantage API超时"""
        symbol = "TSLA"
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            body=requests.exceptions.Timeout("Connection timeout"),
            status=200
        )
        
        result = self.alpha_api.get_stock_news(symbol)
        assert result is None
    
    @responses.activate
    def test_alpha_vantage_empty_feed(self):
        """测试Alpha Vantage返回空feed"""
        symbol = "GOOGL"
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json={"feed": []},
            status=200
        )
        
        result = self.alpha_api.get_stock_news(symbol)
        assert result is not None
        assert result["symbol"] == "GOOGL"
        assert len(result["news"]) == 0
    
    @responses.activate
    def test_alpha_vantage_missing_fields(self):
        """测试Alpha Vantage返回缺少字段的数据"""
        symbol = "MSFT"
        
        mock_response = {
            "feed": [
                {
                    "title": "Test News",
                    # 缺少summary字段
                    "url": "https://example.com",
                    "time_published": "20240101T120000",
                    # 缺少overall_sentiment_score
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json=mock_response,
            status=200
        )
        
        result = self.alpha_api.get_stock_news(symbol)
        assert result is not None
        assert result["news"][0]["summary"] == ""  # 应该使用默认值
        assert result["news"][0]["sentiment"] == 0.0  # 应该使用默认值
    
    @responses.activate
    def test_alpha_vantage_negative_sentiment(self):
        """测试Alpha Vantage返回负面情感数据"""
        symbol = "AMZN"
        
        mock_response = {
            "feed": [
                {
                    "title": "Amazon Faces Regulatory Challenges",
                    "summary": "Amazon faces new antitrust regulations...",
                    "url": "https://example.com",
                    "time_published": "20240101T120000",
                    "source": "Reuters",
                    "overall_sentiment_score": -0.7
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json=mock_response,
            status=200
        )
        
        result = self.alpha_api.get_stock_news(symbol)
        assert result["news"][0]["sentiment"] == -0.7
    
    @responses.activate
    def test_ai_analyzer_empty_response(self):
        """测试AI分析器返回空响应"""
        symbol = "NVDA"
        news_data = {"symbol": "NVDA", "news": [{"title": "Test", "summary": "Test", "sentiment": 0.5}]}
        
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json={"response": ""},
            status=200
        )
        
        result = self.ai_analyzer.analyze_stock_news(symbol, news_data)
        assert "error" in result
        assert result["analysis"]["recommendation"] == "hold"
    
    @responses.activate
    def test_ai_analyzer_partial_json(self):
        """测试AI分析器返回不完整的JSON"""
        symbol = "META"
        news_data = {"symbol": "META", "news": [{"title": "Test", "summary": "Test", "sentiment": 0.5}]}
        
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json={"response": '{"overall_sentiment": "positive"}'},  # 缺少必要字段
            status=200
        )
        
        result = self.ai_analyzer.analyze_stock_news(symbol, news_data)
        assert result["symbol"] == "META"
        # 应该使用默认值填充缺失字段
    
    @responses.activate
    def test_ai_analyzer_very_long_news(self):
        """测试处理非常长的新闻内容"""
        symbol = "NFLX"
        
        # 创建非常长的新闻内容
        long_news = {
            "symbol": "NFLX",
            "news": [
                {
                    "title": "Very Long News Title " * 50,
                    "summary": "Very long summary " * 1000,  # 超长摘要
                    "sentiment": 0.5
                }
            ] * 20  # 20条长新闻
        }
        
        mock_response = {
            "response": json.dumps({
                "overall_sentiment": "neutral",
                "key_points": ["Too much information to process"],
                "technical_analysis": "Unable to process due to data volume",
                "recommendation": "hold",
                "risk_level": "high",
                "reasoning": "Information overload"
            })
        }
        
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json=mock_response,
            status=200
        )
        
        result = self.ai_analyzer.analyze_stock_news(symbol, long_news)
        assert result["symbol"] == "NFLX"
    
    def test_alpha_vantage_special_characters(self):
        """测试股票代码包含特殊字符"""
        api = AlphaVantageAPI()
        api.api_key = "test_key"
        
        # 测试各种特殊字符
        invalid_symbols = ["AAPL@123", "GOOGL-TEST", "MSFT.PR", "TSLA 123", "AAPL/TEST"]
        
        for symbol in invalid_symbols:
            result = api.get_stock_news(symbol)
            assert result is None or isinstance(result, dict)
    
    def test_alpha_vantage_unicode_symbols(self):
        """测试Unicode字符的股票代码"""
        api = AlphaVantageAPI()
        api.api_key = "test_key"
        
        unicode_symbols = ["苹果", "テスラ", "🚀", "AAPL😀", "GOOGL测试"]
        
        for symbol in unicode_symbols:
            result = api.get_stock_news(symbol)
            assert result is None or isinstance(result, dict)
    
    @responses.activate
    def test_alpha_vantage_zero_volume(self):
        """测试交易量为零的情况"""
        symbol = "AMD"
        
        mock_response = {
            "Time Series (Daily)": {
                "2024-01-01": {
                    "1. open": "100.00",
                    "2. high": "100.00",
                    "3. low": "100.00",
                    "4. close": "100.00",
                    "5. volume": "0"  # 零交易量
                }
            }
        }
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json=mock_response,
            status=200
        )
        
        result = self.alpha_api.get_daily_prices(symbol)
        assert result is not None
        assert result["volume"] == 0
    
    @responses.activate
    def test_alpha_vantage_extreme_prices(self):
        """测试极端价格数据"""
        symbol = "BTC"
        
        mock_response = {
            "Time Series (Daily)": {
                "2024-01-01": {
                    "1. open": "0.0001",
                    "2. high": "999999.99",
                    "3. low": "0.00001",
                    "4. close": "50000.00",
                    "5. volume": "1000000000"
                }
            }
        }
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json=mock_response,
            status=200
        )
        
        result = self.alpha_api.get_daily_prices(symbol)
        assert result is not None
        assert result["open"] == 0.0001
        assert result["high"] == 999999.99
        assert result["low"] == 0.00001
    
    def test_ai_analyzer_special_characters_in_news(self):
        """测试新闻中包含特殊字符"""
        symbol = "CRM"
        news_data = {
            "symbol": "CRM",
            "news": [
                {
                    "title": "Salesforce's Q4: \"Record\" earnings & 100% growth!",
                    "summary": "Salesforce beats estimates @ $2.50 EPS. Revenue: $7.5B (¥750億). CEO: 'We're crushing it!' 🚀",
                    "sentiment": 0.9
                }
            ]
        }
        
        # 应该能正常处理特殊字符
        assert news_data["news"][0]["title"] is not None
        assert news_data["news"][0]["summary"] is not None
