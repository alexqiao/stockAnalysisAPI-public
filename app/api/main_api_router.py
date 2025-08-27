from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from app.db.database import get_db
from app.db.models import User, Subscription, StockAnalysis
from app.schemas import UserCreate, UserResponse, SubscriptionCreate, SubscriptionResponse, StockAnalysisResponse, Token
from app.core.security import authenticate_user, create_access_token, get_current_user, get_password_hash, get_current_user_from_cookie_or_header
from services.alpha_vantage_api import AlphaVantageAPI
from services.ai_analyzer import AIAnalyzer
from services.email_service import EmailService
from typing import List

router = APIRouter()

# 初始化服务
alpha_api = AlphaVantageAPI()
ai_analyzer = AIAnalyzer()
email_service = EmailService()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # 创建新用户
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@router.post("/subscribe", response_model=SubscriptionResponse)
def subscribe_stock(
    request: Request,
    subscription: SubscriptionCreate,
    current_user: User = Depends(get_current_user_from_cookie_or_header),
    db: Session = Depends(get_db)
):
    """订阅股票"""
    # 检查是否已订阅
    existing = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.stock_symbol == subscription.stock_symbol.upper()
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Stock already subscribed"
        )
    
    # 创建订阅
    db_subscription = Subscription(
        user_id=current_user.id,
        stock_symbol=subscription.stock_symbol.upper()
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

@router.delete("/unsubscribe/{symbol}")
def unsubscribe_stock(
    symbol: str,
    current_user: User = Depends(get_current_user_from_cookie_or_header),
    db: Session = Depends(get_db)
):
    """取消订阅股票"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.stock_symbol == symbol.upper()
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )
    
    db.delete(subscription)
    db.commit()
    return {"message": "Unsubscribed successfully"}

@router.get("/subscriptions", response_model=List[SubscriptionResponse])
def get_subscriptions(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie_or_header),
    db: Session = Depends(get_db)
):
    """获取用户订阅的股票"""
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).all()
    return subscriptions

@router.get("/analyze/{symbol}")
def analyze_stock(
    request: Request,
    symbol: str,
    current_user: User = Depends(get_current_user_from_cookie_or_header),
    db: Session = Depends(get_db)
):
    """分析股票"""
    symbol = symbol.upper()
    
    # 获取股票数据
    news_data = alpha_api.get_stock_news(symbol)
    price_data = alpha_api.get_daily_prices(symbol)
    
    # **关键修改：在这里检查数据获取是否成功**
    if not news_data or not price_data:
        # 如果任一数据获取失败，则提前返回错误，不再调用AI
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, # 504 表示上游服务器（Alpha Vantage）无响应
            detail=f"无法从上游服务获取 {symbol} 的完整数据，请稍后重试。"
        )
    print("news data and price data fetched successfully")

    
    # AI分析
    analysis_result = ai_analyzer.analyze_stock_news(symbol, news_data, price_data)
    
    # **关键修改：检查分析结果中是否有error字段**
    if "error" in analysis_result:
        # 如果有错误，则向前端返回 502 Bad Gateway 错误
        # 这比返回 200 OK 更准确，因为它表示上游服务（AI模型）出了问题
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI分析服务失败: {analysis_result['error']}"
        )

    return {
        "symbol": symbol,
        "news": news_data.get("news", []),
        "analysis": analysis_result.get("analysis", {}),
        "latest_data": price_data  # Add the latest daily stock data
    }

@router.post("/send-report")
def send_daily_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发送每日报告"""
    # 获取用户订阅的股票
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).all()
    
    if not subscriptions:
        raise HTTPException(
            status_code=404,
            detail="No subscriptions found"
        )
    
    analyses = []
    for subscription in subscriptions:
        symbol = subscription.stock_symbol
        
        # 获取股票数据
        news_data = alpha_api.get_stock_news(symbol)
        price_data = alpha_api.get_daily_prices(symbol)
        
        if news_data:
            # AI分析
            analysis = ai_analyzer.analyze_stock_news(symbol, news_data, price_data)
            analyses.append(analysis)
    
    if analyses:
        # 发送邮件
        success = email_service.send_analysis_report(current_user.email, analyses)
        if success:
            return {"message": "Report sent successfully"}
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send report"
            )
    
    return {"message": "No data to analyze"}

@router.post("/toggle-notifications")
def toggle_email_notifications(
    enabled: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """切换邮件通知设置"""
    current_user.email_notifications = enabled
    db.commit()
    return {"message": "Email notifications updated", "enabled": enabled}
