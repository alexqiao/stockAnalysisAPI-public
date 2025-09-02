#!/usr/bin/env python3
"""
测试邮件发送功能
使用账号 ccppaap 密码 password123 测试邮件发送
"""

import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine
from app.db.models import User
from services.email_service import EmailService

def get_user_email(username: str) -> str:
    """获取指定用户的邮箱地址"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            print(f"找到用户: {username}, 邮箱: {user.email}")
            return user.email
        else:
            print(f"用户 {username} 不存在")
            return None
    finally:
        db.close()

def test_email_send():
    """测试邮件发送功能"""
    print("开始测试邮件发送功能...")
    
    # 获取 ccppaap 用户的邮箱
    email = get_user_email("ccppaap")
    if not email:
        print("无法获取用户邮箱，测试终止")
        return False
    
    # 创建邮件服务实例
    try:
        email_service = EmailService()
        print("邮件服务初始化成功")
    except ValueError as e:
        print(f"邮件服务初始化失败: {e}")
        return False
    
    # 创建测试分析数据
    test_analyses = [
        {
            "symbol": "AAPL",
            "analysis": {
                "recommendation": "buy",
                "overall_sentiment": "positive",
                "risk_level": "low",
                "key_points": [
                    "苹果公司季度财报超出预期",
                    "iPhone 销量强劲增长",
                    "服务业务收入创新高"
                ],
                "technical_analysis": "股价突破阻力位，形成上升趋势",
                "reasoning": "基本面强劲，技术面支持上涨"
            }
        },
        {
            "symbol": "TSLA",
            "analysis": {
                "recommendation": "hold",
                "overall_sentiment": "neutral",
                "risk_level": "high",
                "key_points": [
                    "特斯拉交付量符合预期",
                    "市场竞争加剧",
                    "自动驾驶技术进展缓慢"
                ],
                "technical_analysis": "股价在关键支撑位附近震荡",
                "reasoning": "等待更明确的市场信号"
            }
        }
    ]
    
    # 发送测试邮件
    print(f"准备发送测试邮件到: {email}")
    success = email_service.send_analysis_report(email, test_analyses)
    
    if success:
        print("✅ 邮件发送测试成功！")
        print(f"测试邮件已发送到: {email}")
        return True
    else:
        print("❌ 邮件发送测试失败")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("股票分析API - 邮件发送功能测试")
    print("=" * 50)
    
    success = test_email_send()
    
    print("=" * 50)
    if success:
        print("测试完成: ✅ 成功")
        sys.exit(0)
    else:
        print("测试完成: ❌ 失败")
        sys.exit(1)
