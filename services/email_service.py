import yagmail
import os
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.sender_email = os.getenv("EMAIL_SENDER")
        self.sender_password = os.getenv("EMAIL_PASSWORD")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.126.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        
        if not all([self.sender_email, self.sender_password]):
            raise ValueError("Email configuration not found in environment variables")
    
    def send_analysis_report(self, recipient_email: str, analyses: List[Dict]) -> bool:
        """发送股票分析报告"""
        try:
            yag = yagmail.SMTP(
                user=self.sender_email,
                password=self.sender_password,
                host=self.smtp_server,
                port=self.smtp_port
            )
            
            subject = f"股票分析报告 - {datetime.now().strftime('%Y-%m-%d')}"
            
            html_content = self._generate_html_report(analyses)
            
            yag.send(
                to=recipient_email,
                subject=subject,
                contents=[html_content]
            )
            
            print(f"Report sent to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def _generate_html_report(self, analyses: List[Dict]) -> str:
        """生成HTML格式的报告"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f4f4f4; padding: 20px; border-radius: 5px; }
                .stock-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                .recommendation { font-weight: bold; padding: 5px 10px; border-radius: 3px; }
                .buy { background-color: #d4edda; color: #155724; }
                .sell { background-color: #f8d7da; color: #721c24; }
                .hold { background-color: #fff3cd; color: #856404; }
                .key-points { margin: 10px 0; }
                .key-points li { margin: 5px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>股票分析报告</h1>
                <p>报告生成时间: {current_time}</p>
            </div>
        """.format(current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
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
