"""性能测试套件"""
import pytest
import responses
import time
from unittest.mock import patch, MagicMock
from services.alpha_vantage_api import AlphaVantageAPI
from services.ai_analyzer import AIAnalyzer
from app.models import User, StockAnalysis
from app.database import db
import json

class TestPerformance:
    """性能测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.alpha_api = AlphaVantageAPI()
        self.alpha_api.api_key = "test_api_key"
        self.ai_analyzer = AIAnalyzer(model_name="test-model")
    
    @responses.activate
    def test_alpha_vantage_response_time(self):
        """测试Alpha Vantage API响应时间"""
        symbol = "AAPL"
        
        # 模拟正常响应
        mock_response = {
            "feed": [
                {
                    "title": "Test News",
                    "summary": "Test Summary",
                    "url": "https://example.com",
                    "time_published": "20240101T120000",
                    "source": "Reuters",
                    "overall_sentiment_score": 0.5
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json=mock_response,
            status=200
        )
        
        start_time = time.time()
        result = self.alpha_api.get_stock_news(symbol)
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 5.0  # 响应时间应小于5秒
        assert result is not None
    
    @responses.activate
    def test_alpha_vantage_concurrent_requests(self):
        """测试并发请求处理"""
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
        
        for symbol in symbols:
            mock_response = {
                "feed": [
                    {
                        "title": f"News for {symbol}",
                        "summary": f"Summary for {symbol}",
                        "url": "https://example.com",
                        "time_published": "20240101T120000",
                        "source": "Reuters",
                        "overall_sentiment_score": 0.5
                    }
                ]
            }
            
            responses.add(
                responses.GET,
                "https://www.alphavantage.co/query",
                json=mock_response,
                status=200
            )
        
        start_time = time.time()
        results = []
        for symbol in symbols:
            result = self.alpha_api.get_stock_news(symbol)
            results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert len(results) == 5
        assert all(result is not None for result in results)
        assert total_time < 15.0  # 5个请求总时间应小于15秒
    
    @responses.activate
    def test_ai_analyzer_response_time(self):
        """测试AI分析器响应时间"""
        symbol = "NVDA"
        news_data = {
            "symbol": "NVDA",
            "news": [
                {
                    "title": "NVIDIA Reports Record Earnings",
                    "summary": "NVIDIA beats expectations with strong AI chip sales...",
                    "sentiment": 0.8
                }
            ]
        }
        
        mock_response = {
            "response": json.dumps({
                "overall_sentiment": "positive",
                "key_points": ["Strong earnings", "AI growth"],
                "technical_analysis": "Bullish trend",
                "recommendation": "buy",
                "risk_level": "medium",
                "reasoning": "Strong fundamentals"
            })
        }
        
        responses.add(
            responses.POST,
            "http://localhost:11434/api/generate",
            json=mock_response,
            status=200
        )
        
        start_time = time.time()
        result = self.ai_analyzer.analyze_stock_news(symbol, news_data)
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 10.0  # AI分析响应时间应小于10秒
        assert result is not None
    
    def test_large_dataset_processing(self):
        """测试大数据集处理性能"""
        # 创建大量新闻数据
        large_news_data = {
            "symbol": "TEST",
            "news": [
                {
                    "title": f"News {i}",
                    "summary": f"Summary {i} " * 100,  # 每条摘要100个单词
                    "sentiment": 0.5
                }
                for i in range(100)  # 100条新闻
            ]
        }
        
        # 模拟AI分析器处理大数据集
        with patch('services.ai_analyzer.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "response": json.dumps({
                    "overall_sentiment": "neutral",
                    "key_points": ["Large dataset processed"],
                    "technical_analysis": "Mixed signals",
                    "recommendation": "hold",
                    "risk_level": "medium",
                    "reasoning": "Processed 100 news items"
                })
            }
            mock_post.return_value = mock_response
            
            start_time = time.time()
            result = self.ai_analyzer.analyze_stock_news("TEST", large_news_data)
            end_time = time.time()
            
            processing_time = end_time - start_time
            assert processing_time < 30.0  # 大数据集处理时间应小于30秒
            assert result is not None
    
    def test_memory_usage_with_large_data(self):
        """测试大数据情况下的内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建大量数据
        large_data = {
            "symbol": "MEMORY_TEST",
            "news": [
                {
                    "title": f"Memory Test News {i}",
                    "summary": "Test summary " * 1000,  # 长文本
                    "sentiment": 0.5
                }
                for i in range(1000)  # 1000条新闻
            ]
        }
        
        # 处理数据
        with patch('services.ai_analyzer.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "response": json.dumps({
                    "overall_sentiment": "neutral",
                    "key_points": ["Memory test completed"],
                    "technical_analysis": "Memory usage acceptable",
                    "recommendation": "hold",
                    "risk_level": "low",
                    "reasoning": "Memory usage within limits"
                })
            }
            mock_post.return_value = mock_response
            
            result = self.ai_analyzer.analyze_stock_news("MEMORY_TEST", large_data)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            assert memory_increase < 100  # 内存增加应小于100MB
            assert result is not None
    
    @responses.activate
    def test_rate_limiting_simulation(self):
        """测试速率限制处理"""
        symbol = "RATE_TEST"
        
        # 模拟速率限制响应
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json={"Note": "Thank you for using Alpha Vantage..."},
            status=429
        )
        
        start_time = time.time()
        result = self.alpha_api.get_stock_news(symbol)
        end_time = time.time()
        
        response_time = end_time - start_time
        assert result is None
        assert response_time < 2.0  # 速率限制响应应快速返回
    
    def test_database_query_performance(self):
        """测试数据库查询性能"""
        # 创建测试用户
        user = User(username="perf_test", email="perf@test.com")
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        
        # 创建大量分析记录
        for i in range(100):
            analysis = StockAnalysis(
                symbol=f"TEST{i}",
                user_id=user.id,
                analysis_data={"test": f"data{i}"}
            )
            db.session.add(analysis)
        db.session.commit()
        
        start_time = time.time()
        
        # 查询用户的所有分析
        analyses = StockAnalysis.query.filter_by(user_id=user.id).all()
        
        end_time = time.time()
        query_time = end_time - start_time
        
        assert len(analyses) == 100
        assert query_time < 1.0  # 数据库查询应小于1秒
        
        # 清理测试数据
        StockAnalysis.query.filter_by(user_id=user.id).delete()
        User.query.filter_by(id=user.id).delete()
        db.session.commit()
    
    @responses.activate
    def test_caching_performance(self):
        """测试缓存性能"""
        symbol = "CACHE_TEST"
        
        # 第一次请求
        mock_response = {
            "feed": [
                {
                    "title": "Cached News",
                    "summary": "Cached Summary",
                    "url": "https://example.com",
                    "time_published": "20240101T120000",
                    "source": "Reuters",
                    "overall_sentiment_score": 0.5
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://www.alphavantage.co/query",
            json=mock_response,
            status=200
        )
        
        # 第一次调用
        start_time = time.time()
        result1 = self.alpha_api.get_stock_news(symbol)
        first_call_time = time.time() - start_time
        
        # 第二次调用（应该使用缓存）
        start_time = time.time()
        result2 = self.alpha_api.get_stock_news(symbol)
        second_call_time = time.time() - start_time
        
        assert result1 is not None
        assert result2 is not None
        assert second_call_time < first_call_time * 0.5  # 缓存调用应更快
    
    def test_error_handling_performance(self):
        """测试错误处理性能"""
        # 测试各种错误情况的处理时间
        
        # 网络错误
        with patch('services.alpha_vantage_api.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            start_time = time.time()
            result = self.alpha_api.get_stock_news("ERROR_TEST")
            end_time = time.time()
            
            assert result is None
            assert (end_time - start_time) < 1.0  # 错误处理应快速返回
