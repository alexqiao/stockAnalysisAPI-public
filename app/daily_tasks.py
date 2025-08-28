from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import User, Subscription, StockAnalysis
from datetime import date
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
        
    def run_daily_stock_analysis(self):
        """运行每日股票分析任务"""
        logger.info("Starting daily stock analysis...")
        
        db = SessionLocal()
        try:
            # 1. 查询所有不重复的股票代码
            unique_symbols = db.query(Subscription.stock_symbol).distinct().all()
            unique_symbols = [symbol[0] for symbol in unique_symbols]
            
            if not unique_symbols:
                logger.info("No subscribed stocks found for analysis")
                return
            
            logger.info(f"Found {len(unique_symbols)} unique stock symbols to analyze: {unique_symbols}")
            
            # 2. 遍历股票代码列表
            for symbol in unique_symbols:
                try:
                    logger.info(f"Analyzing stock: {symbol}")
                    
                    # 3. 调用 AlphaVantage API 获取数据
                    news_data = self.alpha_api.get_stock_news(symbol)
                    price_data = self.alpha_api.get_daily_prices(symbol)
                    
                    if not news_data or not price_data:
                        logger.warning(f"Skipping {symbol}: Failed to fetch data from AlphaVantage")
                        continue
                    
                    # 4. 调用 AIAnalyzer 服务进行分析
                    analysis_result = self.ai_analyzer.analyze_stock_news(symbol, news_data, price_data)
                    
                    # 5. 检查并处理分析错误
                    if "error" in analysis_result:
                        logger.error(f"AI analysis failed for {symbol}: {analysis_result['error']}")
                        continue
                    
                    # 6. 删除当天已存在的相同股票代码记录（幂等性）
                    today = date.today()
                    db.query(StockAnalysis).filter(
                        StockAnalysis.stock_symbol == symbol,
                        StockAnalysis.analysis_date == today
                    ).delete()
                    
                    # 保存分析结果到数据库
                    stock_analysis = StockAnalysis(
                        stock_symbol=symbol,
                        analysis_date=today,
                        analysis_result=analysis_result.get("analysis", {}),
                        latest_price_data=price_data,
                        news_data=news_data
                    )
                    
                    db.add(stock_analysis)
                    db.commit()
                    
                    logger.info(f"Successfully analyzed and saved {symbol}")
                    
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    db.rollback()
                    continue
        
        except Exception as e:
            logger.error(f"Error in daily stock analysis: {e}")
            db.rollback()
        finally:
            db.close()
            
        logger.info("Daily stock analysis completed")
        
    def generate_daily_reports(self):
        """生成并发送每日报告（保留原有功能）"""
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
        # 每天上午9:00运行股票分析
        self.scheduler.add_job(
            self.run_daily_stock_analysis,
            CronTrigger(hour=9, minute=0),
            id='daily_stock_analysis',
            name='Daily stock analysis',
            replace_existing=True
        )
        
        # 保留原有的报告发送功能（可选）
        self.scheduler.add_job(
            self.generate_daily_reports,
            CronTrigger(hour=10, minute=0),  # 稍后运行报告发送
            id='daily_report',
            name='Daily report generation',
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
