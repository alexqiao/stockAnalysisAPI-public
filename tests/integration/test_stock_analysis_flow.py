"""股票分析流程集成测试"""
import pytest
import responses
import json

class TestStockAnalysisFlow:
    
    def test_analyze_stock_success(self, client, auth_headers):
        """测试完整股票分析流程成功"""
        symbol = "AAPL"
        
        # Mock Alpha Vantage API响应
        news_response = {
            "feed": [
                {
                    "title": "Apple Stock Rises on Strong Earnings",
                    "summary": "Apple reported better-than-expected earnings...",
                    "url": "https://example.com/news1",
                    "time_published": "20240101T120000",
                    "source": "Reuters",
                    "overall_sentiment_score": 0.8
                }
            ]
        }
        
        price_response = {
            "Time Series (Daily)": {
                "2024-01-01": {
                    "1. open": "150.00",
                    "2. high": "155.00",
                    "3. low": "149.50",
                    "4. close": "154.00",
                    "5. volume": "1000000"
                }
            }
        }
        
        # Mock Ollama响应
        ollama_response = {
            "response": json.dumps({
                "overall_sentiment": "positive",
                "key_points": ["Strong earnings beat expectations"],
                "technical_analysis": "Stock is in uptrend",
                "recommendation": "buy",
                "risk_level": "low",
                "reasoning": "Based on positive earnings"
            })
        }
        
        with responses.RequestsMock() as rsps:
            # 设置mock响应
            rsps.add(
                responses.GET,
                "https://www.alphavantage.co/query",
                json=news_response,
                status=200
            )
            rsps.add(
                responses.GET,
                "https://www.alphavantage.co/query",
                json=price_response,
                status=200
            )
            rsps.add(
                responses.POST,
                "http://localhost:11434/api/generate",
                json=ollama_response,
                status=200
            )
            
            # 发送请求
            response = client.get(
                f"/api/analyze/{symbol}",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["analysis"]["recommendation"] == "buy"
        assert "news" in data
        assert "analysis" in data
    
    def test_analyze_stock_no_auth(self, client):
        """测试无认证访问股票分析"""
        response = client.get("/api/analyze/AAPL")
        assert response.status_code == 401
    
    def test_analyze_stock_invalid_symbol(self, client, auth_headers):
        """测试无效股票代码"""
        symbol = "INVALID"
        
        # Mock Alpha Vantage API返回错误
        news_response = {"Error Message": "Invalid API call"}
        price_response = {"Error Message": "Invalid API call"}
        
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://www.alphavantage.co/query",
                json=news_response,
                status=200
            )
            rsps.add(
                responses.GET,
                "https://www.alphavantage.co/query",
                json=price_response,
                status=200
            )
            
            response = client.get(
                f"/api/analyze/{symbol}",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "INVALID"
        assert "error" in data
        assert data["analysis"]["recommendation"] == "hold"
    
    def test_analyze_stock_api_limit_reached(self, client, auth_headers):
        """测试API限制情况"""
        symbol = "TSLA"
        
        # Mock Alpha Vantage API返回限制错误
        error_response = {
            "Note": "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day."
        }
        
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://www.alphavantage.co/query",
                json=error_response,
                status=200
            )
            
            response = client.get(
                f"/api/analyze/{symbol}",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert "analysis" in data
        assert "No data available" in data["analysis"]["key_points"][0]
    
    def test_analyze_stock_ollama_down(self, client, auth_headers):
        """测试Ollama服务不可用"""
        symbol = "GOOGL"
        
        # Mock Alpha Vantage API响应
        news_response = {
            "feed": [{"title": "Test", "summary": "Test", "overall_sentiment_score": 0.5}]
        }
        price_response = {
            "Time Series (Daily)": {
                "2024-01-01": {
                    "1. open": "100.00",
                    "2. high": "105.00",
                    "3. low": "99.00",
                    "4. close": "103.00",
                    "5. volume": "500000"
                }
            }
        }
        
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://www.alphavantage.co/query",
                json=news_response,
                status=200
            )
            rsps.add(
                responses.GET,
                "https://www.alphavantage.co/query",
                json=price_response,
                status=200
            )
            rsps.add(
                responses.POST,
                "http://localhost:11434/api/generate",
                json={"error": "Service unavailable"},
                status=500
            )
            
            response = client.get(
                f"/api/analyze/{symbol}",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "GOOGL"
        assert "analysis" in data
        assert "分析过程中出现错误" in data["analysis"]["key_points"][0]
        assert data["analysis"]["recommendation"] == "hold"
    
    def test_analyze_stock_no_news_data(self, client, auth_headers):
        """测试无新闻数据的情况"""
        symbol = "MSFT"
        
        # Mock Alpha Vantage API返回空新闻
        news_response = {"feed": []}
        price_response = {
            "Time Series (Daily)": {
                "2024-01-01": {
                    "1. open": "200.00",
                    "2. high": "205.00",
                    "3. low": "198.00",
                    "4. close": "203.00",
                    "5. volume": "1000000"
                }
            }
        }
        
        ollama_response = {
            "response": json.dumps({
                "overall_sentiment": "neutral",
                "key_points": ["No recent news available"],
                "technical_analysis": "Based on price data only",
                "recommendation": "hold",
                "risk_level": "medium",
                "reasoning": "No news sentiment to analyze"
            })
        }
        
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://www.alphavantage.co/query",
                json=news_response,
                status=200
            )
            rsps.add(
                responses.GET,
                "https://www.alphavantage.co/query",
                json=price_response,
                status=200
            )
            rsps.add(
                responses.POST,
                "http://localhost:11434/api/generate",
                json=ollama_response,
                status=200
            )
            
            response = client.get(
                f"/api/analyze/{symbol}",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "MSFT"
        assert data["analysis"]["overall_sentiment"] == "neutral"
