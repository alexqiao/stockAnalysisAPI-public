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
    """获取股票分析报告"""
    symbol = symbol.upper()
    
    # 查询数据库获取最新的分析报告
    latest_analysis = db.query(StockAnalysis).filter(
        StockAnalysis.stock_symbol == symbol
    ).order_by(
        StockAnalysis.analysis_date.desc()
    ).first()
    
    # 如果找不到记录，返回404错误
    if not latest_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"股票 {symbol} 的分析报告尚未生成，请稍后再试。"
        )
    
    # 格式化响应数据
    try:
        news_data = latest_analysis.news_data or {}
        return {
            "symbol": latest_analysis.stock_symbol,
            "analysis_date": latest_analysis.analysis_date.isoformat(),
            "news": news_data.get("news", []) if isinstance(news_data, dict) else [],
            "analysis": latest_analysis.analysis_result if latest_analysis.analysis_result is not None else {},
            "latest_data": latest_analysis.latest_price_data if latest_analysis.latest_price_data is not None else {}
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理分析报告时发生内部错误: {str(e)}"
        )

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
