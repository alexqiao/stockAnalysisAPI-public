# app/api/admin_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models import User, Subscription
from app.schemas import UserResponse, SubscriptionResponse, SubscriptionCreate
from app.core.security import get_current_admin_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin_user)] # 关键：此路由下的所有端点都需要管理员权限
)

@router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """获取所有用户列表"""
    return db.query(User).all()

@router.get("/users/{user_id}/subscriptions", response_model=List[SubscriptionResponse])
def get_user_subscriptions(user_id: int, db: Session = Depends(get_db)):
    """查看指定用户的股票订阅"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="未找到用户")
    return user.subscriptions

@router.post("/users/{user_id}/subscriptions", response_model=SubscriptionResponse)
def add_subscription_for_user(user_id: int, subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    """为指定用户添加股票订阅"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="未找到用户")

    # 检查是否已订阅
    existing = db.query(Subscription).filter_by(user_id=user_id, stock_symbol=subscription.stock_symbol.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="该用户已订阅此股票")

    db_sub = Subscription(user_id=user_id, stock_symbol=subscription.stock_symbol.upper())
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

@router.delete("/users/{user_id}/subscriptions/{symbol}")
def remove_subscription_for_user(user_id: int, symbol: str, db: Session = Depends(get_db)):
    """为指定用户删除股票订阅"""
    sub = db.query(Subscription).filter_by(user_id=user_id, stock_symbol=symbol.upper()).first()
    if not sub:
        raise HTTPException(status_code=404, detail="未找到该订阅记录")

    db.delete(sub)
    db.commit()
    return {"message": "成功删除订阅"}