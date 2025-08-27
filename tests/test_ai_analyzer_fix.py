import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from services.ai_analyzer import AIAnalyzer

def test_ai_analyzer():
    """测试修复后的AI分析器"""
    print("=" * 50)
    print("测试修复后的AI分析器")
    print("=" * 50)
    
    # 创建AI分析器实例
    ai_analyzer = AIAnalyzer()
    
    print(f"Ollama Base URL: {ai_analyzer.ollama_base_url}")
    print(f"Model Name: {ai_analyzer.model_name}")
    print(f"Ollama URL: {ai_analyzer.ollama_url}")
    
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
    
    print(f"\n测试股票: {test_symbol}")
    print("测试新闻数据:", len(test_news_data["news"]), "条新闻")
    print("测试价格数据: 可用")
    
    try:
        # 测试分析功能
        print("\n开始分析股票...")
        result = ai_analyzer.analyze_stock_news(test_symbol, test_news_data, test_price_data)
        
        if "error" in result:
            print(f"❌ 分析失败: {result['error']}")
            
            # 显示调试信息
            print("\n=== 调试信息 ===")
            print(f"Ollama URL: {ai_analyzer.ollama_url}")
            print(f"Model: {ai_analyzer.model_name}")
            
            # 尝试直接调用API来获取更多信息
            import requests
            test_payload = {
                "model": ai_analyzer.model_name,
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": False
            }
            try:
                test_response = requests.post(ai_analyzer.ollama_url, json=test_payload, timeout=30)
                print(f"简单测试响应状态: {test_response.status_code}")
                if test_response.status_code == 200:
                    test_result = test_response.json()
                    print("简单测试成功")
                else:
                    print(f"简单测试失败: {test_response.text}")
            except Exception as test_e:
                print(f"简单测试异常: {test_e}")
                
            return False
        else:
            print("✅ 分析成功！")
            print(f"分析结果包含键: {list(result['analysis'].keys())}")
            return True
            
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ai_analyzer()
    
    if success:
        print("\n🎉 AI分析器修复成功！")
        print("现在可以重新启动应用并测试股票分析功能了。")
    else:
        print("\n❌ AI分析器测试失败，请检查配置。")
