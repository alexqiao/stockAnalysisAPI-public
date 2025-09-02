import yagmail
import os
import json
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class EmailService:
    def __init__(self):
        self.sender_email = os.getenv("EMAIL_SENDER")
        self.sender_password = os.getenv("EMAIL_PASSWORD")
        self.smtp_server = os.getenv("EMAIL_SMTP_SERVER", "smtp.126.com")
        self.smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        
        if not all([self.sender_email, self.sender_password]):
            raise ValueError("Email configuration not found in environment variables")
    
    def send_analysis_report(self, recipient_email: str, analyses: List[Dict]) -> bool:
        """发送股票分析报告（旧版）"""
        try:
            yag = yagmail.SMTP(
                user=self.sender_email,
                password=self.sender_password,
                host=self.smtp_server,
                port=self.smtp_port
            )
            
            subject = f"股票分析报告 - {datetime.now().strftime('%Y-%m-%d')}"
            
            html_content = self._generate_legacy_html_report(analyses)
            
            yag.send(
                to=recipient_email,
                subject=subject,
                contents=[html_content]
            )
            
            print(f"Legacy report sent to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"Error sending legacy email: {e}")
            return False
    
    def send_daily_digest_email(self, user_info: Dict, analyses: List) -> bool:
        """发送每日摘要邮件"""
        try:
            yag = yagmail.SMTP(
                user=self.sender_email,
                password=self.sender_password,
                host=self.smtp_server,
                port=self.smtp_port
            )
            
            subject = f"每日股票分析摘要 - {datetime.now().strftime('%Y-%m-%d')}"
            
            html_content = self._generate_daily_digest_html(user_info, analyses)
            
            yag.send(
                to=user_info['email'],
                subject=subject,
                contents=[html_content]
            )
            
            print(f"Daily digest sent to {user_info['email']}")
            return True
            
        except Exception as e:
            print(f"Error sending daily digest email: {e}")
            return False
    
    def _generate_legacy_html_report(self, analyses: List[Dict]) -> str:
        """生成旧版HTML格式的报告"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .stock-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .recommendation {{ font-weight: bold; padding: 5px 10px; border-radius: 3px; }}
                .buy {{ background-color: #d4edda; color: #155724; }}
                .sell {{ background-color: #f8d7da; color: #721c24; }}
                .hold {{ background-color: #fff3cd; color: #856404; }}
                .key-points {{ margin: 10px 0; }}
                .key-points li {{ margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>股票分析报告</h1>
                <p>报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
        """
        
        for analysis in analyses:
            symbol = analysis.get("symbol", "")
            ai_analysis = analysis.get("analysis", {})
            
            recommendation = ai_analysis.get("recommendation", "hold")
            rec_class = recommendation.lower()
            
            html += f"""
            <div class="stock-section">
                <h2>{symbol} 分析报告</h2>
                <p><strong>总体情绪:</strong> {ai_analysis.get("overall_sentiment", "neutral")}</p>
                <p><strong>投资建议:</strong> <span class="recommendation {rec_class}">{recommendation.upper()}</span></p>
                <p><strong>风险等级:</strong> {ai_analysis.get("risk_level", "medium")}</p>
                
                <div class="key-points">
                    <h3>关键要点:</h3>
                    <ul>
            """
            
            for point in ai_analysis.get("key_points", []):
                html += f"<li>{point}</li>"
            
            html += f"""
                    </ul>
                </div>
                
                <p><strong>技术面分析:</strong> {ai_analysis.get("technical_analysis", "无")}</p>
                <p><strong>分析理由:</strong> {ai_analysis.get("reasoning", "无")}</p>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def _generate_daily_digest_html(self, user_info: Dict, analyses: List) -> str:
        """生成每日摘要HTML内容"""
        # 读取模板文件
        main_template = self._read_template('app/web/templates/email/main.html')
        card_template = self._read_template('app/web/templates/email/card.html')
        
        # 生成股票卡片
        stock_cards_html = ""
        for analysis in analyses:
            stock_card = self._generate_stock_card(card_template, analysis, user_info)
            stock_cards_html += stock_card
        
        # 填充主模板
        html_content = main_template.replace(
            '{stock_cards}', 
            stock_cards_html
        ).replace(
            '{{ analysis_date }}', 
            datetime.now().strftime('%Y-%m-%d')
        ).replace(
            '{{ unsubscribe_url }}',
            f"http://localhost:8000/api/unsubscribe/{user_info['id']}"
        )
        
        return html_content
    
    def _generate_stock_card(self, card_template: str, analysis, user_info: Dict) -> str:
        """生成单个股票卡片HTML"""
        analysis_result = analysis.analysis_result or {}
        latest_price_data = analysis.latest_price_data or {}
        
        # 准备模板数据
        template_data = {
            'symbol': analysis.stock_symbol,
            'overall_sentiment': analysis_result.get('overall_sentiment', 'neutral'),
            'recommendation': analysis_result.get('recommendation', 'hold'),
            'risk_level': analysis_result.get('risk_level', 'medium'),
            'summary': analysis_result.get('summary', '暂无摘要信息'),
            'latest_price': {
                'close': latest_price_data.get('close', 'N/A'),
                'change_percent': latest_price_data.get('change_percent', 'N/A'),
                'volume': latest_price_data.get('volume', 'N/A')
            },
            'report_url': f"http://localhost:8000/analysis/{analysis.stock_symbol}/{analysis.analysis_date}"
        }
        
        # 替换模板变量 - 处理Jinja2语法
        card_html = card_template
        
        # 处理条件语句和过滤器
        card_html = self._process_template_conditions(card_html, template_data)
        
        # 替换简单变量
        for key, value in template_data.items():
            if isinstance(value, dict):
                # 处理嵌套字典
                for sub_key, sub_value in value.items():
                    placeholder = f"{{{{ latest_price.{sub_key} }}}}"
                    card_html = card_html.replace(placeholder, str(sub_value))
            else:
                placeholder = f"{{{{ {key} }}}}"
                card_html = card_html.replace(placeholder, str(value))
        
        return card_html
    
    def _process_template_conditions(self, template: str, data: Dict) -> str:
        """处理模板中的条件语句和过滤器"""
        result = template
        
        # 处理 sentiment-{{ overall_sentiment|lower }}
        sentiment_value = data.get('overall_sentiment', 'neutral').lower()
        result = result.replace('sentiment-{{ overall_sentiment|lower }}', f'sentiment-{sentiment_value}')
        
        # 处理 recommendation-{{ recommendation|lower }}
        recommendation_value = data.get('recommendation', 'hold').lower()
        result = result.replace('recommendation-{{ recommendation|lower }}', f'recommendation-{recommendation_value}')
        
        # 处理 risk-{{ risk_level|lower }}
        risk_level_value = data.get('risk_level', 'medium').lower()
        result = result.replace('risk-{{ risk_level|lower }}', f'risk-{risk_level_value}')
        
        # 处理 {% if risk_level %} 条件块
        risk_level = data.get('risk_level')
        if risk_level:
            # 移除条件开始和结束标记，保留内容
            result = result.replace('{% if risk_level %}', '')
            result = result.replace('{% endif %}', '')
        else:
            # 移除整个条件块
            import re
            result = re.sub(r'{% if risk_level %}.*?{% endif %}', '', result, flags=re.DOTALL)
        
        # 处理默认值过滤器
        result = result.replace('{{ latest_price.close|default(\'N/A\') }}', str(data.get('latest_price', {}).get('close', 'N/A')))
        result = result.replace('{{ latest_price.change_percent|default(\'N/A\') }}', str(data.get('latest_price', {}).get('change_percent', 'N/A')))
        result = result.replace('{{ latest_price.volume|default(\'N/A\') }}', str(data.get('latest_price', {}).get('volume', 'N/A')))
        result = result.replace('{{ summary|default(\'暂无摘要信息\') }}', str(data.get('summary', '暂无摘要信息')))
        
        # 处理条件样式类
        change_percent = data.get('latest_price', {}).get('change_percent')
        if change_percent and isinstance(change_percent, (int, float)):
            if change_percent > 0:
                result = result.replace('{% if latest_price.change_percent and latest_price.change_percent > 0 %}text-success{% elif latest_price.change_percent and latest_price.change_percent < 0 %}text-danger{% endif %}', 'text-success')
            elif change_percent < 0:
                result = result.replace('{% if latest_price.change_percent and latest_price.change_percent > 0 %}text-success{% elif latest_price.change_percent and latest_price.change_percent < 0 %}text-danger{% endif %}', 'text-danger')
            else:
                result = result.replace('{% if latest_price.change_percent and latest_price.change_percent > 0 %}text-success{% elif latest_price.change_percent and latest_price.change_percent < 0 %}text-danger{% endif %}', '')
        else:
            result = result.replace('{% if latest_price.change_percent and latest_price.change_percent > 0 %}text-success{% elif latest_price.change_percent and latest_price.change_percent < 0 %}text-danger{% endif %}', '')
        
        # 处理嵌套的条件语句（涨跌幅的特殊情况）
        result = result.replace('{% if latest_price.change_percent and latest_price.change_percent > 0 %}text-success{% elif latest_price.change_percent and latest_price.change_percent < 0 %}text-danger', 'text-success')
        
        return result
    
    def _read_template(self, template_path: str) -> str:
        """读取模板文件内容"""
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            print(f"Template file not found: {template_path}")
            return ""
        except Exception as e:
            print(f"Error reading template {template_path}: {e}")
            return ""
