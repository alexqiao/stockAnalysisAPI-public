from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.database import get_db
from app.db.models import User, StockAnalysis
from app.core.security import authenticate_user, create_access_token, get_current_user, get_password_hash
from datetime import timedelta, date
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首页"""
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """注册页面"""
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """处理注册表单提交"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "用户名已存在"}
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "邮箱已注册"}
        )
    
    # 创建新用户
    db_user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 注册成功后重定向到登录页面
    return RedirectResponse(url="/login", status_code=303)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页面"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """处理登录表单提交"""
    print(f"登录尝试: username={username}, password={password}")
    user = authenticate_user(db, username, password)
    if not user:
        print(f"登录失败: 用户名或密码错误. authenticate_user returned None for username={username}")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "用户名或密码错误"}
        )
    
    print(f"登录成功: {user.username}. User ID: {user.id}")
    # 创建访问令牌
    access_token_expires = timedelta(days=7)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    print(f"生成的token: {access_token[:20]}...")
    
    # 设置cookie并重定向到仪表盘
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        # httponly=True, # 移除 httponly 以允许前端JS访问
        max_age=7 * 24 * 60 * 60  # 7天
    )
    print(f"重定向到: /dashboard")
    return response


@router.post("/logout")
async def logout():
    """退出登录"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """仪表盘页面"""
    # 从cookie中获取当前用户
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    print(f"User authenticated: {user.username}")
    
    # 获取用户的订阅
    subscribed_stocks = user.subscriptions
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "subscriptions": subscribed_stocks
        }
    )


async def get_current_user_from_cookie(request: Request, db: Session) -> Optional[User]:
    """从cookie中获取当前用户"""
    token = request.cookies.get("access_token")
    print(f"Cookie token: {token}")
    
    # 处理可能的引号包围
    if token and token.startswith('"') and token.endswith('"'):
        token = token[1:-1]
    
    if not token or not token.startswith("Bearer "):
        print("No valid token found in cookie")
        return None
    
    try:
        token_value = token.split(" ")[1]
        print(f"Token value: {token_value}")
        
        # 直接解码JWT token而不是调用get_current_user依赖项
        from jose import JWTError, jwt
        from app.core.security import SECRET_KEY, ALGORITHM
        
        payload = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            print("No username in token payload")
            return None
        
        # 从数据库获取用户
        user = db.query(User).filter(User.username == username).first()
        print(f"User found: {user.username if user else None}")
        return user
        
    except JWTError as e:
        print(f"JWT Error: {e}")
        return None
    except Exception as e:
        print(f"Error getting current user: {e}")
        return None


@router.get("/analysis/{symbol}/{analysis_date_str}", response_class=HTMLResponse)
async def detailed_analysis(
    request: Request,
    symbol: str,
    analysis_date_str: str,
    db: Session = Depends(get_db)
):
    """股票详细分析页面"""
    try:
        # 将日期字符串转换为日期对象
        analysis_date = date.fromisoformat(analysis_date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式无效，请使用YYYY-MM-DD格式")
    
    # 查询数据库中的分析记录
    analysis = db.query(StockAnalysis).filter(
        and_(
            StockAnalysis.stock_symbol == symbol.upper(),
            StockAnalysis.analysis_date == analysis_date
        )
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="分析记录未找到")
    
    # 准备模板数据
    analysis_data = {
        "symbol": symbol.upper(),
        "analysis_date": analysis_date,
        "analysis_result": analysis.analysis_result or {},
        "latest_price_data": analysis.latest_price_data or {},
        "news_data": analysis.news_data or []
    }
    
    return templates.TemplateResponse(
        "detailed_analysis.html",
        {
            "request": request,
            "analysis": analysis_data
        }
    )
