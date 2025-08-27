"""AI分析器单元测试"""
import pytest
import responses
import json
from services.ai_analyzer import AIAnalyzer

class TestAIAnalyzer:
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.analyzer = AIAnalyzer(model_name="test-model")
    
    @responses.activate
    def test_analyze_stock_news_success(self):
        """测试成功分析股票新闻"""
        symbol = "AAPL"
        news_data = {
            "symbol": "AAPL",
            "news": [
                {
                    "title": "Apple Stock Rises on Strong Earnings",
                    "summary": "Apple reported better-than-expected earnings...",
                    "sentiment": 0.8
                },
                {
                    "title": "iPhone Sales Beat Expectations",
                    "summary": "iPhone sales exceeded analyst predictions...",
                    "sentiment": 0.6
                }
            ]
        }
        price_data = {
            "close": 154.00,
            "open": 150.00,
            "high": 155.00,
            "low": 149.50,
            "volume": 1000000
        }
        
        mock_response = {
            "response": json.dumps({
                "overall_sentiment": "positive",
                "key_points": [
                    "Strong earnings beat expectations",
                    "iPhone sales showing growth"
                ],
                "technical_analysis": "Stock is in uptrend with strong momentum",
                "recommendation": "buy",
                "risk_level": "low",
                "reasoning": "Based on positive earnings and strong sales data"
            })
        }
        
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json=mock_response,
            status=200
        )
        
        result = self.analyzer.analyze_stock_news(symbol, news_data, price_data)
        
        assert result["symbol"] == "AAPL"
        assert result["analysis"]["overall_sentiment"] == "positive"
        assert result["analysis"]["recommendation"] == "buy"
        assert len(result["analysis"]["key_points"]) == 2
    
    @responses.activate
    def test_analyze_stock_news_no_price_data(self):
        """测试无价格数据的分析"""
        symbol = "TSLA"
        news_data = {
            "symbol": "TSLA",
            "news": [
                {
                    "title": "Tesla Announces New Model",
                    "summary": "Tesla unveiled a new electric vehicle model...",
                    "sentiment": 0.7
                }
            ]
        }
        
        mock_response = {
            "response": json.dumps({
                "overall_sentiment": "positive",
                "key_points": ["New product announcement"],
                "technical_analysis": "No price data available",
                "recommendation": "hold",
                "risk_level": "medium",
                "reasoning": "Positive news but no technical analysis"
            })
        }
        
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json=mock_response,
            status=200
        )
        
        result = self.analyzer.analyze_stock_news(symbol, news_data)
        
        assert result["symbol"] == "TSLA"
        assert result["analysis"]["recommendation"] == "hold"
    
    @responses.activate
    def test_analyze_stock_news_empty_news(self):
        """测试空新闻数据的分析"""
        symbol = "GOOGL"
        news_data = {"symbol": "GOOGL", "news": []}
        
        mock_response = {
            "response": json.dumps({
                "overall_sentiment": "neutral",
                "key_points": ["No recent news available"],
                "technical_analysis": "No news sentiment to analyze",
                "recommendation": "hold",
                "risk_level": "medium",
                "reasoning": "Insufficient news data for analysis"
            })
        }
        
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json=mock_response,
            status=200
        )
        
        result = self.analyzer.analyze_stock_news(symbol, news_data)
        
        assert result["symbol"] == "GOOGL"
        assert result["analysis"]["overall_sentiment"] == "neutral"
    
    @responses.activate
    def test_analyze_stock_news_ollama_error(self):
        """测试Ollama服务错误处理"""
        symbol = "MSFT"
        news_data = {
            "symbol": "MSFT",
            "news": [{"title": "Test", "summary": "Test", "sentiment": 0.5}]
        }
        
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json={"error": "Service unavailable"},
            status=500
        )
        
        result = self.analyzer.analyze_stock_news(symbol, news_data)
        
        assert result["symbol"] == "MSFT"
        assert "error" in result
        assert result["analysis"]["recommendation"] == "hold"
        assert "分析过程中出现错误" in result["analysis"]["key_points"]
    
    @responses.activate
    def test_analyze_stock_news_invalid_json(self):
        """测试无效JSON响应处理"""
        symbol = "AMZN"
        news_data = {
            "symbol": "AMZN",
            "news": [{"title": "Test", "summary": "Test", "sentiment": 0.5}]
        }
        
        mock_response = {
            "response": "invalid json response"
        }
        
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json=mock_response,
            status=200
        )
        
        result = self.analyzer.analyze_stock_news(symbol, news_data)
        
        assert result["symbol"] == "AMZN"
        assert "error" in result
        assert result["analysis"]["recommendation"] == "hold"
    
    def test_init_custom_model(self):
        """测试自定义模型初始化"""
        custom_analyzer = AIAnalyzer(model_name="custom-model-7b")
        assert custom_analyzer.model_name == "custom-model-7b"
        assert custom_analyzer.ollama_url == "http://localhost:11434/api/generate"
