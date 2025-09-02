#!/usr/bin/env python3
"""
手动发送邮件工具
可以手动触发发送真实的每日摘要邮件
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import User, StockAnalysis
from services.email_service import EmailService
from datetime import date
import argparse

def send_daily_digest_to_user(user_id=None, email=None):
    """向指定用户发送每日摘要邮件"""
    db = SessionLocal()
    email_service = EmailService()
    
    try:
        # 查询用户
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
        elif email:
            user = db.query(User).filter(User.email == email).first()
        else:
            print("错误：必须指定用户ID或邮箱")
            return False
        
        if not user:
            print(f"错误：未找到用户 (ID: {user_id}, Email: {email})")
            return False
        
        if not user.email_notifications:
            print(f"用户 {user.username} 未开启邮件通知")
            return False
        
        # 获取用户订阅的股票代码
        subscribed_symbols = [sub.stock_symbol for sub in user.subscriptions]
        
        if not subscribed_symbols:
            print(f"用户 {user.username} 没有订阅任何股票")
            return False
        
        # 查询当天的分析报告
        today = date.today()
        analyses = db.query(StockAnalysis).filter(
            StockAnalysis.stock_symbol.in_(subscribed_symbols),
            StockAnalysis.analysis_date == today
        ).all()
        
        if not analyses:
            print(f"今天 ({today}) 没有找到 {user.username} 订阅股票的分析报告")
            return False
        
        print(f"找到 {len(analyses)} 个分析报告，准备发送邮件...")
        
        # 准备用户信息
        user_info = {
            'id': user.id,
            'email': user.email,
            'username': user.username
        }
        
        # 发送邮件
        success = email_service.send_daily_digest_email(user_info, analyses)
        
        if success:
            print(f"✅ 成功发送每日摘要邮件到 {user.email}")
            return True
        else:
            print(f"❌ 发送邮件到 {user.email} 失败")
            return False
            
    except Exception as e:
        print(f"❌ 发送邮件时发生错误: {e}")
        return False
    finally:
        db.close()

def send_daily_digest_to_all_users():
    """向所有开启邮件通知的用户发送每日摘要邮件"""
    db = SessionLocal()
    email_service = EmailService()
    
    try:
        # 查询所有开启了邮件通知的用户
        users = db.query(User).filter(User.email_notifications == True).all()
        
        if not users:
            print("没有用户开启邮件通知")
            return
        
        today = date.today()
        total_sent = 0
        total_failed = 0
        
        for user in users:
            try:
                # 获取用户订阅的股票代码
                subscribed_symbols = [sub.stock_symbol for sub in user.subscriptions]
                
                if not subscribed_symbols:
                    print(f"跳过用户 {user.username}：没有订阅任何股票")
                    continue
                
                # 查询当天的分析报告
                analyses = db.query(StockAnalysis).filter(
                    StockAnalysis.stock_symbol.in_(subscribed_symbols),
                    StockAnalysis.analysis_date == today
                ).all()
                
                if not analyses:
                    print(f"跳过用户 {user.username}：今天没有分析报告")
                    continue
                
                # 准备用户信息
                user_info = {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username
                }
                
                # 发送邮件
                success = email_service.send_daily_digest_email(user_info, analyses)
                
                if success:
                    print(f"✅ 已发送到 {user.email}")
                    total_sent += 1
                else:
                    print(f"❌ 发送失败到 {user.email}")
                    total_failed += 1
                    
            except Exception as e:
                print(f"❌ 处理用户 {user.username} 时发生错误: {e}")
                total_failed += 1
                continue
        
        print(f"\n📊 发送完成：成功 {total_sent} 个，失败 {total_failed} 个")
        
    except Exception as e:
        print(f"❌ 发送邮件时发生错误: {e}")
    finally:
        db.close()

def list_users_with_notifications():
    """列出所有开启邮件通知的用户"""
    db = SessionLocal()
    
    try:
        users = db.query(User).filter(User.email_notifications == True).all()
        
        if not users:
            print("没有用户开启邮件通知")
            return
        
        print("开启邮件通知的用户列表：")
        print("-" * 60)
        for user in users:
            stock_count = len(user.subscriptions)
            print(f"ID: {user.id:3d} | 用户名: {user.username:15s} | 邮箱: {user.email:25s} | 订阅股票: {stock_count:2d}")
        
    except Exception as e:
        print(f"❌ 查询用户时发生错误: {e}")
    finally:
        db.close()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="手动发送每日摘要邮件工具")
    parser.add_argument('--user-id', type=int, help='指定用户ID发送邮件')
    parser.add_argument('--email', type=str, help='指定用户邮箱发送邮件')
    parser.add_argument('--all', action='store_true', help='向所有用户发送邮件')
    parser.add_argument('--list', action='store_true', help='列出开启邮件通知的用户')
    
    args = parser.parse_args()
    
    if args.list:
        list_users_with_notifications()
    elif args.all:
        print("开始向所有用户发送每日摘要邮件...")
        send_daily_digest_to_all_users()
    elif args.user_id:
        send_daily_digest_to_user(user_id=args.user_id)
    elif args.email:
        send_daily_digest_to_user(email=args.email)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
