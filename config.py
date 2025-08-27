import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 数据库配置
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stock_analysis.db")
    
    # Alpha Vantage API配置
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    
    # OpenAI API配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # 邮件配置
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    
    # JWT配置
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # 定时任务配置
    DAILY_REPORT_TIME = os.getenv("DAILY_REPORT_TIME", "09:00")
