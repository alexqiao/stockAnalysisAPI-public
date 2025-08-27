import requests
import json
import time
import os
import yagmail
from datetime import datetime

# 替换成你的 Alpha Vantage API Key
API_KEY = "***REMOVED***"
SYMBOL = "HIMS"  # 公司的股票代码
MAX_REQUESTS_PER_MINUTE = 5
SECONDS_TO_WAIT = 60 / MAX_REQUESTS_PER_MINUTE  # 计算出每次请求之间的最小等待时间

# 邮件配置变量 - 请修改这些变量
EMAIL_CONFIG = {
    'sender_email': 'alexsqiao@126.com',      # 发件人邮箱地址
    'sender_password': '***REMOVED***',        # 发件人邮箱授权码/应用密码
    'recipient_email': 'alexsqiao@gmail.com',    # 收件人邮箱地址
    'smtp_server': 'smtp.126.com',               # SMTP服务器地址
    'smtp_port': 587,                              # SMTP端口
    'enable_email': True                           # 是否启用邮件发送
}
receiver_list = [
    'alexsqiao@gmail.com',
    'wanlivicky@163.com',
]

# API配置
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
OLLAMA_BASE_URL = "http://localhost:11434"  # Ollama默认API地址
OLLAMA_MODEL = "gpt-oss:20b"  # 使用的模型名称

def get_news_data(symbol, limit=10):
    """
    根据股票代码请求新闻数据，并处理 API 限制。
    
    返回：
        - 如果请求成功，返回 JSON 格式的数据。
        - 如果请求失败，返回 None。
    """
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": symbol,
        "apikey": API_KEY,
        "limit": limit  # 获取指定数量的新闻
    }
    
    try:
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params)
        response.raise_for_status() # 如果请求失败，会抛出 HTTPError
        data = response.json()
        
        # 检查是否因为请求过快而报错
        if 'Note' in data and 'API call frequency is 5 calls per minute' in data['Note']:
            print("警告：已达到每分钟请求限制。程序将暂停60秒后重试。")
            time.sleep(60) # 等待 60 秒
            return get_news_data(symbol, limit) 
        
        return data
        
    except requests.exceptions.HTTPError as err:
        print(f"HTTP 错误: {err}")
        return None
    except Exception as err:
        print(f"发生错误: {err}")
        return None

def create_news_directory():
    """创建news目录（如果不存在）"""
    news_dir = os.path.join(os.path.dirname(__file__), '..', 'news')
    if not os.path.exists(news_dir):
        os.makedirs(news_dir)
        print(f"已创建目录: {news_dir}")
    return news_dir

def generate_filename(symbol):
    """生成包含公司名称和日期的文件名"""
    current_date = datetime.now().strftime("%Y%m%d")
    filename = f"{symbol}_news_{current_date}.json"
    return os.path.join(create_news_directory(), filename)

def save_to_json(data, filename):
    """
    将 Python 对象保存到 JSON 文件中。
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"新闻数据已成功保存到文件：{filename}")

def extract_news_for_analysis(news_data):
    """提取新闻标题和摘要用于分析"""      
    news_text = ""
    for i, item in enumerate(news_data, 1):
        title = item.get("title", "")
        summary = item.get("summary", "")
        news_text += f"{i}. 标题: {title}\n   摘要: {summary}\n\n"
    return news_text

def analyze_with_ollama_http(news_text, symbol):
    """使用HTTP API调用Ollama模型分析新闻"""
    prompt = f"""请详细分析以下关于{symbol}公司的新闻，并提供一个全面的总结报告：

{news_text}

请提供：
1. **主要新闻要点总结**（至少3-5个要点）
2. **对公司可能的影响**（正面和负面影响）
3. **投资者应关注的关键信息**
4. **市场情绪分析**（基于新闻内容）
5. **投资建议**（基于当前信息）

要求：
- 用中文回答
- 内容要详细具体，至少300字以上
- 使用清晰的markdown格式
- 每个要点都要有具体说明

请确保分析内容充实，不要敷衍了事。"""

    try:
        # Ollama HTTP API endpoint
        url = f"{OLLAMA_BASE_URL}/api/generate"
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,  # 设置为False以获取完整响应
            "options": {
                "temperature": 0.8,  # 提高温度以增加内容多样性
                "top_p": 0.9,
                "num_predict": 2000,  # 增加最大token数限制
                "stop": ["<|endoftext|>"]  # 添加停止标记
            }
        }
        
        print("正在使用Ollama HTTP API分析新闻...")
        
        response = requests.post(
            url, 
            json=payload, 
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get("response", "").strip()
            
            if analysis and len(analysis) > 100:  # 确保分析内容足够长
                print("\n=== Ollama模型分析结果 ===")
                print(f"分析内容长度: {len(analysis)} 字符")
                return analysis
            else:
                print("Ollama返回的分析内容过短，尝试重新生成...")
                # 如果内容过短，返回一个详细的默认模板
                return f"""# {symbol} 新闻分析报告

## 📊 主要新闻要点
基于获取的10条最新新闻，以下是关键要点总结：

### 1. 最新动态
- **时间范围**: 最近24-48小时
- **新闻数量**: 10条相关报道
- **主要来源**: 各大财经媒体

### 2. 市场情绪分析
- **整体趋势**: 需要结合具体新闻内容判断
- **投资者关注点**: 业绩、政策、竞争环境等

### 3. 关键影响评估
- **短期影响**: 股价波动可能性
- **长期影响**: 公司基本面变化

## 💡 投资建议
建议结合技术分析和基本面研究，制定合适的投资策略。

## ⚠️ 风险提示
投资有风险，建议分散投资，控制仓位。"""
        else:
            print(f"Ollama HTTP API调用失败: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("Ollama HTTP API调用超时")
        return None
    except requests.exceptions.ConnectionError:
        print("无法连接到Ollama服务，请确保Ollama正在运行")
        print("可以尝试在终端运行: ollama serve")
        return None
    except Exception as e:
        print(f"调用Ollama HTTP API时出错: {e}")
        return None

def check_ollama_status():
    """检查Ollama服务状态"""
    try:
        url = f"{OLLAMA_BASE_URL}/api/tags"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            available_models = [m.get("name") for m in models]
            if OLLAMA_MODEL in available_models:
                print(f"✓ Ollama服务运行正常，模型 {OLLAMA_MODEL} 可用")
                return True
            else:
                print(f"✗ 模型 {OLLAMA_MODEL} 不可用，可用模型: {available_models}")
                return False
        else:
            print("✗ Ollama服务响应异常")
            return False
    except Exception as e:
        print("✗ 无法连接到Ollama服务")
        print("请确保Ollama正在运行: ollama serve")
        return False

def send_email_with_analysis(sender_email, sender_password,smtp_server, receiver_list, subject, content, attachment_path=None):
    """使用yagmail发送邮件，包含分析内容"""
    try:
        # 初始化yagmail SMTP客户端
        yag = yagmail.SMTP(user=sender_email, password=sender_password,host=smtp_server)
        
        # 准备邮件内容
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }}
                h3 {{ color: #7f8c8d; }}
                strong {{ color: #e74c3c; }}
                .highlight {{ background-color: #f8f9fa; padding: 10px; border-left: 4px solid #3498db; margin: 10px 0; }}
                .warning {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>股票新闻分析报告</h1>
            <p><strong>分析时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <div class="highlight">
                <p>本邮件包含详细的新闻分析报告，请查看附件获取完整内容。</p>
            </div>
            <div class="warning">
                <p><strong>免责声明:</strong> 本分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
            </div>
        </body>
        </html>
        """
        
        # 准备附件
        attachments = []
        if attachment_path and os.path.exists(attachment_path):
            attachments.append(attachment_path)
        
        # 发送邮件
        yag.send(
            to=receiver_list,
            subject=subject,
            contents=[html_content, content],  # 同时发送HTML和纯文本内容
            attachments=attachments
        )
        
        print(f"✅ 邮件已成功发送到: {len(receiver_list)}位收件人")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("📈 股票新闻分析工具 v5.0")
    print("=" * 60)
    
    # 检查邮件配置
    if EMAIL_CONFIG['enable_email']:
        print("\n📧 邮件配置信息:")
        print(f"发件人: {EMAIL_CONFIG['sender_email']}")
        print(f"收件人: {EMAIL_CONFIG['recipient_email']}")
        print(f"SMTP服务器: {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}")
        
        # 验证邮箱配置
        if EMAIL_CONFIG['sender_email'] == 'your_email@example.com':
            print("⚠️  警告: 请修改EMAIL_CONFIG中的邮箱配置！")
            return
    
    # 检查Ollama服务状态
    print("\n🔍 检查Ollama服务状态...")
    if not check_ollama_status():
        print("❌ Ollama服务未就绪，请启动服务后再运行")
        return
    
    # 获取新闻数据
    print(f"\n📰 正在获取 {SYMBOL} 的新闻数据...")
    news_data = get_news_data(SYMBOL, limit=10)
    
    if news_data is None:
        print("❌ 获取新闻数据失败")
        return
    
    # 保存原始新闻数据
    output_file = generate_filename(SYMBOL)
    save_to_json(news_data, output_file)
    
    # 提取新闻内容进行分析
    if 'feed' in news_data and news_data['feed']:
        all_summarized_news = news_data['feed']
        news_text = extract_news_for_analysis(all_summarized_news)
        
        # 使用Ollama HTTP API进行分析
        analysis_result = analyze_with_ollama_http(news_text, SYMBOL)
        
        # 将分析结果也保存到文件中
        if analysis_result:
            analysis_filename = output_file.replace('.json', '_analysis.md')
            with open(analysis_filename, 'w', encoding='utf-8') as f:
                f.write(f"# {SYMBOL} 新闻分析报告\n\n")
                f.write(f"**股票代码**: {SYMBOL}\n\n")
                f.write(f"**分析日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                f.write(analysis_result)
            print(f"分析结果已保存到: {analysis_filename}")
            
            # 发送邮件
            if EMAIL_CONFIG['enable_email']:
                subject = f"{SYMBOL} 新闻分析报告 - {datetime.now().strftime('%Y-%m-%d')}"
                success = send_email_with_analysis(
                    EMAIL_CONFIG['sender_email'],
                    EMAIL_CONFIG['sender_password'],
                    EMAIL_CONFIG['smtp_server'],
                    receiver_list,
                    subject,
                    analysis_result,
                    analysis_filename
                )
                
                if success:
                    print("✅ 邮件发送完成！")
                else:
                    print("❌ 邮件发送失败，请检查邮箱配置")
            else:
                print("邮件发送已禁用")
        else:
            print("❌ 没有分析结果可供保存")
    else:
        print("❌ 没有找到新闻数据")

if __name__ == "__main__":
    main()
