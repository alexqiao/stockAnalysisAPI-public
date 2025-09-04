"""Alpha Vantage API 单元测试"""
import pytest
import responses
from services.alpha_vantage_api import AlphaVantageAPI

class TestAlphaVantageAPI:
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.api = AlphaVantageAPI()
        self.api.api_key = "test_api_key"
    
    @responses.activate
    def test_get_stock_news_success(self):
        """测试成功获取股票新闻"""
        symbol = "AAPL"
        mock_response = {
            "feed": [
                {
                    "title": "Apple Stock Rises on Strong Earnings",
                    "summary": "Apple reported better-than-expected earnings...",
                    "url": "https://example.com/news1",
                    "time_published": "20240101T120000",
                    "source": "Reuters",
                    "overall_sentiment_score": 0.8
                },
                {
                    "title": "iPhone Sales Beat Expectations",
                    "summary": "iPhone sales exceeded analyst predictions...",
                    "url": "https://example.com/news2",
                    "time_published": "20240101T110000",
                    "source": "Bloomberg",
                    "overall_sentiment_score": 0.6
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json=mock_response,
            status=200
        )
        
        result = self.api.get_stock_news(symbol)
        
        assert result is not None
        assert result["symbol"] == "AAPL"
        assert len(result["news"]) == 2
        assert result["news"][0]["title"] == "Apple Stock Rises on Strong Earnings"
        assert result["news"][0]["sentiment"] == 0.8
    
    @responses.activate
    def test_get_stock_news_no_data(self):
        """测试无新闻数据的情况"""
        symbol = "INVALID"
        mock_response = {}
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json=mock_response,
            status=200
        )
        
        result = self.api.get_stock_news(symbol)
        assert result is None
    
    @responses.activate
    def test_get_stock_news_api_error(self):
        """测试API错误处理"""
        symbol = "AAPL"
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json={"error": "API limit reached"},
            status=429
        )
        
        result = self.api.get_stock_news(symbol)
        assert result is None
    
    @responses.activate
    def test_get_daily_prices_success(self):
        """测试成功获取日K数据"""
        symbol = "AAPL"
        mock_response = {
            "Time Series (Daily)": {
                "2024-01-01": {
                    "1. open": "150.00",
                    "2. high": "155.00",
                    "3. low": "149.50",
                    "4. close": "154.00",
                    "5. volume": "1000000"
                },
                "2023-12-29": {
                    "1. open": "148.00",
                    "2. high": "152.00",
                    "3. low": "147.00",
                    "4. close": "149.00",
                    "5. volume": "800000"
                }
            }
        }
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json=mock_response,
            status=200
        )
        
        result = self.api.get_daily_prices(symbol)
        
        assert result is not None
        assert result["symbol"] == "AAPL"
        assert result["date"] == "2024-01-01"
        assert result["open"] == 150.00
        assert result["close"] == 154.00
        assert result["volume"] == 1000000
    
    @responses.activate
    def test_get_daily_prices_no_data(self):
        """测试无价格数据的情况"""
        symbol = "INVALID"
        mock_response = {"Error Message": "Invalid API call"}
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json=mock_response,
            status=200
        )
        
        result = self.api.get_daily_prices(symbol)
        assert result is None
    
    def test_init_without_api_key(self, monkeypatch):
        """测试缺少API Key的情况"""
        monkeypatch.delenv("ALPHA_VANTAGE_API_KEY", raising=False)
        with pytest.raises(ValueError, match="ALPHA_VANTAGE_API_KEY not found"):
            AlphaVantageAPI()

    @responses.activate
    def test_search_symbols_success(self):
        """测试成功搜索股票符号"""
        keywords = "Apple"
        mock_response = {
            "bestMatches": [
                {
                    "1. symbol": "AAPL",
                    "2. name": "Apple Inc.",
                    "3. type": "Equity",
                    "4. region": "United States",
                    "5. marketOpen": "09:30",
                    "6. marketClose": "16:00",
                    "7. timezone": "UTC-05",
                    "8. currency": "USD",
                    "9. matchScore": "1.0000"
                },
                {
                    "1. symbol": "APLE",
                    "2. name": "Apple Hospitality REIT Inc.",
                    "3. type": "Equity",
                    "4. region": "United States",
                    "5. marketOpen": "09:30",
                    "6. marketClose": "16:00",
                    "7. timezone": "UTC-05",
                    "8. currency": "USD",
                    "9. matchScore": "0.8000"
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json=mock_response,
            status=200
        )
        
        result = self.api.search_symbols(keywords)
        
        assert result is not None
        assert len(result) == 2
        assert result[0]["symbol"] == "AAPL"
        assert result[0]["name"] == "Apple Inc."
        assert result[1]["symbol"] == "APLE"
        assert result[1]["name"] == "Apple Hospitality REIT Inc."

    @responses.activate
    def test_search_symbols_no_matches(self):
        """测试搜索无匹配结果的情况"""
        keywords = "InvalidCompany"
        mock_response = {"bestMatches": []}
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json=mock_response,
            status=200
        )
        
        result = self.api.search_symbols(keywords)
        assert result == []

    @responses.activate
    def test_search_symbols_no_best_matches_field(self):
        """测试响应中没有bestMatches字段的情况"""
        keywords = "Test"
        mock_response = {"Error Message": "Invalid API call"}
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json=mock_response,
            status=200
        )
        
        result = self.api.search_symbols(keywords)
        assert result == []

    @responses.activate
    def test_search_symbols_api_error(self):
        """测试API错误处理"""
        keywords = "Apple"
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json={"error": "API limit reached"},
            status=429
        )
        
        result = self.api.search_symbols(keywords)
        assert result == []
