class BaseConfig(object):
    # 应用配置
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'your-secret-key-here'  # 请修改为强密钥

    # 数据库配置
    DIALCT = "mysql"
    DRITVER = "pymysql"
    HOST = '127.0.0.1'
    PORT = "3306"
    USERNAME = "root"
    PASSWORD = "root"  # 数据库的密码
    DBNAME = 'dba'

    # SQLAlchemy 配置
    SQLALCHEMY_DATABASE_URI = f"{DIALCT}+{DRITVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?charset=utf8"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 建议设置为 False 以避免性能警告
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20,
    }

    # Redis 配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB = 0
    REDIS_PASSWORD =123 # 如果有密码请设置

    # 会话配置（如果使用 Redis 存储会话）
    SESSION_TYPE = 'redis'
    SESSION_REDIS = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

    # 跨域配置
    CORS_ORIGINS = "*"
    CORS_SUPPORTS_CREDENTIALS = True