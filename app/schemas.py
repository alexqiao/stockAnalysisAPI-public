from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    stock_symbol: str


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class StockAnalysisResponse(BaseModel):
    stock_symbol: str
    news_data: Optional[str]
    analysis_result: Optional[str]
    recommendation: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
