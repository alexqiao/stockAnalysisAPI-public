#!/usr/bin/env python3
"""
邮箱更新功能测试脚本
用于测试邮箱更新API是否正常工作
"""

import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_email_update_api():
    """测试邮箱更新API导入和基本功能"""
    
    print("=" * 50)
    print("邮箱更新功能测试")
    print("=" * 50)
    
    try:
        # 测试schemas导入
        from app.schemas import UserUpdateEmail
        print("✅ UserUpdateEmail模型导入成功")
        
        # 测试API路由导入
        from app.api.main_api_router import router
        print("✅ API路由导入成功")
        
        # 检查是否有邮箱更新端点
        endpoints = [route.path for route in router.routes]
        email_endpoint = "/users/me/email"
        
        if email_endpoint in endpoints:
            print(f"✅ 邮箱更新端点存在: {email_endpoint}")
        else:
            print(f"❌ 邮箱更新端点不存在")
            print(f"可用端点: {[e for e in endpoints if 'email' in e or 'user' in e]}")
            return False
        
        # 测试模型验证
        try:
            # 测试有效邮箱
            valid_email = UserUpdateEmail(email="test@example.com")
            print("✅ 有效邮箱验证通过")
            
            # 测试无效邮箱
            try:
                invalid_email = UserUpdateEmail(email="invalid-email")
                print("❌ 无效邮箱验证应该失败但没有失败")
                return False
            except Exception:
                print("✅ 无效邮箱验证正确失败")
                
        except Exception as e:
            print(f"❌ 模型验证测试失败: {e}")
            return False
            
        print("\n🎉 邮箱更新功能测试通过！")
        print("\n使用方法:")
        print("1. 登录后进入仪表盘页面")
        print("2. 点击邮箱旁边的'修改'按钮")
        print("3. 输入新邮箱地址并保存")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_email_update_api()
    sys.exit(0 if success else 1)
