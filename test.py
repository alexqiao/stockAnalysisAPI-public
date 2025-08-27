import re
import json

def extract_json_from_qwen_output(text: str) -> dict or None:
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

# 你的模型输出示例
model_output = """
<think>
Okay, let's start analyzing the data provided for TSLA. First, the price information: the latest price is $340.01, which is slightly below the high of $340.25. The open was $321.66, so there's been an increase today. The low is $319.69, which is close to the open. The volume is quite high at 94,016,347, indicating significant trading activity. That might suggest investor interest or volatility.

Now, looking at the news articles. The first one mentions Trump naming Sergio Gor as Ambassador to India, but there's a feud with Elon Musk. This could be a negative for Tesla if it affects Musk's reputation or business. However, the article doesn't directly link this to Tesla's performance, so maybe neutral.

The second article is about Trump appointing Joe Gebbia as Chief Design Officer for federal digital services. This doesn't mention Tesla, so probably not relevant here.

Third article is about a Vanguard ETF for mega caps. While it's about investing in big stocks, it doesn't directly affect Tesla unless it's a recommendation to invest in the ETF, which includes Tesla. But the article is more about the ETF itself, so maybe neutral.

Fourth article is about Elon Musk's xAI simulating software giants like Microsoft, called 'Macrohard'. This could be a positive for Tesla if it's related to innovation or AI advancements, but the article mentions Tesla in the same breath as Microsoft. However, the connection isn't clear. It might be a positive if it's a new venture that could benefit Tesla indirectly.

Fifth article is a prediction about quantum computing stock outperforming Tesla in 2030. This might be a negative for Tesla if it's suggesting that other sectors (quantum computing) could surpass Tesla's value. However, it's a prediction and not certain.

Putting the news together: There's some mixed signals. The xAI article might be positive, but the Trump-Gor nomination could have some negative implications. However, the other articles are less directly related. The overall sentiment from the news is probably neutral to slightly negative, but not strongly so.

For technical analysis, the stock closed near the high, which is a positive sign. The volume is high, which could indicate strong interest. The price increased from open to close, so that's a positive. The low is close to the open, but the high is near the close. This might suggest a bullish trend, but with some volatility.

The recommendation would depend on the analysis. If the technicals are positive and the news is neutral, maybe a 'hold' or 'buy'. However, the risk might be medium because the news has some uncertainty. The high volume could be a sign of potential movement, but without clear positive news, maybe a 'hold' is safer.

Overall, the sentiment is neutral because the news doesn't have a clear positive or negative impact. The technicals are slightly positive, but the recommendation might be to hold due to the uncertainty in the news and the high volume indicating possible volatility.
</think>

{
  "overall_sentiment": "neutral",
  "key_points": [
    "News about Trump's appointments (e.g., Sergio Gor to India) may indirectly affect Tesla through geopolitical or business environment shifts, but no direct impact on TSLA is mentioned.",
    "Elon Musk's xAI initiative ('Macrohard') could signal innovation in AI, potentially benefiting Tesla's ecosystem, but no immediate financial implications are clear.",
    "Quantum computing predictions highlight long-term tech competition, but no direct link to Tesla's near-term performance.",
    "High trading volume ($94M) suggests market interest, but price movement is narrow (open-close range of ~$18.35)."
  ],
  "technical_analysis": "TSLA closed near its daily high ($340.01 vs. $340.25), showing bullish momentum. However, the price remains within a tight range, indicating consolidation. High volume suggests active trading but lacks a clear breakout pattern.",
  "recommendation": "hold",
  "risk_level": "medium",
  "summary": "Mixed signals from news and neutral technicals suggest maintaining a cautious stance. No strong catalysts for immediate price movement.",
  "reasoning": "While Tesla's AI initiatives (e.g., xAI) show innovation potential, news unrelated to core business (e.g., Trump appointments) lacks clear impact. Technicals indicate consolidation, not a strong trend. Medium risk persists due to macroeconomic and competitive uncertainties."
}
"""

# 调用函数并打印结果
extracted_json = extract_json_from_qwen_output(model_output)

if extracted_json:
    print("成功提取并解析的JSON内容:")
    print(json.dumps(extracted_json, indent=2, ensure_ascii=False))