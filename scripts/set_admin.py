# scripts/set_admin.py

import sys
import os
from sqlalchemy.orm import Session

# 将项目根目录添加到Python路径，以便导入app模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import User

def set_user_as_admin(username: str):
    """将指定用户设置为超级用户/管理员"""
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"❌ 错误: 未找到用户 '{username}'")
            return

        user.is_superuser = True
        db.commit()
        print(f"✅ 成功! 用户 '{username}' 现在是管理员了。")

    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python scripts/set_admin.py <要设为管理员的用户名>")
        sys.exit(1)
    
    target_username = sys.argv[1]
    set_user_as_admin(target_username)