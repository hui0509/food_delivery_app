#!/usr/bin/env python3
import sys
import os
import bcrypt

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def hash_password(password: str) -> str:
    """生成密码哈希"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def migrate_existing_passwords():
    """迁移现有明文密码到哈希密码"""
    try:
        # 先导入数据库相关模块
        from sqlalchemy import text, create_engine

        # 数据库连接配置 - 根据实际配置修改

        db_url = "mysql+pymysql://root:root@localhost:3306/dba"

        # 创建数据库引擎
        engine = create_engine(db_url)

        # 获取所有用户的明文密码
        with engine.connect() as conn:
            users = conn.execute(
                text("SELECT id, username, password FROM user")
            ).fetchall()

            migrated_count = 0
            for user in users:
                user_id, username, plain_password = user

                # 跳过已哈希的密码（bcrypt哈希有特定格式）
                if plain_password and (plain_password.startswith("$2b$") or plain_password.startswith("$2a$")):
                    print(f"用户 {username} 的密码已哈希，跳过")
                    continue

                # 哈希明文密码
                hashed_password = hash_password(plain_password)

                # 更新数据库
                conn.execute(
                    text("UPDATE user SET password = :password WHERE id = :id"),
                    {"password": hashed_password, "id": user_id}
                )
                conn.commit()
                migrated_count += 1
                print(f"已迁移用户 {username} 的密码")

            print(f"密码迁移完成，共迁移 {migrated_count} 个用户")
            return True

    except Exception as e:
        print(f"密码迁移失败: {e}")
        return False


if __name__ == "__main__":
    # 输入数据库连接信息
    print("请输入数据库连接信息：")
    db_user = "root"
    db_password ="root"
    db_host = "localhost"
    db_port = "3306"
    db_name = "dba"

    # 设置全局数据库URL
    import os

    os.environ['DATABASE_URL'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    migrate_existing_passwords()