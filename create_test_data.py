#!/usr/bin/env python3
"""
手动创建测试分析数据，用于测试前端显示
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import StockAnalysis
from datetime import date, datetime
import json

def create_test_analysis():
    """创建测试分析数据"""
    db = SessionLocal()
    try:
        # 删除现有的测试数据（如果存在）
        db.query(StockAnalysis).filter(StockAnalysis.stock_symbol == "AAPL").delete()
        
        # 创建测试分析数据
        test_analysis = {
            "overall_sentiment": "positive",
            "key_points": [
                "苹果公司发布新款iPhone，市场反应积极",
                "季度财报超出预期，营收增长强劲",
                "服务业务收入持续增长，利润率提升",
                "中国市场销售表现良好，市场份额扩大"
            ],
            "technical_analysis": "股价突破关键阻力位，技术指标显示买入信号",
            "recommendation": "buy",
            "risk_level": "medium",
            "summary": "苹果公司基本面强劲，技术面积极，建议买入",
            "reasoning": "基于强劲的财报表现和新产品发布，预计股价将继续上涨"
        }
        
        test_price_data = {
            "open": 175.50,
            "high": 178.25,
            "low": 174.80,
            "close": 177.89,
            "volume": 45678900
        }
        
        test_news_data = {
            "news": [
                {
                    "title": "苹果发布新款iPhone 16，预购量创纪录",
                    "summary": "苹果公司最新发布的iPhone 16系列手机在首日预购量达到200万台，创下历史新高",
                    "url": "https://example.com/apple-iphone16-launch"
                },
                {
                    "title": "苹果季度营收超预期，服务业务增长强劲",
                    "summary": "苹果公司公布季度财报，营收达到895亿美元，超出分析师预期，服务业务收入同比增长12%",
                    "url": "https://example.com/apple-earnings-q3"
                },
                {
                    "title": "苹果在中国市场份额扩大至25%",
                    "summary": "根据最新市场调研数据，苹果在中国智能手机市场的份额从22%增长至25%",
                    "url": "https://example.com/apple-china-market-share"
                }
            ]
        }
        
        stock_analysis = StockAnalysis(
            stock_symbol="AAPL",
            analysis_date=date.today(),
            analysis_result=test_analysis,
            latest_price_data=test_price_data,
            news_data=test_news_data
        )
        
        db.add(stock_analysis)
        db.commit()
        
        print(f"✅ 成功创建测试分析数据 for AAPL")
        print(f"📊 分析日期: {date.today()}")
        print(f"📈 价格数据: {test_price_data['close']}")
        print(f"📰 新闻数量: {len(test_news_data['news'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_test_analysis()
    if success:
        print("\n🎉 测试数据创建完成！现在可以测试前端显示了。")
        print("运行命令测试: curl -X GET http://localhost:8000/api/analyze/AAPL -H \"Authorization: Bearer <your_token>\"")
    else:
        print("\n❌ 测试数据创建失败")
        sys.exit(1)
