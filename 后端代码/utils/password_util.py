import bcrypt


class PasswordUtil:
    @staticmethod
    def hash_password(password: str) -> str:
        """生成密码哈希"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            # 如果是旧的明文密码，尝试直接比较（迁移期间）
            return password == hashed_password