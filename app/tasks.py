from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Subscription
from services.alpha_vantage_api import AlphaVantageAPI
from services.ai_analyzer import AIAnalyzer
from services.email_service import EmailService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailyReportScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.alpha_api = AlphaVantageAPI()
        self.ai_analyzer = AIAnalyzer()
        self.email_service = EmailService()
        
    def generate_daily_reports(self):
        """生成并发送每日报告"""
        logger.info("Starting daily report generation...")
        
        db = SessionLocal()
        try:
            # 获取所有用户
            users = db.query(User).all()
            
            for user in users:
                # 获取用户订阅的股票
                subscriptions = db.query(Subscription).filter(
                    Subscription.user_id == user.id
                ).all()
                
                if not subscriptions:
                    continue
                
                analyses = []
                for subscription in subscriptions:
                    symbol = subscription.stock_symbol
                    
                    try:
                        # 获取股票数据
                        news_data = self.alpha_api.get_stock_news(symbol)
                        price_data = self.alpha_api.get_daily_prices(symbol)
                        
                        if news_data:
                            # AI分析
                            analysis = self.ai_analyzer.analyze_stock_news(symbol, news_data, price_data)
                            analyses.append(analysis)
                    except Exception as e:
                        logger.error(f"Error analyzing {symbol}: {e}")
                        continue
                
                if analyses:
                    # 发送邮件
                    success = self.email_service.send_analysis_report(user.email, analyses)
                    if success:
                        logger.info(f"Report sent to {user.email}")
                    else:
                        logger.error(f"Failed to send report to {user.email}")
        
        except Exception as e:
            logger.error(f"Error in daily report generation: {e}")
        finally:
            db.close()
    
    def start(self):
        """启动定时任务"""
        # 每天上午9:00发送报告
        self.scheduler.add_job(
            self.generate_daily_reports,
            CronTrigger(hour=9, minute=0),
            id='daily_report',
            name='Daily stock analysis report',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Daily report scheduler started")
    
    def stop(self):
        """停止定时任务"""
        self.scheduler.shutdown()
        logger.info("Daily report scheduler stopped")

# 全局调度器实例
scheduler = DailyReportScheduler()
