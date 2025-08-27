from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    
    def get_subscribed_stocks_list(self):
        """获取用户订阅的股票代码列表"""
        return [sub.stock_symbol for sub in self.subscriptions]

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_symbol = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="subscriptions")

class StockAnalysis(Base):
    __tablename__ = "stock_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_symbol = Column(String(10), nullable=False, index=True)
    news_data = Column(Text)
    analysis_result = Column(Text)
    recommendation = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
