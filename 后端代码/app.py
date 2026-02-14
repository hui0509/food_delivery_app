# import caching as caching
from werkzeug.wrappers import Response
import time
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from sqlalchemy import text, func
from datetime import datetime, timedelta
import urllib.parse
import os
import uuid
import re
from werkzeug.utils import secure_filename
from pypinyin import pinyin, Style
import bcrypt

from functools import wraps
from config import BaseConfig
from flask_sqlalchemy import SQLAlchemy
import auth
import json
import random
from redis.exceptions import ConnectionError as RedisConnectionError
from redis import StrictRedis

# 创建redis对象
# redis_store = StrictRedis(host=BaseConfig.REDIS_HOST, port=BaseConfig.REDIS_PORT, decode_responses=True)

try:
    redis_store = StrictRedis(
        host=BaseConfig.REDIS_HOST,
        port=BaseConfig.REDIS_PORT,
        decode_responses=True,
        socket_timeout=5
    )
    # 测试连接
    redis_store.ping()
    print("Redis连接成功")
except (RedisConnectionError, Exception) as e:
    print(f"Redis连接失败，使用内存缓存: {e}")
    # 使用内存字典作为回退方案
    redis_store = None
    redis_cache = {}

# 跨域

app = Flask(__name__)
# 允许所有来源访问（开发环境）
# 允许所有来源访问，并支持凭证和所有请求头
# 修复：动态CORS配置，支持任意端口访问
# 使用动态CORS配置，支持任意端口访问
def get_allowed_origins():
    """动态生成允许的域名列表"""
    base_domains = [
        "localhost",
        "127.0.0.1", 
        "192.168.0.100",
        "192.168.110.1"
    ]
    
    origins = []
    for domain in base_domains:
        # 添加常见端口
        for port in [3000, 5000, 8080, 8000, 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009]:
            origins.append(f"http://{domain}:{port}")
        # 添加不带端口的（用于默认端口80）
        origins.append(f"http://{domain}")
    
    # 开发环境：允许所有本地IP的任意端口
    # 注意：生产环境需要严格限制
    origins.append("http://localhost:*")
    origins.append("http://127.0.0.1:*")
    origins.append("http://192.168.*:*")
    
    return origins

CORS(app, supports_credentials=True, origins=get_allowed_origins(), allow_headers=["Content-Type", "token", "Authorization"])

# 添加配置数据库
app.config.from_object(BaseConfig)
# 初始化拓展,app到数据库的ORM映射
db = SQLAlchemy(app)

# 检查数据库连接是否成功
with app.app_context():
    with db.engine.connect() as conn:
        rs = conn.execute(text("select 1"))
        print(rs.fetchone())

import base64
from io import BytesIO




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
            # 如果是 bcrypt 哈希密码
            if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
                return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
            # 否则是旧的明文密码
            return password == hashed_password
        except Exception:
            return False


class ReviewLike(db.Model):
    """评价点赞模型"""
    __tablename__ = 'review_like'

    like_id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, nullable=False, index=True)
    user_phone = db.Column(db.String(20), nullable=False, index=True)
    created_time = db.Column(db.DateTime, default=datetime.now)


class Review(db.Model):
    __tablename__ = 'review'

    review_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False)
    shop_id = db.Column(db.Integer, nullable=False)
    dish_id = db.Column(db.Integer)
    user_phone = db.Column(db.String(20), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    review_type = db.Column(db.String(10), default='shop')
    created_time = db.Column(db.DateTime, default=datetime.now)
    # 新增字段
    likes_count = db.Column(db.Integer, default=0)

# 新建文件：ai_service.py
import requests
import json
import re
from typing import Dict, List, Optional
from flask import current_app





# 在app.py中配置
app.config['DEEPSEEK_API_KEY'] = 'sk-4a4d0abca4af4ae08f297e2ed037bc0b'


# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_english_filename(original_name, entity_name, entity_type="item"):

    # 将中文转换为拼音
    pinyin_list = pinyin(entity_name, style=Style.NORMAL)
    base_name = '_'.join([item[0] for item in pinyin_list])

    # 清理特殊字符，只保留字母、数字、下划线
    base_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
    base_name = re.sub(r'_+', '_', base_name)
    base_name = base_name.strip('_').lower()

    # 如果处理后名称为空，使用默认名称
    if not base_name:
        base_name = entity_type

    # 获取文件扩展名
    ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'jpg'
    # 添加唯一标识符避免重名
    unique_id = str(uuid.uuid4())[:8]
    return f"{base_name}_{unique_id}.{ext}"


def get_frontend_image_path(sub_dir="shop"):

    # 后端代码目录
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    # 前端公共目录路径
    frontend_public_dir = os.path.join(
        backend_dir,
        '..',
        '前端代码',
        'sjk',
        'public',
        'images',
        sub_dir
    )
    return os.path.abspath(frontend_public_dir)


def save_uploaded_image(image_file, entity_name, entity_type="shop"):
    try:
        if not allowed_file(image_file.filename):
            return False, None, "不支持的文件格式，请上传图片文件"

        # 生成文件名和路径
        filename = generate_english_filename(image_file.filename, entity_name, entity_type)
        upload_dir = get_frontend_image_path(entity_type)

        # 确保上传目录存在
        os.makedirs(upload_dir, exist_ok=True)

        # 保存文件
        file_path = os.path.join(upload_dir, filename)
        image_file.save(file_path)

        # 生成前端访问URL
        image_url = f"/images/{entity_type}/{filename}"

        print(f"图片已保存到: {file_path}")
        print(f"前端访问URL: {image_url}")

        return True, image_url, None

    except Exception as e:
        print(f"保存图片错误: {e}")
        return False, None, "保存图片失败"


def delete_old_image(image_url, entity_type="shop"):
    try:
        # 获取文件名
        filename = os.path.basename(image_url)

        # 检查是否是默认图片，默认图片不删除
        default_images = {
            "shop": "default-shop.jpg",
            "dish": "default-dish.jpg"
        }

        if (filename and
                filename != default_images.get(entity_type) and
                image_url != f"/images/{entity_type}/{default_images.get(entity_type)}"):

            upload_dir = get_frontend_image_path(entity_type)
            old_image_path = os.path.join(upload_dir, filename)

            if os.path.exists(old_image_path):
                os.remove(old_image_path)
                print(f"已删除旧图片: {old_image_path}")
                return True

    except Exception as e:
        print(f"删除旧图片失败: {e}")

    return False





def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('token')
        phone = get_token_phone(token)
        if not phone:
            return jsonify({"status": 1001, "msg": "请重新登录"})

        # 关键：校验 role，必须是 1（管理员）
        user_result = db.session.execute(
            text("SELECT role FROM user WHERE telephone = :phone"),
            {"phone": phone}
        ).fetchone()

        if not user_result or user_result.role != 1:
            return jsonify({"status": 403, "msg": "权限不足，只有管理员可以访问此接口"})

        # 把当前管理员的 phone 注入到 request 中，方便后面接口直接用
        request.current_admin_phone = phone
        return f(*args, **kwargs)
    return decorated_function



# 新增超级管理员校验装饰器：在后端定义一个新的 @super_admin_required 装饰器
def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('token')
        phone = get_token_phone(token)
        if not phone:
            return jsonify({"status": 1001, "msg": "请重新登录"})
        # 查询用户角色和超级管理员标志
        user = db.session.execute(
            text("SELECT role, is_super FROM user WHERE telephone = :phone"),
            {"phone": phone}
        ).fetchone()
        # 只有 role=1 且 is_super=1 才算超级管理员
        if not user or user.role != 1 or user.is_super != 1:
            return jsonify({"status": 403, "msg": "权限不足，只有超级管理员可以访问此接口"})
        # 保存当前管理员手机号供后续使用
        request.current_admin_phone = phone
        return f(*args, **kwargs)
    return decorated_function


# 用户登录
@app.route("/api/user/login", methods=["POST"])
@cross_origin()
def user_login():
    try:
        if not request.json:
            return jsonify({"code": 1001, "msg": "请求数据格式错误"})

        userortel = request.json.get("userortel", "").strip()
        password = request.json.get("password", "").strip()

        if not userortel or not password:
            return jsonify({"code": 1002, "msg": "用户名/手机号和密码不能为空"})

        # 先查询用户
        sql = text('''
            SELECT * FROM user 
            WHERE username = :userortel OR telephone = :userortel
        ''')
        data = db.session.execute(sql, {'userortel': userortel}).first()

        if data and PasswordUtil.verify_password(password, data[2]):  # data[2] 是 password
            user = {
                'id': data[0],
                'username': data[1],
                'password': data[2],  # 仍然是哈希密码
                'telephone': data[3],
                'role': data[4],
                'is_super': data[6]
            }

            token_bytes = auth.encode_func(user)
            token = token_bytes.decode('utf-8') if isinstance(token_bytes, bytes) else token_bytes

            return jsonify({
                "code": 200,
                "msg": "登录成功",
                "token": token,
                "role": data[4],
                "is_super": data[6]
            })
        else:
            return jsonify({"code": 1000, "msg": "用户名/手机号或密码错误"})

    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({"code": 500, "msg": "系统错误"})

# 用户注册
@app.route("/api/user/register/test", methods=["POST"])
@cross_origin()
def register_test():
    try:
        rq = request.json
        username = rq.get("username")
        password = rq.get("password")
        telephone = rq.get("telephone")
        role = rq.get("role", 0)

        if not all([username, password, telephone]):
            return jsonify({"status": 1001, "msg": "用户名、密码和手机号不能为空"})

        if role not in [0, 1]:
            return jsonify({"status": 1002, "msg": "角色参数无效"})

        # 检查用户名或手机号是否已存在
        exist_check = db.session.execute(
            text("SELECT id, username, telephone FROM user WHERE username = :username OR telephone = :telephone"),
            {"username": username, "telephone": telephone}
        ).fetchone()

        if exist_check:
            if exist_check.telephone == telephone:
                return jsonify({"status": 1000, "msg": "该手机号已注册"})
            else:
                return jsonify({"status": 1000, "msg": "该用户名已存在"})

        # 密码哈希处理
        hashed_password = PasswordUtil.hash_password(password)

        # 插入用户
        db.session.execute(
            text("""
                INSERT INTO user (username, password, telephone, role, is_super) 
                VALUES (:username, :password, :telephone, :role, 0)
            """),
            {"username": username, "password": hashed_password, "telephone": telephone, "role": role}
        )

        # 获取用户 id
        result = db.session.execute(
            text("SELECT id FROM user WHERE telephone = :telephone"),
            {"telephone": telephone}
        )
        user_id = result.fetchone()[0]

        # 插入用户信息
        db.session.execute(
            text("""
                INSERT INTO user_msg 
                (id, real_name, sex, age, mail, phone, user_name) 
                VALUES 
                (:id, '', '', NULL, '', :phone, :user_name)
            """),
            {
                "id": user_id,
                "phone": telephone,
                "user_name": username
            }
        )

        db.session.commit()
        return jsonify({"status": 200, "msg": "注册成功"})

    except Exception as e:
        db.session.rollback()
        print(f"注册失败: {e}")
        return jsonify({"status": 500, "msg": "注册失败，请稍后重试"})

# 找回密码（重置密码）
@app.route("/api/user/resetPassword", methods=["POST"])
@cross_origin()
def reset_password():
    try:
        rq = request.json
        telephone = rq.get("telephone")
        new_password = rq.get("newPassword")

        if not all([telephone, new_password]):
            return jsonify({"status": 1001, "msg": "手机号和新密码不能为空"})

        # 检查手机号是否存在
        user_check = db.session.execute(
            text("SELECT id FROM user WHERE telephone = :telephone"),
            {"telephone": telephone}
        ).fetchone()

        if not user_check:
            return jsonify({"status": 1003, "msg": "该手机号未注册"})

        # 密码哈希处理
        hashed_password = PasswordUtil.hash_password(new_password)

        # 更新密码
        db.session.execute(
            text("UPDATE user SET password = :password WHERE telephone = :telephone"),
            {"password": hashed_password, "telephone": telephone}
        )

        db.session.commit()
        return jsonify({"status": 200, "msg": "密码重置成功"})

    except Exception as e:
        db.session.rollback()
        print(f"密码重置失败: {e}")
        return jsonify({"status": 500, "msg": "密码重置失败，请稍后重试"})


# 获取店铺详情
@app.route("/api/shops/<int:shop_id>", methods=["GET"])
@cross_origin()
def get_shop_detail(shop_id):
    try:
        print(f"获取店铺详情: {shop_id}")

        # 查询店铺信息
        shop_query = text("""
            SELECT shop_id, shop_name, description, image_url, status 
            FROM shop 
            WHERE shop_id = :shop_id
        """)

        shop_data = db.session.execute(shop_query, {'shop_id': shop_id}).fetchone()

        if shop_data:
            shop = {
                'shop_id': shop_data[0],
                'shop_name': shop_data[1],
                'description': shop_data[2],
                'image_url': shop_data[3],
                'status': shop_data[4]
            }
            return jsonify(status=200, data=shop)
        else:
            return jsonify(status=404, msg="店铺不存在")

    except Exception as e:
        print(f"获取店铺详情错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 获取店铺菜品列表
@app.route("/api/shops/<int:shop_id>/dishes", methods=["GET"])
@cross_origin()
def get_shop_dishes(shop_id):
    try:
        print(f"获取店铺菜品列表: {shop_id}")

        # 查询店铺菜品
        dishes_query = text("""
            SELECT dish_id, dish_name, price, description, image_url, monthly_sales, status 
            FROM dish 
            WHERE shop_id = :shop_id AND status = 1
            ORDER BY sort_order, dish_id
        """)

        dishes_data = db.session.execute(dishes_query, {'shop_id': shop_id}).fetchall()

        dishes = []
        for row in dishes_data:
            dish = {
                'dish_id': row[0],
                'dish_name': row[1],
                'price': float(row[2]),
                'description': row[3],
                'image_url': row[4],
                'monthly_sales': row[5],
                'status': row[6]
            }
            dishes.append(dish)

        return jsonify(status=200, data=dishes)

    except Exception as e:
        print(f"获取店铺菜品错误: {e}")
        return jsonify(status=500, msg="系统错误")


def get_token_phone(token):
    try:
        if not token:
            return None
        data = auth.decode_func(token)
        return data.get('telephone')
    except Exception as e:
        print(f"Token解析错误: {e}")
        return None


# 提交评价
@app.route("/api/review/submit", methods=["POST"])
@cross_origin()
def submit_review():
    try:
        data = request.json
        order_id = data.get('order_id')
        shop_id = data.get('shop_id')
        dish_id = data.get('dish_id')  # 可以为空（店铺评价）
        rating = data.get('rating')
        comment = data.get('comment', '')
        review_type = data.get('review_type', 'shop')  # shop 或 dish

        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        # 验证订单属于当前用户且已完成
        order_check = db.session.execute(
            text('SELECT order_id, checked FROM oorder WHERE order_id = :order_id AND cons_phone = :phone'),
            {'order_id': order_id, 'phone': user_phone}
        ).fetchone()

        if not order_check:
            return jsonify(status=400, msg="订单不存在")

        if order_check[1] != 2:
            return jsonify(status=400, msg="只能对已完成的订单进行评价")

        # 检查是否已评价过（同一订单、同一类型、同一菜品）
        existing_query = text('''
            SELECT review_id FROM review 
            WHERE order_id = :order_id AND user_phone = :phone 
            AND review_type = :review_type
        ''')
        params = {'order_id': order_id, 'phone': user_phone, 'review_type': review_type}

        if dish_id:
            existing_query = text('''
                SELECT review_id FROM review 
                WHERE order_id = :order_id AND user_phone = :phone 
                AND review_type = :review_type AND dish_id = :dish_id
            ''')
            params['dish_id'] = dish_id

        existing_review = db.session.execute(existing_query, params).fetchone()

        if existing_review:
            return jsonify(status=400, msg="已评价过")

        # 插入评价
        db.session.execute(text('''
            INSERT INTO review (order_id, shop_id, dish_id, user_phone, rating, comment, review_type)
            VALUES (:order_id, :shop_id, :dish_id, :user_phone, :rating, :comment, :review_type)
        '''), {
            'order_id': order_id,
            'shop_id': shop_id,
            'dish_id': dish_id,
            'user_phone': user_phone,
            'rating': rating,
            'comment': comment,
            'review_type': review_type
        })

        db.session.commit()
        return jsonify(status=200, msg="评价提交成功")

    except Exception as e:
        db.session.rollback()
        print(f"提交评价错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 获取店铺评价 - 修复时间格式化并添加头像
@app.route("/api/review/shop/<int:shop_id>", methods=["GET"])
@cross_origin()
def get_shop_reviews(shop_id):
    try:
        # 获取评价列表 - 包含头像
        reviews_query = text('''
            SELECT r.review_id, r.order_id, r.rating, r.comment, r.created_time,
                   u.username, u.telephone, um.avatar_url,
                   GROUP_CONCAT(DISTINCT od.dish_name) as dishes
            FROM review r
            LEFT JOIN user u ON r.user_phone = u.telephone
            LEFT JOIN user_msg um ON u.id = um.id
            LEFT JOIN order_detail od ON r.order_id = od.order_id
            WHERE r.shop_id = :shop_id AND r.review_type = 'shop'
            GROUP BY r.review_id, r.order_id, r.rating, r.comment, r.created_time, 
                     u.username, u.telephone, um.avatar_url
            ORDER BY r.created_time DESC
            LIMIT 20
        ''')

        reviews_data = db.session.execute(reviews_query, {'shop_id': shop_id}).fetchall()

        reviews = []
        for row in reviews_data:
            # 处理时间
            created_time = row[4]
            time_str = ""

            if created_time:
                try:
                    if isinstance(created_time, datetime):
                        time_str = created_time.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(created_time, str):
                        try:
                            dt = datetime.strptime(created_time, '%Y-%m-%d %H:%M:%S')
                            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            time_str = created_time
                    else:
                        time_str = str(created_time)
                except:
                    time_str = str(created_time) if created_time else ""

            # 处理头像URL
            avatar_url = row[7] or '/images/user/default-avatar.jpg'
            if avatar_url and not avatar_url.startswith('/') and not avatar_url.startswith('http'):
                avatar_url = '/' + avatar_url

            review = {
                'review_id': row[0],
                'order_id': row[1],
                'rating': row[2],
                'comment': row[3] or '',
                'created_time': time_str,
                'username': row[5] or f"用户{row[6][-4:]}" if row[6] else '匿名用户',
                'avatar_url': avatar_url,  # 添加头像字段
                'dishes': row[8].split(',') if row[8] else []
            }
            reviews.append(review)

        # 获取统计信息
        stats_query = text('''
            SELECT 
                COUNT(*) as total_reviews,
                AVG(rating) as avg_rating,
                COUNT(CASE WHEN rating = 5 THEN 1 END) as five_star,
                COUNT(CASE WHEN rating = 4 THEN 1 END) as four_star,
                COUNT(CASE WHEN rating = 3 THEN 1 END) as three_star,
                COUNT(CASE WHEN rating = 2 THEN 1 END) as two_star,
                COUNT(CASE WHEN rating = 1 THEN 1 END) as one_star
            FROM review
            WHERE shop_id = :shop_id AND review_type = 'shop'
        ''')

        stats_data = db.session.execute(stats_query, {'shop_id': shop_id}).fetchone()

        stats = {
            'total_reviews': stats_data[0] or 0,
            'avg_rating': round(float(stats_data[1] or 0), 1),
            'rating_distribution': {
                '5': stats_data[2] or 0,
                '4': stats_data[3] or 0,
                '3': stats_data[4] or 0,
                '2': stats_data[5] or 0,
                '1': stats_data[6] or 0
            }
        }

        return jsonify(status=200, data={'reviews': reviews, 'stats': stats})

    except Exception as e:
        print(f"获取店铺评价错误: {e}")
        return jsonify(status=500, msg="系统错误")

# 获取菜品评价
@app.route("/api/review/dish/<int:dish_id>", methods=["GET"])
@cross_origin()
def get_dish_reviews(dish_id):
    try:
        # 使用原生SQL查询，包含头像
        reviews_query = text('''
            SELECT r.review_id, r.order_id, r.rating, r.comment, r.created_time,
                   u.username, u.telephone, um.avatar_url
            FROM review r
            LEFT JOIN user u ON r.user_phone = u.telephone
            LEFT JOIN user_msg um ON u.id = um.id
            WHERE r.dish_id = :dish_id AND r.review_type = 'dish'
            ORDER BY r.created_time DESC
            LIMIT 15
        ''')

        reviews_data = db.session.execute(reviews_query, {'dish_id': dish_id}).fetchall()

        # 获取统计信息
        stats_query = text('''
            SELECT 
                COUNT(*) as total_reviews,
                AVG(rating) as avg_rating
            FROM review
            WHERE dish_id = :dish_id AND review_type = 'dish'
        ''')

        stats_data = db.session.execute(stats_query, {'dish_id': dish_id}).fetchone()

        reviews = []
        for row in reviews_data:
            # 处理时间
            created_time = row[4]
            if isinstance(created_time, datetime):
                time_str = created_time.strftime('%Y-%m-%d %H:%M:%S')
            elif created_time:
                try:
                    if isinstance(created_time, str):
                        time_str = created_time
                    else:
                        time_str = str(created_time)
                except:
                    time_str = ''
            else:
                time_str = ''

            # 处理头像URL
            avatar_url = row[7] or '/images/user/default-avatar.jpg'
            if avatar_url and not avatar_url.startswith('/') and not avatar_url.startswith('http'):
                avatar_url = '/' + avatar_url

            review = {
                'review_id': row[0],
                'order_id': row[1],
                'rating': row[2],
                'comment': row[3],
                'created_time': time_str,
                'username': row[5] or f"用户{row[6][-4:]}" if row[6] else '匿名用户',
                'avatar_url': avatar_url  # 添加头像字段
            }
            reviews.append(review)

        stats = {
            'total_reviews': stats_data[0] or 0,
            'avg_rating': round(float(stats_data[1] or 0), 1) if stats_data[1] else 0
        }

        return jsonify(status=200, data={'reviews': reviews, 'stats': stats})

    except Exception as e:
        print(f"获取菜品评价错误: {e}")
        return jsonify(status=500, msg="系统错误")

# 获取推荐店铺（基于评分和销量）
@app.route("/api/recommend/shops", methods=["GET"])
@cross_origin()
def recommend_shops():
    try:
        sort_by = request.args.get('sort_by', 'recommend')
        filter_type = request.args.get('filter', 'all')

        user_phone = get_token_phone(request.headers.get('token'))

        # 排序规则
        order_sql_map = {
            'rating': 'avg_rating DESC',
            'sales': 'total_sales DESC',
            'popular': 'order_count DESC',
            'recommend': 'avg_rating DESC, total_sales DESC'
        }
        order_sql = order_sql_map.get(sort_by, 'avg_rating DESC, total_sales DESC')

        # 筛选规则
        having_conditions = []
        where_extra = []

        if filter_type == 'high_rating':
            having_conditions.append('avg_rating >= 4.5')
        elif filter_type == 'popular':
            having_conditions.append('total_sales >= 100')
        elif filter_type == 'new':
            # 新店：30天内
            where_extra.append('DATEDIFF(NOW(), s.created_time) <= 30')

        having_sql = f"HAVING {' AND '.join(having_conditions)}" if having_conditions else ''
        where_extra_sql = f"AND {' AND '.join(where_extra)}" if where_extra else ''

        # ========== 登录用户 ==========
        if user_phone:
            user_pref_query = text('''
                SELECT s.shop_id, COUNT(*) AS order_count
                FROM oorder o
                JOIN shop s ON o.shop_id = s.shop_id
                WHERE o.cons_phone = :phone AND o.checked = 2
                GROUP BY s.shop_id
                ORDER BY order_count DESC
                LIMIT 3
            ''')

            user_prefs = db.session.execute(
                user_pref_query, {'phone': user_phone}
            ).fetchall()

            pref_ids = [row[0] for row in user_prefs] if user_prefs else []

            recommend_query = text(f'''
                SELECT
                    s.shop_id,
                    s.shop_name,
                    s.description,
                    s.image_url,
                    COALESCE(AVG(r.rating), 0) AS avg_rating,
                    COALESCE(COUNT(DISTINCT r.review_id), 0) AS review_count,
                    COALESCE(SUM(d.monthly_sales), 0) AS total_sales,
                    COUNT(DISTINCT o.order_id) AS order_count
                FROM shop s
                LEFT JOIN review r ON s.shop_id = r.shop_id AND r.review_type = 'shop'
                LEFT JOIN dish d ON s.shop_id = d.shop_id
                LEFT JOIN oorder o ON s.shop_id = o.shop_id
                WHERE s.status = 1
                {where_extra_sql}
                {f"AND s.shop_id NOT IN :pref_ids" if pref_ids else ""}
                GROUP BY s.shop_id
                {having_sql}
                ORDER BY {order_sql}
                LIMIT 8
            ''')

            params = {'pref_ids': tuple(pref_ids)} if pref_ids else {}
            recommended = db.session.execute(recommend_query, params).fetchall()

        # ========== 未登录用户 ==========
        else:
            recommend_query = text(f'''
                SELECT
                    s.shop_id,
                    s.shop_name,
                    s.description,
                    s.image_url,
                    COALESCE(AVG(r.rating), 0) AS avg_rating,
                    COALESCE(COUNT(DISTINCT r.review_id), 0) AS review_count,
                    COALESCE(SUM(d.monthly_sales), 0) AS total_sales,
                    COUNT(DISTINCT o.order_id) AS order_count
                FROM shop s
                LEFT JOIN review r ON s.shop_id = r.shop_id AND r.review_type = 'shop'
                LEFT JOIN dish d ON s.shop_id = d.shop_id
                LEFT JOIN oorder o ON s.shop_id = o.shop_id
                WHERE s.status = 1
                {where_extra_sql}
                GROUP BY s.shop_id
                {having_sql}
                ORDER BY {order_sql}
                LIMIT 8
            ''')

            recommended = db.session.execute(recommend_query).fetchall()

        # ========== 封装返回 ==========
        shops = []
        for row in recommended:
            avg_rating = round(float(row[4]), 1)
            shop = {
                'shop_id': row[0],
                'shop_name': row[1],
                'description': row[2],
                'image_url': row[3] or '/images/shop/default-shop.jpg',
                'avg_rating': avg_rating,
                'review_count': row[5],
                'total_sales': row[6],
                'order_count': row[7],
                'recommend_reason': get_recommend_reason(avg_rating, row[6])
            }
            shops.append(shop)

        return jsonify(status=200, data=shops)

    except Exception as e:
        print(f"获取推荐店铺错误: {e}")
        return jsonify(status=500, msg="系统错误")




def get_recommend_reason(avg_rating, total_sales):
    """生成推荐理由"""
    reasons = []

    if avg_rating >= 4.5:
        reasons.append("超高评价")
    elif avg_rating >= 4.0:
        reasons.append("好评如潮")

    if total_sales >= 500:
        reasons.append("月销爆款")
    elif total_sales >= 200:
        reasons.append("人气店铺")

    if not reasons:
        if avg_rating >= 3.5:
            reasons.append("品质保证")
        else:
            reasons.append("新店尝鲜")

    return " · ".join(reasons)


# 获取热门评价
@app.route("/api/recommend/hot-reviews", methods=["GET"])
@cross_origin()
def hot_reviews():
    try:
        # 获取当前用户手机号
        user_phone = get_token_phone(request.headers.get('token', ''))

        # 修改SQL查询，添加关联user_msg表来获取头像
        sql = '''
            SELECT r.review_id, r.shop_id, r.dish_id, r.rating, r.comment, r.created_time,
                   u.username, um.avatar_url, s.shop_name, d.dish_name, r.likes_count
            FROM review r
            JOIN user u ON r.user_phone = u.telephone
            LEFT JOIN user_msg um ON u.id = um.id  -- 添加关联获取头像
            LEFT JOIN shop s ON r.shop_id = s.shop_id
            LEFT JOIN dish d ON r.dish_id = d.dish_id
            WHERE (r.rating = 5 OR LENGTH(r.comment) > 20)
            ORDER BY r.created_time DESC
            LIMIT 10
        '''

        reviews_data = db.session.execute(text(sql)).fetchall()

        reviews = []
        for row in reviews_data:
            # 处理时间
            created_time = row[5]
            time_str = ""

            if created_time:
                try:
                    if isinstance(created_time, datetime):
                        time_str = created_time.strftime('%Y-%m-%d %H:%M')
                    elif isinstance(created_time, str):
                        try:
                            dt = datetime.strptime(created_time, '%Y-%m-%d %H:%M:%S')
                            time_str = dt.strftime('%Y-%m-%d %H:%M')
                        except:
                            time_str = created_time
                    else:
                        time_str = str(created_time)
                except:
                    time_str = str(created_time) if created_time else ""

            # 获取点赞数
            likes_count = row[10] or 0

            # 判断当前用户是否点赞
            liked = False
            if user_phone:
                # 查询该用户是否点赞过该评价
                like_exists = ReviewLike.query.filter_by(
                    review_id=row[0],
                    user_phone=user_phone
                ).first()
                liked = bool(like_exists)

            # 处理头像URL - 确保有正确的路径
            avatar_url = row[7] or '/images/user/default-avatar.jpg'
            if avatar_url and not avatar_url.startswith('/') and not avatar_url.startswith('http'):
                avatar_url = '/' + avatar_url

            review = {
                'review_id': row[0],
                'shop_id': row[1],
                'dish_id': row[2],
                'rating': row[3],
                'comment': row[4] or '',
                'created_time': time_str,
                'username': row[6] or '匿名用户',
                'avatar_url': avatar_url,  # 添加头像字段
                'shop_name': row[8] or '未知店铺',
                'dish_name': row[9],
                'type': '菜品评价' if row[2] else '店铺评价',
                'likes': likes_count,  # 点赞数
                'liked': liked         # 当前用户是否点赞
            }
            reviews.append(review)

        return jsonify(status=200, data=reviews)

    except Exception as e:
        print(f"获取热门评价错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 获取推荐菜品
@app.route("/api/recommend/dishes", methods=["GET"])
@cross_origin()
def recommend_dishes():
    try:
        user_phone = get_token_phone(request.headers.get('token'))

        # 如果用户已登录，基于历史订单推荐
        if user_phone:
            # 获取用户常点的菜品
            user_pref_query = text('''
                SELECT od.dish_id, COUNT(*) as order_count
                FROM order_detail od
                JOIN oorder o ON od.order_id = o.order_id
                WHERE o.cons_phone = :phone
                GROUP BY od.dish_id
                ORDER BY order_count DESC
                LIMIT 5
            ''')

            user_prefs = db.session.execute(user_pref_query, {'phone': user_phone}).fetchall()

            if user_prefs:
                pref_ids = [row[0] for row in user_prefs]
                # 使用参数化查询，注意：在IN子句中需要使用元组
                query = text('''
                    SELECT d.dish_id, d.shop_id, d.dish_name, d.price, d.description, 
                           d.image_url, d.monthly_sales, s.shop_name,
                           COALESCE(AVG(r.rating), 0) as avg_rating,
                           COUNT(DISTINCT r.review_id) as review_count
                    FROM dish d
                    JOIN shop s ON d.shop_id = s.shop_id
                    LEFT JOIN review r ON d.dish_id = r.dish_id AND r.review_type = 'dish'
                    WHERE d.status = 1 AND s.status = 1 AND d.dish_id NOT IN :pref_ids
                    GROUP BY d.dish_id, d.shop_id, d.dish_name, d.price, d.description, 
                             d.image_url, d.monthly_sales, s.shop_name
                    HAVING avg_rating >= 4.0 OR monthly_sales >= 50
                    ORDER BY monthly_sales DESC, avg_rating DESC
                    LIMIT 10
                ''')
                dishes = db.session.execute(query, {'pref_ids': tuple(pref_ids)}).fetchall()
            else:
                query = text('''
                    SELECT d.dish_id, d.shop_id, d.dish_name, d.price, d.description, 
                           d.image_url, d.monthly_sales, s.shop_name,
                           COALESCE(AVG(r.rating), 0) as avg_rating,
                           COUNT(DISTINCT r.review_id) as review_count
                    FROM dish d
                    JOIN shop s ON d.shop_id = s.shop_id
                    LEFT JOIN review r ON d.dish_id = r.dish_id AND r.review_type = 'dish'
                    WHERE d.status = 1 AND s.status = 1
                    GROUP BY d.dish_id, d.shop_id, d.dish_name, d.price, d.description, 
                             d.image_url, d.monthly_sales, s.shop_name
                    ORDER BY monthly_sales DESC, avg_rating DESC
                    LIMIT 12
                ''')
                dishes = db.session.execute(query).fetchall()
        else:
            query = text('''
                SELECT d.dish_id, d.shop_id, d.dish_name, d.price, d.description, 
                       d.image_url, d.monthly_sales, s.shop_name,
                       COALESCE(AVG(r.rating), 0) as avg_rating,
                       COUNT(DISTINCT r.review_id) as review_count
                FROM dish d
                JOIN shop s ON d.shop_id = s.shop_id
                LEFT JOIN review r ON d.dish_id = r.dish_id AND r.review_type = 'dish'
                WHERE d.status = 1 AND s.status = 1
                GROUP BY d.dish_id, d.shop_id, d.dish_name, d.price, d.description, 
                         d.image_url, d.monthly_sales, s.shop_name
                ORDER BY monthly_sales DESC
                LIMIT 12
            ''')
            dishes = db.session.execute(query).fetchall()

        dishes_list = []
        for row in dishes:
            dish = {
                'dish_id': row[0],
                'shop_id': row[1],
                'dish_name': row[2],
                'price': float(row[3]),
                'description': row[4] or '',
                'image_url': row[5] or '/images/dish/default-dish.jpg',
                'monthly_sales': row[6],
                'shop_name': row[7],
                'avg_rating': round(float(row[8]), 1),
                'review_count': row[9],
                'recommend_reason': get_dish_recommend_reason(row[8], row[6])
            }
            dishes_list.append(dish)

        return jsonify(status=200, data=dishes_list)

    except Exception as e:
        print(f"获取推荐菜品错误: {e}")
        return jsonify(status=500, msg="系统错误")


def get_dish_recommend_reason(avg_rating, monthly_sales):
    """生成菜品推荐理由"""
    reasons = []

    if avg_rating >= 4.5:
        reasons.append("超高评价")
    elif avg_rating >= 4.0:
        reasons.append("好评如潮")

    if monthly_sales >= 200:
        reasons.append("爆款菜品")
    elif monthly_sales >= 100:
        reasons.append("人气菜品")

    if not reasons:
        if avg_rating >= 3.5:
            reasons.append("口碑不错")
        else:
            reasons.append("值得一试")

    return " · ".join(reasons)


# 获取待评价订单（优化版）
@app.route("/api/review/pending", methods=["GET"])
@cross_origin()
def pending_reviews():
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        pending_query = text('''
            SELECT
                o.order_id,
                o.shop_id,
                s.shop_name,
                o.create_time,
                GROUP_CONCAT(DISTINCT d.dish_id) AS dish_ids,
                GROUP_CONCAT(DISTINCT d.dish_name) AS dish_names,
                GROUP_CONCAT(DISTINCT d.image_url) AS dish_images
            FROM oorder o
            JOIN order_detail od ON o.order_id = od.order_id
            JOIN dish d ON od.dish_id = d.dish_id
            JOIN shop s ON o.shop_id = s.shop_id
            WHERE o.cons_phone = :phone
              AND o.checked = 2
              AND NOT EXISTS (
                  SELECT 1
                  FROM review r
                  WHERE r.order_id = o.order_id
                    AND r.user_phone = o.cons_phone
                    AND r.review_type = 'shop'
              )
            GROUP BY o.order_id, o.shop_id, s.shop_name, o.create_time
            ORDER BY o.create_time DESC
            LIMIT 10
        ''')

        pending_data = db.session.execute(
            pending_query, {'phone': user_phone}
        ).fetchall()

        orders = []
        for row in pending_data:
            dish_ids = row[4].split(',') if row[4] else []
            dish_names = row[5].split(',') if row[5] else []
            dish_images = row[6].split(',') if row[6] else []

            dishes = []
            for i in range(min(len(dish_ids), len(dish_names))):
                dishes.append({
                    'dish_id': int(dish_ids[i]),
                    'dish_name': dish_names[i].strip(),
                    'image_url': dish_images[i] if i < len(dish_images) else None
                })

            create_time = row[3]
            if create_time is None:
                time_str = ''
            elif isinstance(create_time, datetime):
                time_str = create_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                time_str = str(create_time).strip()

            orders.append({
                'order_id': row[0],
                'shop_id': row[1],
                'shop_name': row[2],
                'create_time': time_str,
                'dishes': dishes
            })

        return jsonify(status=200, data=orders)

    except Exception as e:
        print(f"获取待评价订单错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 评价点赞接口
@app.route("/api/review/<int:review_id>/like", methods=["POST"])
@cross_origin()
def like_review(review_id):
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="请先登录")

        # 检查评价是否存在
        review = Review.query.get(review_id)
        if not review:
            return jsonify(status=404, msg="评价不存在")

        # 检查是否已点赞
        existing_like = ReviewLike.query.filter_by(
            review_id=review_id,
            user_phone=user_phone
        ).first()

        if existing_like:
            # 取消点赞
            db.session.delete(existing_like)
            review.likes_count = max(0, review.likes_count - 1)
            db.session.commit()

            # 更新Redis缓存
            update_redis_cache(review_id, review.likes_count)

            return jsonify(
                status=200,
                msg="取消点赞成功",
                likes=review.likes_count,
                liked=False
            )
        else:
            # 添加点赞
            new_like = ReviewLike(
                review_id=review_id,
                user_phone=user_phone
            )
            db.session.add(new_like)
            review.likes_count = (review.likes_count or 0) + 1
            db.session.commit()

            # 更新Redis缓存
            update_redis_cache(review_id, review.likes_count)

            return jsonify(
                status=200,
                msg="点赞成功",
                likes=review.likes_count,
                liked=True
            )

    except Exception as e:
        print(f"点赞评价错误: {e}")
        db.session.rollback()
        return jsonify(status=500, msg="系统错误")


def update_redis_cache(review_id, likes_count):
    """更新Redis缓存"""
    try:
        if redis_store is not None:
            redis_store.set(f"review_likes:{review_id}", likes_count)
        else:
            # 更新内存缓存
            if 'review_likes' not in redis_cache:
                redis_cache['review_likes'] = {}
            redis_cache['review_likes'][review_id] = likes_count
    except Exception as e:
        print(f"更新Redis缓存错误: {e}")


# 获取评价点赞数
@app.route("/api/review/<int:review_id>/likes", methods=["GET"])
@cross_origin()
def get_review_likes(review_id):
    try:
        # 优先从缓存获取
        likes = get_likes_from_cache(review_id)
        if likes is not None:
            return jsonify(status=200, data={"likes": likes})

        # 缓存中没有，从数据库获取
        review = Review.query.get(review_id)
        likes = review.likes_count if review else 0

        # 更新缓存
        update_redis_cache(review_id, likes)

        return jsonify(status=200, data={"likes": likes})

    except Exception as e:
        print(f"获取评价点赞数错误: {e}")
        return jsonify(status=200, data={"likes": 0})


def get_likes_from_cache(review_id):
    """从缓存获取点赞数"""
    try:
        if redis_store is not None:
            likes = redis_store.get(f"review_likes:{review_id}")
            return int(likes) if likes else None
        else:
            return redis_cache.get('review_likes', {}).get(review_id)
    except:
        return None


# 获取用户是否已点赞
@app.route("/api/review/<int:review_id>/like/status", methods=["GET"])
@cross_origin()
def get_like_status(review_id):
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=200, data={"liked": False})

        # 检查是否已点赞
        existing_like = ReviewLike.query.filter_by(
            review_id=review_id,
            user_phone=user_phone
        ).first()

        return jsonify(status=200, data={"liked": bool(existing_like)})

    except Exception as e:
        print(f"获取点赞状态错误: {e}")
        return jsonify(status=200, data={"liked": False})



# 获取评价列表（带点赞数）
@app.route("/api/reviews", methods=["GET"])
@cross_origin()
def get_reviews():
    try:
        shop_id = request.args.get('shop_id')
        dish_id = request.args.get('dish_id')
        user_phone = get_token_phone(request.headers.get('token', ''))
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        # 构建基础查询条件
        where_clause = "WHERE 1=1"
        params = {}

        if shop_id:
            where_clause += " AND r.shop_id = :shop_id"
            params['shop_id'] = shop_id
        if dish_id:
            where_clause += " AND r.dish_id = :dish_id"
            params['dish_id'] = dish_id

        # 使用原生SQL查询，包含用户头像
        query = text(f'''
            SELECT r.review_id, r.order_id, r.shop_id, r.dish_id, 
                   r.user_phone, r.rating, r.comment, r.review_type, r.created_time,
                   u.username, um.avatar_url,
                   COUNT(rl.review_id) as likes_count
            FROM review r
            LEFT JOIN user u ON r.user_phone = u.telephone
            LEFT JOIN user_msg um ON u.id = um.id
            LEFT JOIN review_like rl ON r.review_id = rl.review_id
            {where_clause}
            GROUP BY r.review_id, r.order_id, r.shop_id, r.dish_id, 
                     r.user_phone, r.rating, r.comment, r.review_type, r.created_time,
                     u.username, um.avatar_url
            ORDER BY r.created_time DESC
            LIMIT :limit OFFSET :offset
        ''')

        # 计算分页
        offset = (page - 1) * page_size
        params['limit'] = page_size
        params['offset'] = offset

        # 执行查询
        reviews_data = db.session.execute(query, params).fetchall()

        # 获取总记录数
        count_query = text(f'''
            SELECT COUNT(*) FROM review r {where_clause}
        ''')
        total_count = db.session.execute(count_query, params).scalar() or 0

        result = []
        for row in reviews_data:
            # 处理头像URL
            avatar_url = row[10] or '/images/user/default-avatar.jpg'
            if avatar_url and not avatar_url.startswith('/') and not avatar_url.startswith('http'):
                avatar_url = '/' + avatar_url

            # 检查当前用户是否已点赞
            liked = False
            if user_phone:
                like_check_query = text('''
                    SELECT 1 FROM review_like 
                    WHERE review_id = :review_id AND user_phone = :user_phone
                ''')
                like_exists = db.session.execute(like_check_query, {
                    'review_id': row[0],
                    'user_phone': user_phone
                }).fetchone()
                liked = bool(like_exists)

            result.append({
                'review_id': row[0],
                'order_id': row[1],
                'shop_id': row[2],
                'dish_id': row[3],
                'user_phone': row[4],
                'rating': row[5],
                'comment': row[6],
                'review_type': row[7],
                'created_time': row[8].strftime('%Y-%m-%d %H:%M:%S') if row[8] else None,
                'username': row[9] or f"用户{row[4][-4:]}" if row[4] else '匿名用户',
                'avatar_url': avatar_url,
                'likes': row[11] or 0,
                'liked': liked
            })

        return jsonify(status=200, data={
            'reviews': result,
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })

    except Exception as e:
        print(f"获取评价列表错误: {e}")
        return jsonify(status=500, msg="系统错误")

# 初始化缓存（应用启动时运行）
def init_review_likes_cache():
    """将数据库中的点赞数据加载到缓存"""
    try:
        print("正在初始化点赞缓存...")

        # 从数据库获取所有评价的点赞数
        from sqlalchemy import func
        result = db.session.query(
            Review.review_id,
            Review.likes_count
        ).all()

        for review_id, likes_count in result:
            update_redis_cache(review_id, likes_count or 0)

        print(f"点赞缓存初始化完成，共加载 {len(result)} 条数据")

    except Exception as e:
        print(f"初始化点赞缓存错误: {e}")



# 还未配送的订单
@app.route("/api/user/unsend", methods=["POST", "GET", "DELETE"])
@cross_origin()
def user_unsend():
    if request.method == 'GET':
        phone = get_token_phone(request.headers.get('token'))
        if not phone:
            return jsonify(status=401, msg="用户未登录")

        print(f"获取用户 {phone} 的未发送订单")

        # 使用参数化查询，修复 SQL 注入风险
        data = db.session.execute(text('''
            SELECT o.order_id, o.shop_id, o.shop_name, o.order_money, o.order_way, 
                   o.cons_name, o.cons_addre, o.checked, o.create_time,
                   s.image_url as shop_image
            FROM oorder o 
            LEFT JOIN shop s ON o.shop_id = s.shop_id
            WHERE o.checked=0 AND o.cons_phone=:phone
            ORDER BY o.create_time DESC
        '''), {'phone': phone}).fetchall()

        Data = []
        for row in data:
            # 获取订单详情
            order_details = db.session.execute(text('''
                SELECT od.dish_id, od.dish_name, od.price, od.quantity, od.subtotal,
                       d.image_url as dish_image
                FROM order_detail od
                LEFT JOIN dish d ON od.dish_id = d.dish_id
                WHERE od.order_id = :order_id
            '''), {'order_id': row[0]}).fetchall()

            details_list = []
            for detail in order_details:
                details_list.append({
                    'dish_id': detail[0],
                    'dish_name': detail[1],
                    'price': float(detail[2]),
                    'quantity': detail[3],
                    'subtotal': float(detail[4]),
                    'dish_image': detail[5]
                })

            dic = {
                'order_id': row[0],
                'shop_id': row[1],
                'shop_name': row[2],
                'order_money': float(row[3]),
                'order_way': row[4],
                'cons_name': row[5],
                'cons_addre': row[6],
                'checked': row[7],
                'create_time': row[8],
                'shop_image': row[9],
                'orderDetails': details_list  # 添加订单详情
            }
            Data.append(dic)

        return jsonify(status=200, tabledata=Data)

    if request.method == 'POST':
        try:
            rq = request.json
            order_id = rq.get("order_id")
            cons_name = rq.get("cons_name")
            cons_addre = rq.get("cons_addre")

            if not all([order_id, cons_name, cons_addre]):
                return jsonify(status=400, msg="参数不完整")

            print(f"修改订单 {order_id} 的收货信息")

            # 使用参数化查询
            db.session.execute(
                text('UPDATE oorder SET cons_name=:cons_name, cons_addre=:cons_addre WHERE order_id=:order_id'),
                {'cons_name': cons_name, 'cons_addre': cons_addre, 'order_id': order_id}
            )
            db.session.commit()
            return jsonify(status=200, msg="修改成功")

        except Exception as e:
            db.session.rollback()
            print(f"修改订单失败: {e}")
            return jsonify(status=500, msg="修改失败")

    if request.method == 'DELETE':
        try:
            order_id = request.json.get("delete_id")
            if not order_id:
                return jsonify(status=400, msg="缺少订单ID")

            print(f"删除订单 {order_id}")

            # 先删除订单明细，再删除订单（因为有外键约束）
            db.session.execute(text('DELETE FROM order_detail WHERE order_id=:order_id'),
                               {'order_id': order_id})
            db.session.execute(text('DELETE FROM oorder WHERE order_id=:order_id'),
                               {'order_id': order_id})
            db.session.commit()
            return jsonify(status=200, msg="删除成功")

        except Exception as e:
            db.session.rollback()
            print(f"删除订单失败: {e}")
            return jsonify(status=500, msg="删除失败")


# 正在配送的订单
@app.route("/api/user/sending", methods=["POST", "GET", "DELETE"])
@cross_origin()
def user_sending():
    if request.method == 'GET':
        try:
            phone = get_token_phone(request.headers.get('token'))
            if not phone:
                return jsonify(status=401, msg="用户未登录")

            # 使用参数化查询获取已发货订单（checked=1）
            data = db.session.execute(text('''
                SELECT o.order_id, o.shop_id, o.shop_name, o.order_money, o.order_way, 
                       o.cons_phone, o.cons_name, o.cons_addre, o.checked, o.create_time,
                       s.image_url as shop_image,
                       d.disp_id, d.deliver_time, dp.dispatcher_name, dp.dispatcher_phone
                FROM oorder o 
                LEFT JOIN shop s ON o.shop_id = s.shop_id
                LEFT JOIN delivery d ON o.order_id = d.order_id
                LEFT JOIN dispatcher dp ON d.disp_id = dp.dispatcher_id
                WHERE o.checked=1 AND o.cons_phone=:phone
                ORDER BY o.create_time DESC
            '''), {'phone': phone}).fetchall()

            Data = []
            for row in data:
                # 获取订单详情
                order_details = db.session.execute(text('''
                    SELECT od.dish_id, od.dish_name, od.price, od.quantity, od.subtotal,
                           d.image_url as dish_image
                    FROM order_detail od
                    LEFT JOIN dish d ON od.dish_id = d.dish_id
                    WHERE od.order_id = :order_id
                '''), {'order_id': row[0]}).fetchall()

                details_list = []
                for detail in order_details:
                    details_list.append({
                        'dish_id': detail[0],
                        'dish_name': detail[1],
                        'price': float(detail[2]),
                        'quantity': detail[3],
                        'subtotal': float(detail[4]),
                        'dish_image': detail[5]
                    })

                dic = {
                    'order_id': row[0],
                    'shop_id': row[1],
                    'shop_name': row[2],
                    'order_money': float(row[3]),
                    'order_way': row[4],
                    'cons_phone': row[5],
                    'cons_name': row[6],
                    'cons_addre': row[7],
                    'checked': row[8],
                    'create_time': row[9],
                    'shop_image': row[10],
                    'disp_id': row[11],
                    'deliver_time': row[12],
                    'disp_name': row[13],  # 配送员姓名
                    'disp_phone': row[14],  # 配送员电话
                    'orderDetails': details_list
                }
                Data.append(dic)

            return jsonify(status=200, tabledata=Data)

        except Exception as e:
            print(f"获取已发货订单失败: {e}")
            return jsonify(status=500, msg="获取数据失败")


# 确认收货接口
@app.route("/api/user/confirm-receipt", methods=["POST"])
@cross_origin()
def confirm_receipt():
    try:
        data = request.json
        order_id = data.get('order_id')

        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        print(f"用户 {user_phone} 确认收货，订单ID: {order_id}")

        # 验证订单属于当前用户且状态为配送中 (checked=1)
        order_check = db.session.execute(
            text('SELECT order_id, checked FROM oorder WHERE order_id = :order_id AND cons_phone = :phone'),
            {'order_id': order_id, 'phone': user_phone}
        ).fetchone()

        if not order_check:
            return jsonify(status=404, msg="订单不存在")

        if order_check[1] != 1:
            return jsonify(status=400, msg="订单状态异常，无法确认收货")

        # 更新订单状态为已完成 (checked=2)
        db.session.execute(
            text('UPDATE oorder SET checked = 2 WHERE order_id = :order_id'),
            {'order_id': order_id}
        )

        # 更新配送记录状态为已完成
        db.session.execute(
            text('UPDATE delivery SET ended = 1 WHERE order_id = :order_id'),
            {'order_id': order_id}
        )

        db.session.commit()
        return jsonify(status=200, msg="确认收货成功")

    except Exception as e:
        db.session.rollback()
        print(f"确认收货失败: {e}")
        return jsonify(status=500, msg="确认收货失败")


#获取已完成的订单
@app.route("/api/user/sended", methods=["POST", "GET", "DELETE"])
@cross_origin()
def user_sended():
    if request.method == 'GET':
        try:
            phone = get_token_phone(request.headers.get('token'))
            if not phone:
                return jsonify(status=401, msg="用户未登录")

            # 使用参数化查询获取已完成订单（checked=2）
            data = db.session.execute(text('''
                SELECT o.order_id, o.shop_id, o.shop_name, o.order_money, o.order_way, 
                       o.cons_phone, o.cons_name, o.cons_addre, o.checked, o.create_time,
                       s.image_url as shop_image,
                       d.disp_id, d.deliver_time, dp.dispatcher_name, dp.dispatcher_phone
                FROM oorder o 
                LEFT JOIN shop s ON o.shop_id = s.shop_id
                LEFT JOIN delivery d ON o.order_id = d.order_id
                LEFT JOIN dispatcher dp ON d.disp_id = dp.dispatcher_id
                WHERE o.checked=2 AND o.cons_phone=:phone
                ORDER BY o.create_time DESC
            '''), {'phone': phone}).fetchall()

            Data = []
            for row in data:
                # 获取订单详情
                order_details = db.session.execute(text('''
                    SELECT od.dish_id, od.dish_name, od.price, od.quantity, od.subtotal,
                           d.image_url as dish_image
                    FROM order_detail od
                    LEFT JOIN dish d ON od.dish_id = d.dish_id
                    WHERE od.order_id = :order_id
                '''), {'order_id': row[0]}).fetchall()

                details_list = []
                for detail in order_details:
                    details_list.append({
                        'dish_id': detail[0],
                        'dish_name': detail[1],
                        'price': float(detail[2]),
                        'quantity': detail[3],
                        'subtotal': float(detail[4]),
                        'dish_image': detail[5]
                    })

                dic = {
                    'order_id': row[0],
                    'shop_id': row[1],
                    'shop_name': row[2],
                    'order_money': float(row[3]),
                    'order_way': row[4],
                    'cons_phone': row[5],
                    'cons_name': row[6],
                    'cons_addre': row[7],
                    'checked': row[8],
                    'create_time': row[9],
                    'shop_image': row[10],
                    'disp_id': row[11],
                    'deliver_time': row[12],
                    'disp_name': row[13],  # 配送员姓名
                    'disp_phone': row[14],  # 配送员电话
                    'orderDetails': details_list
                }
                Data.append(dic)

            return jsonify(status=200, tabledata=Data)

        except Exception as e:
            print(f"获取已完成订单失败: {e}")
            return jsonify(status=500, msg="获取数据失败")


# 在 app.py 中添加这些辅助函数（如果还没有的话）
def get_user_avatar_path():
    """获取用户头像存储路径"""
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_public_dir = os.path.join(
        backend_dir,
        '..',
        '前端代码',
        'sjk',
        'public',
        'images',
        'user'
    )
    return os.path.abspath(frontend_public_dir)



# 用户头像的函数
def save_user_avatar(image_file, phone):
    """保存用户头像"""
    try:
        # 检查文件格式
        if not allowed_file(image_file.filename):
            return False, None, "不支持的文件格式，请上传图片文件"

        # 生成文件名
        ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else 'jpg'
        unique_id = str(uuid.uuid4())[:8]
        filename = f"avatar_{phone}_{unique_id}.{ext}"

        # 保存路径
        upload_dir = get_user_avatar_path()
        os.makedirs(upload_dir, exist_ok=True)

        # 保存文件
        file_path = os.path.join(upload_dir, filename)
        image_file.save(file_path)

        # 生成前端访问URL
        avatar_url = f"/images/user/{filename}"

        print(f"用户头像已保存到: {file_path}")
        print(f"前端访问URL: {avatar_url}")

        return True, avatar_url, None

    except Exception as e:
        print(f"保存用户头像错误: {e}")
        return False, None, f"保存头像失败: {str(e)}"


# 删除用户头像
def delete_user_avatar(avatar_url):
    """删除用户旧头像"""
    try:
        # 检查是否是默认头像，默认头像不删除
        default_avatar = "/images/user/default-avatar.jpg"
        if avatar_url and avatar_url != default_avatar:
            filename = os.path.basename(avatar_url)
            upload_dir = get_user_avatar_path()
            old_avatar_path = os.path.join(upload_dir, filename)

            if os.path.exists(old_avatar_path):
                os.remove(old_avatar_path)
                print(f"已删除旧头像: {old_avatar_path}")
                return True
    except Exception as e:
        print(f"删除用户旧头像失败: {e}")
    return False


# 上传头像接口 - 使用简单的版本
@app.route("/api/user/upload-avatar", methods=["POST"])
@cross_origin()
def upload_user_avatar():
    """上传用户头像（简化版）"""
    try:
        # 获取用户信息
        token = request.headers.get('token')
        phone = get_token_phone(token)
        if not phone:
            return jsonify(status=1001, msg="请重新登录")

        # 检查是否有文件上传
        if 'avatar' not in request.files:
            return jsonify(status=400, msg="请选择头像文件")

        avatar_file = request.files['avatar']
        if avatar_file.filename == '':
            return jsonify(status=400, msg="请选择有效的头像文件")

        # 检查文件类型
        if not allowed_file(avatar_file.filename):
            return jsonify(status=400, msg="只支持jpg, jpeg, png, gif, bmp, webp格式的图片")

        # 检查文件大小
        if len(avatar_file.read()) > 2 * 1024 * 1024:  # 2MB
            avatar_file.seek(0)  # 重置文件指针
            return jsonify(status=400, msg="图片大小不能超过2MB")
        avatar_file.seek(0)  # 重置文件指针

        # 获取用户当前头像信息
        user_info = db.session.execute(
            text("SELECT avatar_url FROM user_msg WHERE phone = :phone"),
            {"phone": phone}
        ).fetchone()

        old_avatar_url = user_info.avatar_url if user_info else None

        # 保存新头像
        success, avatar_url, error_msg = save_user_avatar(avatar_file, phone)
        if not success:
            return jsonify(status=400, msg=error_msg)

        # 更新数据库
        result = db.session.execute(
            text("UPDATE user_msg SET avatar_url = :avatar_url WHERE phone = :phone"),
            {"avatar_url": avatar_url, "phone": phone}
        )

        # 如果用户没有user_msg记录，创建一条
        if result.rowcount == 0:
            # 获取用户ID
            user_id_result = db.session.execute(
                text("SELECT id FROM user WHERE telephone = :phone"),
                {"phone": phone}
            ).fetchone()

            if user_id_result:
                user_id = user_id_result[0]
                # 插入新记录
                db.session.execute(
                    text("""
                        INSERT INTO user_msg 
                        (id, phone, avatar_url, user_name, real_name) 
                        VALUES (:id, :phone, :avatar_url, :username, :username)
                    """),
                    {
                        "id": user_id,
                        "phone": phone,
                        "avatar_url": avatar_url,
                        "username": phone  # 临时使用手机号作为用户名
                    }
                )

        # 删除旧头像（如果不是默认头像）
        if old_avatar_url and old_avatar_url != '/images/user/default-avatar.jpg':
            delete_user_avatar(old_avatar_url)

        db.session.commit()

        return jsonify({
            "status": 200,
            "msg": "头像上传成功",
            "avatar_url": avatar_url
        })

    except Exception as e:
        db.session.rollback()
        print(f"上传用户头像错误: {e}")
        return jsonify(status=500, msg="头像上传失败")


# 删除头像接口
@app.route("/api/user/remove-avatar", methods=["POST"])
@cross_origin()
def remove_user_avatar():
    """删除用户头像（恢复默认）"""
    try:
        token = request.headers.get('token')
        phone = get_token_phone(token)
        if not phone:
            return jsonify(status=1001, msg="请重新登录")

        # 获取用户当前头像
        user_info = db.session.execute(
            text("SELECT avatar_url FROM user_msg WHERE phone = :phone"),
            {"phone": phone}
        ).fetchone()

        if user_info and user_info.avatar_url:
            # 删除旧头像文件
            if user_info.avatar_url != '/images/user/default-avatar.jpg':
                delete_user_avatar(user_info.avatar_url)

        # 更新为默认头像 - 这里使用.jpg，如果您用的是.png，请修改
        default_avatar = "/images/user/default-avatar.jpg"
        db.session.execute(
            text("UPDATE user_msg SET avatar_url = :avatar_url WHERE phone = :phone"),
            {"avatar_url": default_avatar, "phone": phone}
        )

        db.session.commit()

        return jsonify({
            "status": 200,
            "msg": "头像已恢复默认",
            "avatar_url": default_avatar
        })

    except Exception as e:
        db.session.rollback()
        print(f"删除用户头像错误: {e}")
        return jsonify(status=500, msg="头像删除失败")


# usermsg接口
@app.route("/api/user/usermsg", methods=["GET", "POST"])
@cross_origin()
def usermsg():
    """
    GET  : 获取当前登录用户的扩展信息（包含头像）
    POST : 保存用户修改后的扩展信息（包含头像URL）
    """
    token = request.headers.get('token')
    phone = get_token_phone(token)
    if not phone:
        return jsonify(status=1001, msg="token 无效或已过期，请重新登录")

    if request.method == 'GET':
        try:
            sql = text("""
                SELECT real_name, sex, age, mail, phone, user_name, avatar_url
                FROM user_msg
                WHERE phone = :phone
            """)
            result = db.session.execute(sql, {"phone": phone}).fetchone()

            if not result:
                # 如果没有记录，创建默认数据
                default_avatar = "/images/user/default-avatar.jpg"  # 或 .png
                data = {
                    "real_name": "",
                    "sex": "",
                    "age": "",
                    "mail": "",
                    "phone": phone,
                    "user_name": "",
                    "avatar_url": default_avatar
                }
                return jsonify(status=200, data=data)

            data = {
                "real_name": result.real_name or "",
                "sex": result.sex or "",
                "age": result.age if result.age is not None else "",
                "mail": result.mail or "",
                "phone": result.phone or phone,
                "user_name": result.user_name or "",
                "avatar_url": result.avatar_url or "/images/user/default-avatar.jpg"
            }
            return jsonify(status=200, data=data)

        except Exception as e:
            print(f"[GET usermsg] 异常: {e}")
            return jsonify(status=500, msg="服务器内部错误")

    elif request.method == 'POST':
        try:
            json_data = request.get_json()
            if not json_data:
                return jsonify(status=400, msg="请求体不能为空")

            real_name = json_data.get("real_name", "").strip()
            sex = json_data.get("sex", "").strip()
            age = json_data.get("age")
            mail = json_data.get("mail", "").strip()
            user_name = json_data.get("user_name", "").strip()
            avatar_url = json_data.get("avatar_url", "").strip()

            # 必填校验
            if not real_name:
                real_name = user_name  # 如果没有真实姓名，使用用户名
            if not user_name:
                user_name = phone  # 如果没有用户名，使用手机号

            # age 处理
            if age in ["", None, "null"]:
                age = None
            else:
                try:
                    age = int(age)
                    if age < 1 or age > 150:
                        return jsonify(status=1005, msg="年龄必须在 1-150 之间")
                except (ValueError, TypeError):
                    return jsonify(status=1005, msg="年龄格式不正确")

            # 设置默认头像URL
            if not avatar_url:
                avatar_url = "/images/user/default-avatar.jpg"

            # 检查用户信息是否存在
            check_sql = text("SELECT phone FROM user_msg WHERE phone = :phone")
            exists = db.session.execute(check_sql, {"phone": phone}).fetchone()

            if exists:
                # 更新现有记录
                update_sql = text("""
                    UPDATE user_msg
                    SET real_name = :real_name,
                        sex = :sex,
                        age = :age,
                        mail = :mail,
                        user_name = :user_name,
                        avatar_url = :avatar_url
                    WHERE phone = :phone
                """)
            else:
                # 获取用户ID
                user_id_result = db.session.execute(
                    text("SELECT id FROM user WHERE telephone = :phone"),
                    {"phone": phone}
                ).fetchone()

                if not user_id_result:
                    return jsonify(status=404, msg="用户不存在")

                user_id = user_id_result[0]
                # 创建新记录
                update_sql = text("""
                    INSERT INTO user_msg 
                    (id, real_name, sex, age, mail, phone, user_name, avatar_url)
                    VALUES (:id, :real_name, :sex, :age, :mail, :phone, :user_name, :avatar_url)
                """)

            params = {
                "real_name": real_name,
                "sex": sex,
                "age": age,
                "mail": mail,
                "user_name": user_name,
                "avatar_url": avatar_url,
                "phone": phone
            }

            if not exists:
                params["id"] = user_id

            result = db.session.execute(update_sql, params)

            db.session.commit()

            if result.rowcount == 0 and exists:
                return jsonify(status=1004, msg="信息未发生变更")

            return jsonify(status=200, msg="个人信息保存成功")

        except Exception as e:
            db.session.rollback()
            print(f"[POST usermsg] 异常: {e}")
            return jsonify(status=500, msg="服务器内部错误")


# 更改用户密码
@app.route("/api/user/pwd_chg", methods=["POST"])
@cross_origin()
def user_pwd_chg():
    if request.method == 'POST':
        try:
            pwd = request.json.get('new_pwd')
            old_pwd = request.json.get('old_pwd')

            if not pwd or not old_pwd:
                return jsonify(status=1001, msg="密码不能为空")

            phone = get_token_phone(request.headers.get('token'))
            if not phone:
                return jsonify(status=1002, msg="token无效")

            # 使用参数化查询验证旧密码
            sql = text('SELECT * FROM user WHERE telephone = :phone AND password = :old_pwd')
            data = db.session.execute(sql, {'phone': phone, 'old_pwd': old_pwd}).fetchall()

            if not data:
                return jsonify(status=1000, msg="原始密码错误")
            else:
                # 使用参数化查询更新密码
                update_sql = text('UPDATE user SET password = :new_pwd WHERE telephone = :phone')
                db.session.execute(update_sql, {'new_pwd': pwd, 'phone': phone})
                db.session.commit()
                return jsonify(status=200, msg="修改成功")

        except Exception as e:
            db.session.rollback()
            print(f"修改密码错误: {e}")
            return jsonify(status=500, msg="系统错误")


# 获取店铺列表
@app.route("/api/shops", methods=["GET"])
@cross_origin()
def get_shops():
    try:
        data = db.session.execute(text('''
            SELECT shop_id, shop_name, description, image_url, status 
            FROM shop 
            WHERE status = 1
            ORDER BY shop_id
        ''')).fetchall()

        shops = []
        for row in data:
            shop = {
                'shop_id': row[0],
                'shop_name': row[1],
                'description': row[2],
                'image_url': row[3],
                'status': row[4]
            }
            shops.append(shop)
        return jsonify(status=200, data=shops)
    except Exception as e:
        print(f"获取店铺列表错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 更新购物车数量接口
@app.route("/api/cart/update", methods=["POST"])
@cross_origin()
def update_cart_quantity():
    try:
        data = request.json
        cart_id = data.get('cart_id')
        quantity = data.get('quantity')

        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=1001, msg="用户未登录")

        # 验证购物车项属于当前用户
        cart_item = db.session.execute(text('''
            SELECT cart_id FROM cart 
            WHERE cart_id = :cart_id AND user_phone = :user_phone
        '''), {'cart_id': cart_id, 'user_phone': user_phone}).fetchone()

        if not cart_item:
            return jsonify(status=1002, msg="购物车项不存在")

        # 更新数量
        db.session.execute(text('''
            UPDATE cart SET quantity = :quantity 
            WHERE cart_id = :cart_id
        '''), {'quantity': quantity, 'cart_id': cart_id})

        db.session.commit()
        return jsonify(status=200, msg="更新成功")

    except Exception as e:
        db.session.rollback()
        print(f"更新购物车数量错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 添加到购物车
@app.route("/api/cart/add", methods=["POST"])
@cross_origin()
def add_to_cart():
    try:
        data = request.json
        dish_id = data.get('dish_id')
        quantity = data.get('quantity', 1)

        # 获取用户电话
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=1001, msg="用户未登录")

        # 获取菜品信息
        dish = db.session.execute(text('''
            SELECT dish_id, shop_id, dish_name, price 
            FROM dish 
            WHERE dish_id = :dish_id AND status = 1
        '''), {'dish_id': dish_id}).fetchone()

        if not dish:
            return jsonify(status=1002, msg="菜品不存在")

        # 检查购物车中是否已有该菜品
        existing_item = db.session.execute(text('''
            SELECT cart_id, quantity 
            FROM cart 
            WHERE user_phone = :user_phone AND dish_id = :dish_id
        '''), {'user_phone': user_phone, 'dish_id': dish_id}).fetchone()

        if existing_item:
            # 更新数量
            new_quantity = existing_item[1] + quantity
            db.session.execute(text('''
                UPDATE cart SET quantity = :quantity 
                WHERE cart_id = :cart_id
            '''), {'quantity': new_quantity, 'cart_id': existing_item[0]})
        else:
            # 新增购物车项
            db.session.execute(text('''
                INSERT INTO cart (user_phone, shop_id, dish_id, quantity) 
                VALUES (:user_phone, :shop_id, :dish_id, :quantity)
            '''), {
                'user_phone': user_phone,
                'shop_id': dish[1],
                'dish_id': dish_id,
                'quantity': quantity
            })

        db.session.commit()
        return jsonify(status=200, msg="添加成功")

    except Exception as e:
        db.session.rollback()
        print(f"添加到购物车错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 获取购物车
@app.route("/api/cart", methods=["GET"])
@cross_origin()
def get_cart():
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=1001, msg="用户未登录")

        data = db.session.execute(text('''
            SELECT c.cart_id, c.dish_id, c.quantity, d.dish_name, d.price, d.image_url, 
                   s.shop_id, s.shop_name
            FROM cart c
            JOIN dish d ON c.dish_id = d.dish_id
            JOIN shop s ON c.shop_id = s.shop_id
            WHERE c.user_phone = :user_phone
            ORDER BY c.created_time DESC
        '''), {'user_phone': user_phone}).fetchall()

        cart_items = []
        total_amount = 0

        for row in data:
            subtotal = float(row[4]) * row[2]
            total_amount += subtotal

            item = {
                'cart_id': row[0],
                'dish_id': row[1],
                'quantity': row[2],
                'dish_name': row[3],
                'price': float(row[4]),
                'image_url': row[5],
                'shop_id': row[6],
                'shop_name': row[7],
                'subtotal': subtotal
            }
            cart_items.append(item)

        return jsonify(status=200, data={
            'items': cart_items,
            'total_amount': total_amount
        })

    except Exception as e:
        print(f"获取购物车错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 从购物车删除
@app.route("/api/cart/remove", methods=["POST"])
@cross_origin()
def remove_from_cart():
    try:
        cart_id = request.json.get('cart_id')
        user_phone = get_token_phone(request.headers.get('token'))

        if not user_phone:
            return jsonify(status=1001, msg="用户未登录")

        db.session.execute(text('''
            DELETE FROM cart 
            WHERE cart_id = :cart_id AND user_phone = :user_phone
        '''), {'cart_id': cart_id, 'user_phone': user_phone})

        db.session.commit()
        return jsonify(status=200, msg="删除成功")

    except Exception as e:
        db.session.rollback()
        print(f"删除购物车项错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 清空购物车
@app.route("/api/cart/clear", methods=["POST"])
@cross_origin()
def clear_cart():
    try:
        user_phone = get_token_phone(request.headers.get('token'))

        if not user_phone:
            return jsonify(status=1001, msg="用户未登录")

        db.session.execute(text('''
            DELETE FROM cart 
            WHERE user_phone = :user_phone
        '''), {'user_phone': user_phone})

        db.session.commit()
        return jsonify(status=200, msg="清空成功")

    except Exception as e:
        db.session.rollback()
        print(f"清空购物车错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 新的下单接口（基于购物车，支持地址管理）
# 新的下单接口（基于购物车，支持地址管理）
@app.route("/api/order/cart", methods=["POST"])
@cross_origin()
def create_order_from_cart():
    try:
        data = request.json
        order_way = data.get('order_way')
        cons_name = data.get('cons_name')
        cons_addre = data.get('cons_addre')
        cons_phone = data.get('cons_phone')
        remark = data.get('remark', '')
        address_id = data.get('address_id')  # 新增：地址ID

        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=1001, msg="用户未登录")

        # 方式一：如果提供了地址ID，从地址表获取地址信息
        if address_id:
            # 验证地址是否属于当前用户
            address_query = text("""
                SELECT cons_name, cons_phone, province, city, district, street 
                FROM user_address 
                WHERE address_id = :address_id 
                AND user_phone = :user_phone 
                AND status = 1
            """)

            address_data = db.session.execute(address_query, {
                'address_id': address_id,
                'user_phone': user_phone
            }).fetchone()

            if not address_data:
                return jsonify(status=1004, msg="地址不存在或无权使用")

            # 使用地址表中的信息
            cons_name = address_data[0]
            cons_phone = address_data[1]
            # 组合完整地址
            province = address_data[2]
            city = address_data[3]
            district = address_data[4]
            street = address_data[5]
            full_address = f"{province}{city}{district}{street}"

            # 更新使用地址表中的信息
            cons_addre = full_address

            print(f"使用地址ID={address_id}, 收货人={cons_name}, 电话={cons_phone}, 地址={full_address}")

        # 方式二：如果没有地址ID，使用直接传递的地址信息（兼容旧版）
        else:
            # 如果没有传递收货电话，使用用户注册电话
            if not cons_phone:
                cons_phone = user_phone
                print(f"使用用户注册电话作为收货电话: {cons_phone}")

            # 验证必填字段
            if not all([order_way, cons_name, cons_addre]):
                return jsonify(status=1001, msg="订单信息不完整")

            # 对于旧版订单，address_id为NULL
            address_id = None

        # 获取购物车数据
        cart_data = db.session.execute(text('''
            SELECT c.dish_id, c.quantity, d.dish_name, d.price, s.shop_id, s.shop_name
            FROM cart c
            JOIN dish d ON c.dish_id = d.dish_id
            JOIN shop s ON c.shop_id = s.shop_id
            WHERE c.user_phone = :user_phone
        '''), {'user_phone': user_phone}).fetchall()

        if not cart_data:
            return jsonify(status=1002, msg="购物车为空")

        # 检查所有菜品是否来自同一店铺
        shop_ids = set(row[4] for row in cart_data)
        if len(shop_ids) > 1:
            return jsonify(status=1003, msg="请选择同一店铺的菜品下单")

        shop_id = list(shop_ids)[0]
        shop_name = cart_data[0][5]

        # 计算总金额
        total_amount = sum(float(row[3]) * row[1] for row in cart_data)

        # 生成订单
        create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(f"创建订单: shop_id={shop_id}, 收货人={cons_name}, 电话={cons_phone}, 地址ID={address_id}")

        # 插入订单（包含shop_id、remark和address_id）
        sql = text('''
            INSERT INTO oorder 
            (shop_id, shop_name, order_money, order_way, cons_phone, cons_name, cons_addre, address_id, create_time, remark) 
            VALUES (:shop_id, :shop_name, :order_money, :order_way, :cons_phone, :cons_name, :cons_addre, :address_id, :create_time, :remark)
        ''')
        result = db.session.execute(sql, {
            'shop_id': shop_id,
            'shop_name': shop_name,
            'order_money': total_amount,
            'order_way': order_way,
            'cons_phone': cons_phone,
            'cons_name': cons_name,
            'cons_addre': cons_addre,
            'address_id': address_id,  # 新增address_id字段
            'create_time': create_time,
            'remark': remark
        })
        db.session.flush()
        order_id = result.lastrowid

        print(f"订单创建成功，订单ID: {order_id}")

        # 插入订单明细
        detail_count = 0
        for row in cart_data:
            dish_id, quantity, dish_name, price = row[0], row[1], row[2], row[3]
            subtotal = float(price) * quantity

            # 插入订单明细表
            db.session.execute(text('''
                INSERT INTO order_detail (order_id, dish_id, dish_name, price, quantity, subtotal) 
                VALUES (:order_id, :dish_id, :dish_name, :price, :quantity, :subtotal)
            '''), {
                'order_id': order_id,
                'dish_id': dish_id,
                'dish_name': dish_name,
                'price': price,
                'quantity': quantity,
                'subtotal': subtotal
            })
            detail_count += 1

            # 更新菜品销量
            db.session.execute(text('''
                UPDATE dish 
                SET monthly_sales = monthly_sales + :quantity 
                WHERE dish_id = :dish_id
            '''), {'quantity': quantity, 'dish_id': dish_id})

        print(f"插入 {detail_count} 条订单明细")

        # 清空购物车
        db.session.execute(
            text('DELETE FROM cart WHERE user_phone = :user_phone'),
            {'user_phone': user_phone}
        )

        db.session.commit()

        # 返回更多订单信息
        return jsonify(status=200, msg="下单成功", data={
            'order_id': order_id,
            'shop_name': shop_name,
            'total_amount': total_amount,
            'cons_name': cons_name,
            'cons_phone': cons_phone,
            'cons_addre': cons_addre,
            'create_time': create_time,
            'address_id': address_id  # 返回地址ID
        })

    except Exception as e:
        db.session.rollback()
        print(f"下单失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(status=500, msg="下单失败")

# 管理端店铺管理 - 更新到新表结构
@app.route("/api/manager/shop", methods=["POST", "GET", "DELETE"])
@cross_origin()
@admin_required
def manager_shop():
    try:
        # 获取店铺信息 - 更新到新的shop表
        if request.method == 'GET':
            sql = text("""
                SELECT 
                    s.shop_id, 
                    s.shop_name, 
                    s.description, 
                    s.image_url, 
                    s.status, 
                    s.created_time,
                    COALESCE(AVG(d.price), 0) AS avg_price,
                    COALESCE(AVG(d.monthly_sales), 0) AS avg_monthly_sales,
                    COALESCE(SUM(d.monthly_sales), 0) AS total_sales
                FROM shop s
                LEFT JOIN dish d ON s.shop_id = d.shop_id AND d.status = 1
                GROUP BY s.shop_id
                ORDER BY total_sales DESC
            """)
            data = db.session.execute(sql).fetchall()

            Data = []
            for row in data:
                dic = dict(
                    shop_id=row[0],
                    shop_name=row[1],
                    description=row[2] or '',
                    image_url=row[3] or '/images/shop/default-shop.jpg',
                    status=row[4],
                    created_time=row[5].strftime('%Y-%m-%d %H:%M:%S') if row[5] else '',
                    price=round(float(row[6]), 2),
                    avg_sale=round(float(row[7]), 1),  # 每个店铺的平均月销量（用于统计卡片）
                    sale=int(row[8])  # 店铺总月销量（表格里显示）
                )
                Data.append(dic)
            return jsonify(status=200, tabledata=Data)

        # 添加店铺
        if request.method == 'POST' and request.json.get('action') == "add":
            rq = request.json
            shop_name = rq.get('shop_name')
            description = rq.get('description', '')
            image_url = rq.get('image_url', '/images/shop/default-shop.jpg')

            # 检查店铺是否已存在
            exist = db.session.execute(
                text('SELECT * FROM shop WHERE shop_name = :shop_name'),
                {'shop_name': shop_name}
            ).fetchall()

            if not exist:
                db.session.execute(text('''
                    INSERT INTO shop (shop_name, description, image_url) 
                    VALUES (:shop_name, :description, :image_url)
                '''), {
                    'shop_name': shop_name,
                    'description': description,
                    'image_url': image_url
                })
                db.session.commit()
                return jsonify(status=200, msg="添加成功")
            else:
                return jsonify(status=1000, msg="该店铺已存在")

        # 修改店铺
        if request.method == 'POST' and request.json.get('action') == "change":
            rq = request.json
            shop_id = rq.get('shop_id')
            shop_name = rq.get('shop_name')
            description = rq.get('description', '')
            image_url = rq.get('image_url', '/images/shop/default-shop.jpg')
            status = rq.get('status', 1)

            db.session.execute(text('''
                UPDATE shop 
                SET shop_name = :shop_name, description = :description, 
                    image_url = :image_url, status = :status
                WHERE shop_id = :shop_id
            '''), {
                'shop_name': shop_name,
                'description': description,
                'image_url': image_url,
                'status': status,
                'shop_id': shop_id
            })
            db.session.commit()
            return jsonify(status=200, msg="修改成功")

        # 删除店铺 - 改为级联删除
        if request.method == 'DELETE':
            shop_id = request.json.get('shop_id')

            try:
                # 先删除该店铺下的所有菜品（级联删除）
                db.session.execute(
                    text('DELETE FROM dish WHERE shop_id = :shop_id'),
                    {'shop_id': shop_id}
                )

                # 再删除店铺本身
                result = db.session.execute(
                    text('DELETE FROM shop WHERE shop_id = :shop_id'),
                    {'shop_id': shop_id}
                )

                db.session.commit()

                if result.rowcount == 0:
                    return jsonify(status=1004, msg="店铺不存在或已被删除")

                return jsonify(status=200, msg="店铺及所有菜品删除成功")

            except Exception as e:
                db.session.rollback()
                print(f"删除店铺失败: {e}")
                return jsonify(status=500, msg="删除失败，请稍后重试")

    except Exception as e:
        db.session.rollback()
        print(f"管理端店铺操作错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 专门处理店铺状态切换的接口
@app.route("/api/manager/shop/status", methods=["POST"])
@cross_origin()
@admin_required
def toggle_shop_status():
    try:
        data = request.json
        shop_id = data.get('shop_id')
        new_status = data.get('status')

        if not shop_id or new_status is None:
            return jsonify(status=1001, msg="参数错误")

        # 更新店铺状态
        db.session.execute(text('''
            UPDATE shop 
            SET status = :status 
            WHERE shop_id = :shop_id
        '''), {'status': new_status, 'shop_id': shop_id})

        db.session.commit()

        status_text = "启用" if new_status == 1 else "停用"
        return jsonify(status=200, msg=f"店铺{status_text}成功")

    except Exception as e:
        db.session.rollback()
        print(f"切换店铺状态错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 新增：获取所有店铺列表（用于下拉选择）
@app.route("/api/manager/shops/list", methods=["GET"])
@cross_origin()
@admin_required
def manager_shops_list():
    try:
        data = db.session.execute(text('''
            SELECT shop_id, shop_name 
            FROM shop 
            WHERE status = 1
            ORDER BY shop_id
        ''')).fetchall()

        shops = []
        for row in data:
            shops.append({
                'shop_id': row[0],
                'shop_name': row[1]
            })
        return jsonify(status=200, data=shops)
    except Exception as e:
        print(f"获取店铺列表错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 菜品管理接口
@app.route("/api/manager/shop/<int:shop_id>/dishes", methods=["GET", "POST", "PUT", "DELETE"])
@cross_origin()
@admin_required
def manager_shop_dishes(shop_id):
    try:
        # 获取店铺菜品列表
        if request.method == 'GET':
            data = db.session.execute(text('''
                SELECT dish_id, dish_name, price, description, image_url, 
                       monthly_sales, status, sort_order, created_time
                FROM dish 
                WHERE shop_id = :shop_id
                ORDER BY sort_order, dish_id
            '''), {'shop_id': shop_id}).fetchall()

            dishes = []
            for row in data:
                dish = {
                    'dish_id': row[0],
                    'dish_name': row[1],
                    'price': float(row[2]),
                    'description': row[3],
                    'image_url': row[4] if row[4] else '/images/dish/default-dish.jpg',
                    'monthly_sales': row[5],
                    'status': row[6],
                    'sort_order': row[7],
                    'created_time': row[8].strftime('%Y-%m-%d %H:%M:%S') if row[8] else ''
                }
                dishes.append(dish)
            return jsonify(status=200, data=dishes)

        # 添加菜品
        if request.method == 'POST':
            data = request.json
            dish_name = data.get('dish_name')
            price = data.get('price')
            description = data.get('description', '')
            image_url = data.get('image_url', '/images/dish/default-dish.jpg')
            sort_order = data.get('sort_order', 0)

            # 检查菜品是否已存在
            exist = db.session.execute(text('''
                SELECT * FROM dish 
                WHERE shop_id = :shop_id AND dish_name = :dish_name
            '''), {'shop_id': shop_id, 'dish_name': dish_name}).fetchall()

            if exist:
                return jsonify(status=1001, msg="该菜品已存在")

            db.session.execute(text('''
                INSERT INTO dish (shop_id, dish_name, price, description, image_url, sort_order)
                VALUES (:shop_id, :dish_name, :price, :description, :image_url, :sort_order)
            '''), {
                'shop_id': shop_id,
                'dish_name': dish_name,
                'price': price,
                'description': description,
                'image_url': image_url,
                'sort_order': sort_order
            })
            db.session.commit()
            return jsonify(status=200, msg="添加菜品成功")

        # 修改菜品
        if request.method == 'PUT':
            data = request.json
            print(f"=== 收到菜品更新请求 ===")
            print(f"店铺ID: {shop_id}")
            print(f"请求数据: {data}")

            dish_id = data.get('dish_id')
            dish_name = data.get('dish_name')
            price = data.get('price')
            description = data.get('description', '')
            image_url = data.get('image_url', '/images/dish/default-dish.jpg')
            # 关键修改：不要设置默认值
            status = data.get('status')
            sort_order = data.get('sort_order', 0)

            # 验证必要字段
            if not dish_id or not dish_name:
                return jsonify(status=1001, msg="菜品ID和名称不能为空")

            # 验证status字段是否存在且有效
            if status is None:
                return jsonify(status=1002, msg="状态字段不能为空")

            # 确保status是整数类型
            try:
                status = int(status)
                if status not in [0, 1]:
                    return jsonify(status=1003, msg="状态值无效，必须是0或1")
            except (ValueError, TypeError):
                return jsonify(status=1003, msg="状态值必须是数字")

            print(f"更新菜品状态: dish_id={dish_id}, status={status}")

            # 执行更新
            result = db.session.execute(text('''
                UPDATE dish 
                SET dish_name = :dish_name, price = :price, description = :description,
                    image_url = :image_url, status = :status, sort_order = :sort_order
                WHERE dish_id = :dish_id AND shop_id = :shop_id
            '''), {
                'dish_name': dish_name,
                'price': price,
                'description': description,
                'image_url': image_url,
                'status': status,
                'sort_order': sort_order,
                'dish_id': dish_id,
                'shop_id': shop_id
            })

            db.session.commit()
            print(f"更新成功，影响行数: {result.rowcount}")
            return jsonify(status=200, msg="修改菜品成功")

        # 删除菜品
        if request.method == 'DELETE':
            dish_id = request.json.get('dish_id')

            db.session.execute(text('''
                DELETE FROM dish 
                WHERE dish_id = :dish_id AND shop_id = :shop_id
            '''), {'dish_id': dish_id, 'shop_id': shop_id})
            db.session.commit()
            return jsonify(status=200, msg="删除菜品成功")

    except Exception as e:
        db.session.rollback()
        print(f"菜品管理错误: {e}")
        return jsonify(status=500, msg="系统错误")


from flask import jsonify, request
from flask_cors import cross_origin
from sqlalchemy import text




@app.route("/api/manage/admininfo", methods=["GET", "POST"])
@cross_origin()  # 允许后台跨域访问
@admin_required
def manage_admininfo():
    """
    GET  : 获取当前管理员的个人信息（管理员后台专用）
    POST : 保存管理员个人信息修改
    """
    # 1. 统一 token 校验（和用户端完全一样）
    token = request.headers.get('token')
    phone = request.current_admin_phone

    if not phone:
        return jsonify(status=1001, msg="登录已过期，请重新登录")

    try:
        if request.method == 'GET':
            # 兼容 11位 和 10位手机号（彻底杜绝查不到的问题）
            sql = text("""
                SELECT real_name, sex, age, mail, phone, user_name
                FROM user_msg
                WHERE phone = :phone1
                   OR phone = :phone2
                   OR phone = :phone3
            """)

            # phone1: 完整11位
            # phone2: 如果是10位，补1再试
            # phone3: 如果是11位，去1再试（兼容所有历史垃圾数据）
            p1 = phone
            p2 = '1' + phone if len(phone) == 10 and phone.isdigit() else phone
            p3 = phone[1:] if phone.startswith('1') and len(phone) == 11 else phone

            result = db.session.execute(sql, {"phone1": p1, "phone2": p2, "phone3": p3}).fetchone()

            if not result:
                return jsonify(status=1002, msg="管理员信息未找到")

            data = {
                "real_name": result.real_name or "",
                "sex": result.sex or "男",
                "age": result.age if result.age is not None else "",
                "mail": result.mail or "",
                "phone": result.phone or phone,  # 优先用数据库的，防止乱码
                "user_name": result.user_name or "管理员"
            }
            return jsonify({"status": 200, "data": data})

        # ==================== POST：保存管理员信息 ====================
        elif request.method == 'POST':
            json_data = request.json
            if not json_data:
                return jsonify(status=400, msg="请求数据不能为空")

            real_name = json_data.get("real_name", "").strip()
            sex = json_data.get("sex", "").strip()
            age = json_data.get("age")
            mail = json_data.get("mail", "").strip()
            user_name = json_data.get("user_name", "").strip()

            if not real_name or not user_name:
                return jsonify(status=1003, msg="真实姓名和用户名不能为空")

            # age 处理
            if age in ["", None, "null"]:
                age = None
            else:
                try:
                    age = int(age)
                except:
                    return jsonify(status=1005, msg="年龄格式错误")

            # 使用数据库中真实的 phone 更新（避免手机号格式问题）
            find_phone_sql = text("SELECT phone FROM user_msg WHERE phone LIKE :pattern")
            real_phone = db.session.execute(find_phone_sql, {"pattern": f"%{phone[-10:]}"})  # 取后10位模糊匹配
            real_phone = real_phone.fetchone()
            update_phone = real_phone[0] if real_phone else phone

            update_sql = text("""
                UPDATE user_msg SET
                    real_name = :real_name,
                    sex = :sex,
                    age = :age,
                    mail = :mail,
                    user_name = :user_name
                WHERE phone = :phone
            """)
            result = db.session.execute(update_sql, {
                "real_name": real_name,
                "sex": sex,
                "age": age,
                "mail": mail,
                "user_name": user_name,
                "phone": update_phone
            })

            if result.rowcount == 0:
                return jsonify(status=1004, msg="更新失败，信息未变更")

            db.session.commit()
            return jsonify(status=200, msg="保存成功")

    except Exception as e:
        db.session.rollback()
        print(f"管理员信息接口错误: {e}")
        return jsonify(status=500, msg="服务器错误")



# ==================== 用户管理接口 ====================
@app.route("/api/manager/users", methods=["GET", "PUT", "DELETE"])
@cross_origin()
@super_admin_required
def manager_users():
    try:
        # ==================== GET：获取用户列表 ====================
        if request.method == 'GET':
            search = request.args.get('search', '').strip()
            page = int(request.args.get('page', 1))
            size = int(request.args.get('size', 10))

            base_sql = """
                SELECT id, username, telephone, role, 
                       DATE_FORMAT(created_time, '%Y-%m-%d %H:%i:%s') as created_time
                FROM user
            """
            params = {}
            if search:
                base_sql += " WHERE username LIKE :search OR telephone LIKE :search"
                params['search'] = f"%{search}%"

            count_sql = "SELECT COUNT(*) FROM user"
            if search:
                count_sql += " WHERE username LIKE :search OR telephone LIKE :search"

            total = db.session.execute(text(count_sql), params).scalar()

            offset = (page - 1) * size
            sql = base_sql + " ORDER BY id DESC LIMIT :limit OFFSET :offset"
            params.update({'limit': size, 'offset': offset})

            rows = db.session.execute(text(sql), params).fetchall()

            data = []
            for row in rows:
                data.append({
                    'id': row.id,
                    'username': row.username,
                    'telephone': row.telephone,
                    'role': row.role,
                    'role_text': '管理员' if row.role == 1 else '普通用户',
                    'created_time': row.created_time
                })

            return jsonify(status=200, total=total, data=data)

        # ==================== PUT：修改角色 ====================
        elif request.method == 'PUT':
            rq = request.json
            user_id = rq.get('id')
            new_role = rq.get('role')

            if new_role not in [0, 1]:
                return jsonify(status=1001, msg="角色值不合法")

            if new_role == 0:
                current_role = db.session.execute(
                    text("SELECT role FROM user WHERE id = :id"), {'id': user_id}
                ).scalar()

                if current_role == 1:
                    admin_count = db.session.execute(
                        text("SELECT COUNT(*) FROM user WHERE role = 1")
                    ).scalar()
                    if admin_count <= 1:
                        return jsonify(status=1002, msg="系统必须保留至少一位管理员！")

            db.session.execute(
                text("UPDATE user SET role = :role WHERE id = :id"),
                {'role': new_role, 'id': user_id}
            )
            db.session.commit()
            return jsonify(status=200, msg="角色修改成功")

        # ==================== DELETE：删除用户（安全版） ====================
        elif request.method == 'DELETE':
            rq = request.json
            user_id = rq.get('id')
            if not user_id:
                return jsonify(status=1001, msg="缺少用户ID")

            # 1. 不能删除自己
            current_phone = request.current_admin_phone
            current_user = db.session.execute(
                text("SELECT id FROM user WHERE telephone = :phone"),
                {"phone": current_phone}
            ).fetchone()

            if current_user and current_user.id == int(user_id):
                return jsonify(status=1003, msg="不能删除当前登录账号！")

            # 2. 查询目标用户
            target = db.session.execute(
                text("SELECT role, username FROM user WHERE id = :id"),
                {"id": user_id}
            ).fetchone()

            if not target:
                return jsonify(status=1004, msg="用户不存在")

            # 3. 不能删除最后一个管理员
            if target.role == 1:
                admin_count = db.session.execute(
                    text("SELECT COUNT(*) FROM user WHERE role = 1")
                ).scalar()
                if admin_count <= 1:
                    return jsonify(status=1002, msg="不能删除最后一个管理员！")

            # 4. 不能删除系统默认 admin
            if target.username == 'admin':
                return jsonify(status=1005, msg="不能删除系统默认管理员账号！")

            # 执行删除（先删 user_msg 避免外键冲突）
            db.session.execute(text("DELETE FROM user_msg WHERE id = :id"), {"id": user_id})
            db.session.execute(text("DELETE FROM user WHERE id = :id"), {"id": user_id})
            db.session.commit()

            return jsonify(status=200, msg="用户删除成功")

    except Exception as e:
        db.session.rollback()
        print(f"用户管理接口错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 配送员管理
@app.route("/api/manager/dispatcher", methods=["POST", "GET", "DELETE"])
@cross_origin()
@admin_required
def manager_dispatcher():
    if request.method == 'GET':
        data = db.session.execute(text('select * from dispatcher')).fetchall()
        Data = []
        for i in range(len(data)):
            dic = dict(dispatcher_id=data[i][0], dispatcher_name=data[i][1], dispatcher_phone=data[i][2])
            Data.append(dic)
        return jsonify(status=200, tabledata=Data)
    if request.method == 'POST':
        rq = request.json
        dispatcher_id = rq.get('dispatcher_id')
        dispatcher_name = rq.get('dispatcher_name')
        dispatcher_phone = rq.get('dispatcher_phone')
        exist = db.session.execute(text('select * from dispatcher where dispatcher_id="%s"' % dispatcher_id)).fetchall()
        if not exist:
            db.session.execute(
                text('insert dispatcher(dispatcher_id,dispatcher_name,dispatcher_phone) value("%s","%s","%s")' % (
                    dispatcher_id, dispatcher_name, dispatcher_phone)))
            db.session.commit()
            return jsonify(status=200, msg="添加成功")
        else:
            return jsonify(status=1000, msg="该编号已存在")
    if request.method == 'DELETE':
        want_delete = request.json.get('want_delete')
        db.session.execute(text('delete from dispatcher where dispatcher_id="%s"' % want_delete))
        db.session.commit()
        return jsonify(status=200, msg="解雇成功")


# 获取物流信息
@app.route("/api/manager/delivery", methods=["GET"])
@cross_origin()
@admin_required
def manager_delivery():
    ended = request.args.get('id')
    if ended == '0':
        data = db.session.execute(text('select * from delivery where ended=0')).fetchall()
        Data = []
        for i in range(len(data)):
            dic = dict(order_id=data[i][0], cons_phone=data[i][1], disp_id=data[i][2], deliver_time=data[i][3])
            Data.append(dic)
        return jsonify(status=200, tabledata=Data)
    else:
        data = db.session.execute(text('select * from delivery where ended=1')).fetchall()
        Data = []
        for i in range(len(data)):
            dic = dict(order_id=data[i][0], cons_phone=data[i][1], disp_id=data[i][2], deliver_time=data[i][3])
            Data.append(dic)
        return jsonify(status=200, tabledata=Data)

# 获取所有未发货的订单
@app.route("/api/manager/unsend", methods=["GET", "POST"])
@cross_origin()
@admin_required
def manager_unsend():
    if request.method == 'GET':
        try:
            # 使用参数化查询获取未发货订单
            data = db.session.execute(text('''
                SELECT o.order_id, o.shop_id, o.shop_name, o.order_money, o.order_way, 
                       o.cons_phone, o.cons_name, o.cons_addre, o.checked, o.create_time,
                       s.image_url as shop_image
                FROM oorder o 
                LEFT JOIN shop s ON o.shop_id = s.shop_id
                WHERE o.checked=0
                ORDER BY o.create_time DESC
            ''')).fetchall()

            Data = []
            for row in data:
                # 获取订单详情
                order_details = db.session.execute(text('''
                    SELECT od.dish_id, od.dish_name, od.price, od.quantity, od.subtotal,
                           d.image_url as dish_image
                    FROM order_detail od
                    LEFT JOIN dish d ON od.dish_id = d.dish_id
                    WHERE od.order_id = :order_id
                '''), {'order_id': row[0]}).fetchall()

                details_list = []
                for detail in order_details:
                    details_list.append({
                        'dish_id': detail[0],
                        'dish_name': detail[1],
                        'price': float(detail[2]),
                        'quantity': detail[3],
                        'subtotal': float(detail[4]),
                        'dish_image': detail[5]
                    })

                dic = {
                    'order_id': row[0],
                    'shop_id': row[1],
                    'shop_name': row[2],
                    'order_money': float(row[3]),  # 修正字段名
                    'order_way': row[4],  # 修正字段名
                    'cons_phone': row[5],
                    'cons_name': row[6],
                    'cons_addre': row[7],
                    'checked': row[8],
                    'create_time': row[9],
                    'shop_image': row[10],
                    'orderDetails': details_list  # 添加订单详情
                }
                Data.append(dic)

            # 获取送餐员信息（包含姓名）
            disp_range = db.session.execute(text('''
                SELECT dispatcher_id, dispatcher_name, dispatcher_phone 
                FROM dispatcher
            ''')).fetchall()

            Disp_range = []
            for row in disp_range:
                dic = {
                    'disp_id': row[0],
                    'disp_name': row[1],
                    'disp_phone': row[2]
                }
                Disp_range.append(dic)

            return jsonify(status=200, tabledata=Data, disp_range=Disp_range)

        except Exception as e:
            print(f"获取未发货订单失败: {e}")
            return jsonify(status=500, msg="获取数据失败")

    if request.method == 'POST':
        try:
            rq = request.json
            order_id = rq.get('order_id')
            disp_id = rq.get('dispatcher_id')
            deliver_time = rq.get('deliver_time')

            if not all([order_id, disp_id, deliver_time]):
                return jsonify(status=400, msg="参数不完整")

            # 使用参数化查询获取收货人电话
            cons_phone_result = db.session.execute(
                text('SELECT cons_phone FROM oorder WHERE order_id = :order_id'),
                {'order_id': order_id}
            ).first()

            if not cons_phone_result:
                return jsonify(status=404, msg="订单不存在")

            cons_phone = cons_phone_result[0]

            # 插入派送记录
            db.session.execute(text('''
                INSERT INTO delivery (order_id, cons_phone, disp_id, deliver_time) 
                VALUES (:order_id, :cons_phone, :disp_id, :deliver_time)
            '''), {
                'order_id': order_id,
                'cons_phone': cons_phone,
                'disp_id': disp_id,
                'deliver_time': deliver_time
            })

            # 更新订单状态为已派送 (checked=1)
            db.session.execute(text('''
                UPDATE oorder SET checked = 1 WHERE order_id = :order_id
            '''), {'order_id': order_id})

            db.session.commit()
            return jsonify(status=200, msg="成功派发")

        except Exception as e:
            db.session.rollback()
            print(f"派单失败: {e}")
            return jsonify(status=500, msg="派单失败")

# 获取所有正在运送的订单
@app.route("/api/manager/sending", methods=["GET"])
@cross_origin()
@admin_required
def manager_sending():
    if request.method == 'GET':
        try:
            # 使用参数化查询获取所有已发货订单（checked=1）
            data = db.session.execute(text('''
                SELECT o.order_id, o.shop_id, o.shop_name, o.order_money, o.order_way, 
                       o.cons_phone, o.cons_name, o.cons_addre, o.checked, o.create_time,
                       s.image_url as shop_image,
                       d.disp_id, d.deliver_time, dp.dispatcher_name, dp.dispatcher_phone
                FROM oorder o 
                LEFT JOIN shop s ON o.shop_id = s.shop_id
                LEFT JOIN delivery d ON o.order_id = d.order_id
                LEFT JOIN dispatcher dp ON d.disp_id = dp.dispatcher_id
                WHERE o.checked=1
                ORDER BY o.create_time DESC
            ''')).fetchall()

            Data = []
            for row in data:
                # 获取订单详情
                order_details = db.session.execute(text('''
                    SELECT od.dish_id, od.dish_name, od.price, od.quantity, od.subtotal,
                           d.image_url as dish_image
                    FROM order_detail od
                    LEFT JOIN dish d ON od.dish_id = d.dish_id
                    WHERE od.order_id = :order_id
                '''), {'order_id': row[0]}).fetchall()

                details_list = []
                for detail in order_details:
                    details_list.append({
                        'dish_id': detail[0],
                        'dish_name': detail[1],
                        'price': float(detail[2]),
                        'quantity': detail[3],
                        'subtotal': float(detail[4]),
                        'dish_image': detail[5]
                    })

                dic = {
                    'order_id': row[0],
                    'shop_id': row[1],
                    'shop_name': row[2],
                    'order_money': float(row[3]),
                    'order_way': row[4],
                    'cons_phone': row[5],
                    'cons_name': row[6],
                    'cons_addre': row[7],
                    'checked': row[8],
                    'create_time': row[9],
                    'shop_image': row[10],
                    'disp_id': row[11],
                    'deliver_time': row[12],
                    'disp_name': row[13],  # 配送员姓名
                    'disp_phone': row[14],  # 配送员电话
                    'orderDetails': details_list
                }
                Data.append(dic)

            return jsonify(status=200, tabledata=Data)

        except Exception as e:
            print(f"获取已发货订单失败: {e}")
            return jsonify(status=500, msg="获取数据失败")

# 获取所有已经收货的订单
@app.route("/api/manager/sended", methods=["GET"])
@cross_origin()
@admin_required
def manager_sended():
    if request.method == 'GET':
        try:
            # 使用参数化查询获取所有已完成订单（checked=2）
            data = db.session.execute(text('''
                SELECT o.order_id, o.shop_id, o.shop_name, o.order_money, o.order_way, 
                       o.cons_phone, o.cons_name, o.cons_addre, o.checked, o.create_time,
                       s.image_url as shop_image,
                       d.disp_id, d.deliver_time, dp.dispatcher_name, dp.dispatcher_phone
                FROM oorder o 
                LEFT JOIN shop s ON o.shop_id = s.shop_id
                LEFT JOIN delivery d ON o.order_id = d.order_id
                LEFT JOIN dispatcher dp ON d.disp_id = dp.dispatcher_id
                WHERE o.checked=2
                ORDER BY o.create_time DESC
            ''')).fetchall()

            Data = []
            for row in data:
                # 获取订单详情
                order_details = db.session.execute(text('''
                    SELECT od.dish_id, od.dish_name, od.price, od.quantity, od.subtotal,
                           d.image_url as dish_image
                    FROM order_detail od
                    LEFT JOIN dish d ON od.dish_id = d.dish_id
                    WHERE od.order_id = :order_id
                '''), {'order_id': row[0]}).fetchall()

                details_list = []
                for detail in order_details:
                    details_list.append({
                        'dish_id': detail[0],
                        'dish_name': detail[1],
                        'price': float(detail[2]),
                        'quantity': detail[3],
                        'subtotal': float(detail[4]),
                        'dish_image': detail[5]
                    })

                dic = {
                    'order_id': row[0],
                    'shop_id': row[1],
                    'shop_name': row[2],
                    'order_money': float(row[3]),
                    'order_way': row[4],
                    'cons_phone': row[5],
                    'cons_name': row[6],
                    'cons_addre': row[7],
                    'checked': row[8],
                    'create_time': row[9],
                    'shop_image': row[10],
                    'disp_id': row[11],
                    'deliver_time': row[12],
                    'disp_name': row[13],  # 配送员姓名
                    'disp_phone': row[14],  # 配送员电话
                    'orderDetails': details_list
                }
                Data.append(dic)

            return jsonify(status=200, tabledata=Data)

        except Exception as e:
            print(f"获取已完成订单失败: {e}")
            return jsonify(status=500, msg="获取数据失败")




# 商家管理相关接口
def store_owner_required(f):
    """商家权限校验装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('token')
        phone = get_token_phone(token)
        if not phone:
            return jsonify({"status": 1001, "msg": "请重新登录"})

        # 校验用户角色：role=1 且 is_super=0 的为商家
        user_result = db.session.execute(
            text("SELECT id, username, role, is_super FROM user WHERE telephone = :phone"),
            {"phone": phone}
        ).fetchone()

        if not user_result or user_result.role != 1 or user_result.is_super != 0:
            return jsonify({"status": 403, "msg": "权限不足，只有商家可以访问此接口"})

        # 保存当前商家信息
        request.current_store_owner_id = user_result.id
        request.current_store_owner_username = user_result.username
        return f(*args, **kwargs)

    return decorated_function


# 根据商家用户名获取店铺信息
@app.route("/api/shop/owner/<string:username>", methods=["GET"])
@cross_origin()
@store_owner_required
def get_shop_by_owner(username):
    try:
        # 验证请求的username与当前商家用户名是否匹配
        if username != request.current_store_owner_username:
            return jsonify({"status": 403, "msg": "只能访问自己的店铺信息"})

        # 查询商家拥有的店铺 - 修正后的查询
        shop_query = text("""
            SELECT s.shop_id, s.shop_name, s.description, s.image_url, s.status, s.created_time
            FROM shop s
            WHERE s.owner_username = :username
        """)

        shop_data_list = db.session.execute(shop_query, {'username': username}).fetchall()

        if shop_data_list:
            shops_info = []
            for shop_data in shop_data_list:
                shop_info = {
                    'shop_id': shop_data[0],
                    'shop_name': shop_data[1],
                    'description': shop_data[2] or '',
                    'image_url': shop_data[3] or '/images/shop/default-shop.jpg',
                    'status': shop_data[4],
                    'created_time': shop_data[5].strftime('%Y-%m-%d %H:%M:%S') if shop_data[5] else ''
                }
                shops_info.append(shop_info)

            return jsonify(status=200, data=shops_info)
        else:
            return jsonify(status=404, msg="未找到该商家的店铺信息")

    except Exception as e:
        print(f"获取商家店铺信息错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 根据店铺ID获取菜品列表
@app.route("/api/dishes/shop/<int:shop_id>", methods=["GET"])
@cross_origin()
@store_owner_required
def get_dishes_by_shop_id(shop_id):
    try:
        current_username = request.current_store_owner_username

        # 验证当前用户是否有权限访问该店铺
        shop_query = text("""
            SELECT s.shop_id 
            FROM shop s 
            WHERE s.shop_id = :shop_id AND s.owner_username = :username
        """)
        shop_result = db.session.execute(shop_query, {
            'shop_id': shop_id,
            'username': current_username
        }).fetchone()

        if not shop_result:
            return jsonify(status=403, msg="无权访问该店铺的菜品信息")

        # 查询该店铺的所有菜品
        dishes_query = text("""
            SELECT dish_id, dish_name, price, description, image_url, 
                   monthly_sales, status, sort_order, created_time
            FROM dish 
            WHERE shop_id = :shop_id
            ORDER BY sort_order, dish_id
        """)

        dishes_data = db.session.execute(dishes_query, {'shop_id': shop_id}).fetchall()

        dishes = []
        for row in dishes_data:
            dish = {
                'dish_id': row[0],
                'dish_name': row[1],
                'price': float(row[2]),
                'description': row[3] or '',
                'image_url': row[4] or '/images/dish/default-dish.jpg',
                'monthly_sales': row[5],
                'status': bool(row[6]),  # 确保返回布尔值
                'sort_order': row[7],
                'created_time': row[8].strftime('%Y-%m-%d %H:%M:%S') if row[8] else ''
            }
            dishes.append(dish)

        return jsonify(status=200, data=dishes)

    except Exception as e:
        print(f"根据店铺ID获取菜品错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 创建新店铺
@app.route("/api/shop/owner/<string:username>", methods=["POST"])
@cross_origin()
@store_owner_required
def create_shop_by_owner(username):
    try:
        # 验证权限
        if username != request.current_store_owner_username:
            return jsonify({"status": 403, "msg": "只能为自己创建店铺"})

        # 获取前端图片存储路径
        upload_dir = get_frontend_image_path("shop")

        # 检查是表单数据还是JSON数据
        if request.content_type and 'multipart/form-data' in request.content_type:
            # 处理表单数据（包含文件上传）
            shop_name = request.form.get('shop_name')
            description = request.form.get('description', '')
            status = request.form.get('status', 1, type=int)
            image_url = '/images/shop/default-shop.jpg'  # 默认图片

            if not shop_name:
                return jsonify(status=1001, msg="店铺名称不能为空")

            # 处理文件上传
            image_file = request.files.get('image_file')
            if image_file and image_file.filename:
                success, new_image_url, error_msg = save_uploaded_image(
                    image_file, shop_name, "shop"
                )
                if success:
                    image_url = new_image_url
                else:
                    return jsonify(status=400, msg=error_msg)
        else:
            # 处理JSON数据（保持向后兼容）
            data = request.json
            if not data:
                return jsonify(status=400, msg="请求数据不能为空")

            shop_name = data.get('shop_name')
            description = data.get('description', '')
            image_url = data.get('image_url', '/images/shop/default-shop.jpg')
            status = data.get('status', 1)

            if not shop_name:
                return jsonify(status=1001, msg="店铺名称不能为空")

        # 检查店铺名称是否已存在
        check_query = text("SELECT shop_id FROM shop WHERE shop_name = :shop_name")
        existing_shop = db.session.execute(check_query, {'shop_name': shop_name}).fetchone()

        if existing_shop:
            return jsonify(status=1002, msg="店铺名称已存在")

        # 插入新店铺
        insert_query = text("""
            INSERT INTO shop (shop_name, owner_username, description, image_url, status)
            VALUES (:shop_name, :owner_username, :description, :image_url, :status)
        """)

        db.session.execute(insert_query, {
            'shop_name': shop_name,
            'owner_username': username,
            'description': description,
            'image_url': image_url,
            'status': status
        })

        db.session.commit()
        return jsonify(status=200, msg="店铺创建成功", image_url=image_url)

    except Exception as e:
        db.session.rollback()
        print(f"创建店铺错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 更新店铺信息
@app.route("/api/shop/<int:shop_id>/owner/<string:username>", methods=["PUT"])
@cross_origin()
@store_owner_required
def update_shop_by_owner(shop_id, username):
    try:
        # 验证权限
        if username != request.current_store_owner_username:
            return jsonify({"status": 403, "msg": "只能修改自己的店铺信息"})

        # 首先验证该店铺是否属于当前用户
        verify_query = text("""
            SELECT shop_id, image_url FROM shop 
            WHERE shop_id = :shop_id AND owner_username = :username
        """)
        shop_info = db.session.execute(verify_query, {
            'shop_id': shop_id,
            'username': username
        }).fetchone()

        if not shop_info:
            return jsonify(status=403, msg="无权修改该店铺信息")

        image_url = shop_info.image_url

        # 检查是表单数据还是JSON数据
        if request.content_type and 'multipart/form-data' in request.content_type:
            # 处理表单数据（包含文件上传）
            shop_name = request.form.get('shop_name')
            description = request.form.get('description', '')
            status = request.form.get('status', 1, type=int)

            if not shop_name:
                return jsonify(status=1001, msg="店铺名称不能为空")

            # 处理文件上传
            image_file = request.files.get('image_file')
            if image_file and image_file.filename:
                success, new_image_url, error_msg = save_uploaded_image(
                    image_file, shop_name, "shop"
                )
                if success:
                    # 删除旧的图片文件
                    delete_old_image(shop_info.image_url, "shop")
                    image_url = new_image_url
                else:
                    return jsonify(status=400, msg=error_msg)
            else:
                # 如果没有上传文件，但提供了URL，使用URL
                provided_url = request.form.get('image_url')
                if provided_url:
                    image_url = provided_url
        else:
            # 处理JSON数据（保持向后兼容）
            data = request.json
            if not data:
                return jsonify(status=400, msg="请求数据不能为空")

            shop_name = data.get('shop_name')
            description = data.get('description', '')
            image_url = data.get('image_url', image_url)  # 如果没有提供，保持原图片
            status = data.get('status', 1)

            if not shop_name:
                return jsonify(status=1001, msg="店铺名称不能为空")

        # 检查店铺名称是否与其他店铺重复
        check_query = text("SELECT shop_id FROM shop WHERE shop_name = :shop_name AND shop_id != :shop_id")
        existing_shop = db.session.execute(check_query, {'shop_name': shop_name, 'shop_id': shop_id}).fetchone()

        if existing_shop:
            return jsonify(status=1002, msg="店铺名称已存在")

        # 更新店铺信息
        update_query = text("""
            UPDATE shop 
            SET shop_name = :shop_name, description = :description, 
                image_url = :image_url, status = :status
            WHERE shop_id = :shop_id AND owner_username = :username
        """)

        result = db.session.execute(update_query, {
            'shop_name': shop_name,
            'description': description,
            'image_url': image_url,
            'status': status,
            'shop_id': shop_id,
            'username': username
        })

        if result.rowcount == 0:
            return jsonify(status=1004, msg="店铺不存在或更新失败")

        db.session.commit()
        return jsonify(status=200, msg="店铺信息更新成功", image_url=image_url)

    except Exception as e:
        db.session.rollback()
        print(f"商家更新店铺信息错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 删除店铺（级联删除）
@app.route("/api/shop/<int:shop_id>/owner/<string:username>", methods=["DELETE"])
@cross_origin()
@store_owner_required
def delete_shop_by_owner(shop_id, username):
    try:
        # 验证权限
        if username != request.current_store_owner_username:
            return jsonify({"status": 403, "msg": "只能删除自己的店铺"})

        # 首先验证该店铺是否属于当前用户，并获取店铺图片
        verify_query = text("""
            SELECT shop_id, image_url FROM shop 
            WHERE shop_id = :shop_id AND owner_username = :username
        """)
        shop_info = db.session.execute(verify_query, {
            'shop_id': shop_id,
            'username': username
        }).fetchone()

        if not shop_info:
            return jsonify(status=403, msg="无权删除该店铺")

        # 检查是否有关联的订单存在
        check_orders_query = text("SELECT order_id FROM oorder WHERE shop_id = :shop_id LIMIT 1")
        has_orders = db.session.execute(check_orders_query, {'shop_id': shop_id}).fetchone()

        # 如果有订单关联，不能删除
        if has_orders:
            return jsonify(status=400, msg="该店铺有关联的订单，无法删除")

        # 开始事务，先删除关联的菜品，再删除店铺
        try:
            # 获取该店铺下的所有菜品信息（用于删除菜品图片）
            dishes_query = text("SELECT dish_id, image_url FROM dish WHERE shop_id = :shop_id")
            dishes = db.session.execute(dishes_query, {'shop_id': shop_id}).fetchall()

            # 删除所有菜品的图片文件
            for dish in dishes:
                delete_old_image(dish.image_url, "dish")
                print(f"已删除菜品图片: {dish.image_url}")

            # 删除关联的菜品
            delete_dishes_query = text("DELETE FROM dish WHERE shop_id = :shop_id")
            db.session.execute(delete_dishes_query, {'shop_id': shop_id})

            # 删除店铺图片文件
            delete_old_image(shop_info.image_url, "shop")
            print(f"已删除店铺图片: {shop_info.image_url}")

            # 删除店铺
            delete_shop_query = text("DELETE FROM shop WHERE shop_id = :shop_id AND owner_username = :username")
            result = db.session.execute(delete_shop_query, {
                'shop_id': shop_id,
                'username': username
            })

            if result.rowcount == 0:
                db.session.rollback()
                return jsonify(status=404, msg="店铺不存在或删除失败")

            db.session.commit()
            return jsonify(status=200, msg="店铺及关联菜品删除成功")

        except Exception as e:
            db.session.rollback()
            print(f"删除店铺事务错误: {e}")
            return jsonify(status=500, msg="删除失败，请稍后重试")

    except Exception as e:
        db.session.rollback()
        print(f"删除店铺错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 添加菜品
@app.route("/api/dishes", methods=["POST"])
@cross_origin()
@store_owner_required
def add_dish():
    try:
        current_username = request.current_store_owner_username

        # 检查是表单数据还是JSON数据
        if request.content_type and 'multipart/form-data' in request.content_type:
            # 处理表单数据（包含文件上传）
            shop_id = request.form.get('shop_id')
            dish_name = request.form.get('dish_name')
            price = request.form.get('price')
            description = request.form.get('description', '')
            sort_order = request.form.get('sort_order', 0, type=int)
            status = request.form.get('status', 1, type=int)
            image_url = '/images/dish/default-dish.jpg'  # 默认图片

            if not dish_name:
                return jsonify(status=400, msg="菜品名称不能为空")
            if not price:
                return jsonify(status=400, msg="菜品价格不能为空")

            # 处理文件上传
            image_file = request.files.get('image_file')
            if image_file and image_file.filename:
                success, new_image_url, error_msg = save_uploaded_image(
                    image_file, dish_name, "dish"
                )
                if success:
                    image_url = new_image_url
                else:
                    return jsonify(status=400, msg=error_msg)
        else:
            # 处理JSON数据（保持向后兼容）
            data = request.get_json()
            if not data:
                return jsonify(status=400, msg="请求数据不能为空")

            shop_id = data.get('shop_id')
            dish_name = data.get('dish_name')
            price = data.get('price')
            description = data.get('description', '')
            image_url = data.get('image_url', '/images/dish/default-dish.jpg')
            sort_order = data.get('sort_order', 0)
            status = data.get('status', 1)

            if not dish_name:
                return jsonify(status=400, msg="菜品名称不能为空")
            if not price:
                return jsonify(status=400, msg="菜品价格不能为空")

        # 验证用户是否有权限在该店铺添加菜品
        shop_query = text("""
            SELECT shop_id FROM shop 
            WHERE shop_id = :shop_id AND owner_username = :username
        """)
        shop_result = db.session.execute(shop_query, {
            'shop_id': shop_id,
            'username': current_username
        }).fetchone()

        if not shop_result:
            return jsonify(status=403, msg="无权在该店铺添加菜品")

        # 插入新菜品
        insert_query = text("""
            INSERT INTO dish (shop_id, dish_name, price, description, image_url, sort_order, status)
            VALUES (:shop_id, :dish_name, :price, :description, :image_url, :sort_order, :status)
        """)

        db.session.execute(insert_query, {
            'shop_id': shop_id,
            'dish_name': dish_name,
            'price': price,
            'description': description,
            'image_url': image_url,
            'sort_order': sort_order,
            'status': status
        })
        db.session.commit()

        return jsonify(status=200, msg="菜品添加成功", image_url=image_url)

    except Exception as e:
        db.session.rollback()
        print(f"添加菜品错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 更新菜品
@app.route("/api/dishes/<int:dish_id>", methods=["PUT"])
@cross_origin()
@store_owner_required
def update_dish(dish_id):
    try:
        current_username = request.current_store_owner_username

        # 首先获取当前菜品信息（用于保留原有图片）
        current_dish_query = text("""
            SELECT d.image_url, d.dish_name, d.shop_id
            FROM dish d 
            JOIN shop s ON d.shop_id = s.shop_id 
            WHERE d.dish_id = :dish_id AND s.owner_username = :username
        """)
        dish_info = db.session.execute(current_dish_query, {
            'dish_id': dish_id,
            'username': current_username
        }).fetchone()

        if not dish_info:
            return jsonify(status=403, msg="无权修改该菜品")

        image_url = dish_info.image_url
        dish_name = dish_info.dish_name
        shop_id = dish_info.shop_id

        # 检查是表单数据还是JSON数据
        if request.content_type and 'multipart/form-data' in request.content_type:
            # 处理表单数据
            dish_name = request.form.get('dish_name', dish_name)
            price = request.form.get('price')
            description = request.form.get('description', '')
            sort_order = request.form.get('sort_order', 0, type=int)
            status = request.form.get('status', 1, type=int)

            if not dish_name:
                return jsonify(status=400, msg="菜品名称不能为空")
            if not price:
                return jsonify(status=400, msg="菜品价格不能为空")

            # 处理文件上传
            image_file = request.files.get('image_file')
            if image_file and image_file.filename:
                success, new_image_url, error_msg = save_uploaded_image(
                    image_file, dish_name, "dish"
                )
                if success:
                    # 删除旧的图片文件
                    delete_old_image(dish_info.image_url, "dish")
                    image_url = new_image_url
                else:
                    return jsonify(status=400, msg=error_msg)
            else:
                # 如果没有上传文件，但提供了URL，使用URL
                provided_url = request.form.get('image_url')
                if provided_url:
                    image_url = provided_url
        else:
            # 处理JSON数据
            data = request.get_json()
            if not data:
                return jsonify(status=400, msg="请求数据不能为空")

            dish_name = data.get('dish_name', dish_name)
            price = data.get('price')
            description = data.get('description', '')
            status = data.get('status', 1)
            sort_order = data.get('sort_order', 0)
            # 如果提供了新的URL，使用新的URL
            if data.get('image_url'):
                image_url = data.get('image_url')

            if not dish_name:
                return jsonify(status=400, msg="菜品名称不能为空")
            if not price:
                return jsonify(status=400, msg="菜品价格不能为空")

        # 更新菜品信息
        update_query = text("""
            UPDATE dish 
            SET dish_name = :dish_name, 
                price = :price, 
                description = :description, 
                image_url = :image_url,
                status = :status,
                sort_order = :sort_order
            WHERE dish_id = :dish_id
        """)

        db.session.execute(update_query, {
            'dish_id': dish_id,
            'dish_name': dish_name,
            'price': price,
            'description': description,
            'image_url': image_url,
            'status': status,
            'sort_order': sort_order
        })
        db.session.commit()

        return jsonify(status=200, msg="菜品更新成功", image_url=image_url)

    except Exception as e:
        db.session.rollback()
        print(f"更新菜品错误: {e}")
        return jsonify(status=500, msg="系统错误")

# 删除菜品
@app.route("/api/dishes/<int:dish_id>", methods=["DELETE"])
@cross_origin()
@store_owner_required
def delete_dish(dish_id):
    try:
        current_username = request.current_store_owner_username

        # 验证用户是否有权限删除该菜品，并获取菜品图片
        dish_query = text("""
            SELECT d.dish_id, d.image_url
            FROM dish d 
            JOIN shop s ON d.shop_id = s.shop_id 
            WHERE d.dish_id = :dish_id AND s.owner_username = :username
        """)
        dish_result = db.session.execute(dish_query, {
            'dish_id': dish_id,
            'username': current_username
        }).fetchone()

        if not dish_result:
            return jsonify(status=403, msg="无权删除该菜品")

        # 删除菜品图片文件
        delete_old_image(dish_result.image_url, "dish")
        print(f"已删除菜品图片: {dish_result.image_url}")

        # 删除菜品记录
        delete_query = text("DELETE FROM dish WHERE dish_id = :dish_id")
        result = db.session.execute(delete_query, {'dish_id': dish_id})

        if result.rowcount == 0:
            return jsonify(status=404, msg="菜品不存在")

        db.session.commit()
        return jsonify(status=200, msg="菜品删除成功")

    except Exception as e:
        db.session.rollback()
        print(f"删除菜品错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 根据商家用户名获取订单列表
@app.route("/api/orders/shop/owner/<string:username>", methods=["GET"])
@cross_origin()
@store_owner_required
def get_orders_by_owner(username):
    try:
        # 验证请求的username与当前商家用户名是否匹配
        if username != request.current_store_owner_username:
            return jsonify({"status": 403, "msg": "只能访问自己的订单信息"})

        # 查询商家拥有的店铺的订单
        orders_query = text("""
            SELECT 
                o.order_id,
                o.shop_name,
                o.shop_id,
                o.order_money,
                o.order_way,
                o.cons_phone,
                o.cons_name,
                o.cons_addre,
                o.checked,
                o.create_time,
                s.owner_username
            FROM oorder o
            LEFT JOIN shop s ON o.shop_id = s.shop_id
            WHERE s.owner_username = :username
            ORDER BY o.create_time DESC
        """)

        orders_data = db.session.execute(orders_query, {'username': username}).fetchall()

        if orders_data:
            orders_info = []
            for order_data in orders_data:
                order_info = {
                    'order_id': order_data[0],
                    'shop_name': order_data[1],
                    'shop_id': order_data[2],
                    'order_money': float(order_data[3]) if order_data[3] else 0,
                    'order_way': order_data[4],
                    'cons_phone': order_data[5],
                    'cons_name': order_data[6],
                    'cons_addre': order_data[7],
                    'checked': order_data[8],
                    'create_time': order_data[9],
                    'owner_username': order_data[10]
                }
                orders_info.append(order_info)

            return jsonify(status=200, data=orders_info, msg="获取订单成功")
        else:
            return jsonify(status=404, msg="该商家暂无订单", data=[])

    except Exception as e:
        print(f"获取商家订单信息错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 获取订单详情
@app.route("/api/orders/<int:order_id>/details", methods=["GET"])
@cross_origin()
@store_owner_required
def get_order_details(order_id):
    try:
        # 首先验证订单是否属于当前商家
        verify_query = text("""
            SELECT o.order_id 
            FROM oorder o
            LEFT JOIN shop s ON o.shop_id = s.shop_id
            WHERE o.order_id = :order_id AND s.owner_username = :username
        """)

        verification = db.session.execute(verify_query, {
            'order_id': order_id,
            'username': request.current_store_owner_username
        }).fetchone()

        if not verification:
            return jsonify({"status": 403, "msg": "无权访问该订单"})

        # 查询订单详情
        details_query = text("""
            SELECT 
                od.detail_id,
                od.dish_id,
                od.dish_name,
                od.price,
                od.quantity,
                od.subtotal,
                d.image_url,
                d.description
            FROM order_detail od
            LEFT JOIN dish d ON od.dish_id = d.dish_id
            WHERE od.order_id = :order_id
        """)

        details_data = db.session.execute(details_query, {'order_id': order_id}).fetchall()

        details_info = []
        for detail_data in details_data:
            detail_info = {
                'detail_id': detail_data[0],
                'dish_id': detail_data[1],
                'dish_name': detail_data[2],
                'price': float(detail_data[3]) if detail_data[3] else 0,
                'quantity': detail_data[4],
                'subtotal': float(detail_data[5]) if detail_data[5] else 0,
                'image_url': detail_data[6] or '/images/dish/default-dish.jpg',
                'description': detail_data[7] or ''
            }
            details_info.append(detail_info)

        return jsonify(status=200, data=details_info, msg="获取订单详情成功")

    except Exception as e:
        print(f"获取订单详情错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 更新订单状态
@app.route("/api/orders/<int:order_id>/status", methods=["PUT"])
@cross_origin()
@store_owner_required
def update_order_status(order_id):
    try:
        data = request.get_json()
        checked = data.get('checked')

        if checked not in [0, 1, 2]:
            return jsonify({"status": 400, "msg": "订单状态值无效"})

        # 验证订单是否属于当前商家
        verify_query = text("""
            SELECT o.order_id 
            FROM oorder o
            LEFT JOIN shop s ON o.shop_id = s.shop_id
            WHERE o.order_id = :order_id AND s.owner_username = :username
        """)

        verification = db.session.execute(verify_query, {
            'order_id': order_id,
            'username': request.current_store_owner_username
        }).fetchone()

        if not verification:
            return jsonify({"status": 403, "msg": "无权操作该订单"})

        # 更新订单状态
        update_query = text("""
            UPDATE oorder 
            SET checked = :checked 
            WHERE order_id = :order_id
        """)

        db.session.execute(update_query, {
            'checked': checked,
            'order_id': order_id
        })
        db.session.commit()

        return jsonify(status=200, msg="更新订单状态成功")

    except Exception as e:
        db.session.rollback()
        print(f"更新订单状态错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 发货接口（创建配送记录）
@app.route("/api/orders/<int:order_id>/delivery", methods=["POST"])
@cross_origin()
@store_owner_required
def create_delivery(order_id):
    try:
        data = request.get_json()
        disp_id = data.get('disp_id')
        deliver_time = data.get('deliver_time', '30分钟')

        if not disp_id:
            return jsonify({"status": 400, "msg": "配送员ID不能为空"})

        # 验证订单是否属于当前商家且状态为待发货
        verify_query = text("""
            SELECT o.order_id, o.cons_phone
            FROM oorder o
            LEFT JOIN shop s ON o.shop_id = s.shop_id
            WHERE o.order_id = :order_id 
                AND s.owner_username = :username 
                AND o.checked = 0
        """)

        verification = db.session.execute(verify_query, {
            'order_id': order_id,
            'username': request.current_store_owner_username
        }).fetchone()

        if not verification:
            return jsonify({"status": 403, "msg": "无权操作该订单或订单状态不正确"})

        # 验证配送员是否存在
        dispatcher_query = text("""
            SELECT dispatcher_id 
            FROM dispatcher 
            WHERE dispatcher_id = :disp_id
        """)

        dispatcher = db.session.execute(dispatcher_query, {'disp_id': disp_id}).fetchone()
        if not dispatcher:
            return jsonify({"status": 400, "msg": "配送员不存在"})

        # 检查是否已存在配送记录
        existing_delivery_query = text("""
            SELECT order_id 
            FROM delivery 
            WHERE order_id = :order_id
        """)

        existing_delivery = db.session.execute(existing_delivery_query, {'order_id': order_id}).fetchone()
        if existing_delivery:
            return jsonify({"status": 400, "msg": "该订单已发货"})

        # 创建配送记录
        delivery_query = text("""
            INSERT INTO delivery (order_id, cons_phone, disp_id, deliver_time, ended) 
            VALUES (:order_id, :cons_phone, :disp_id, :deliver_time, 0)
        """)

        db.session.execute(delivery_query, {
            'order_id': order_id,
            'cons_phone': verification[1],
            'disp_id': disp_id,
            'deliver_time': deliver_time
        })

        # 更新订单状态为已发货
        update_order_query = text("""
            UPDATE oorder 
            SET checked = 1 
            WHERE order_id = :order_id
        """)

        db.session.execute(update_order_query, {'order_id': order_id})
        db.session.commit()

        return jsonify(status=200, msg="发货成功")

    except Exception as e:
        db.session.rollback()
        print(f"发货操作错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 获取配送员列表
@app.route("/api/dispatchers", methods=["GET"])
@cross_origin()
@store_owner_required
def get_dispatchers():
    try:
        dispatchers_query = text("""
            SELECT dispatcher_id, dispatcher_name, dispatcher_phone 
            FROM dispatcher
            ORDER BY dispatcher_id
        """)

        dispatchers_data = db.session.execute(dispatchers_query).fetchall()

        dispatchers_info = []
        for dispatcher_data in dispatchers_data:
            dispatcher_info = {
                'dispatcher_id': dispatcher_data[0],
                'dispatcher_name': dispatcher_data[1],
                'dispatcher_phone': dispatcher_data[2]
            }
            dispatchers_info.append(dispatcher_info)

        return jsonify(status=200, data=dispatchers_info, msg="获取配送员列表成功")

    except Exception as e:
        print(f"获取配送员列表错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 获取订单配送信息
@app.route("/api/orders/<int:order_id>/delivery", methods=["GET"])
@cross_origin()
@store_owner_required
def get_order_delivery(order_id):
    try:
        # 验证订单是否属于当前商家
        verify_query = text("""
            SELECT o.order_id 
            FROM oorder o
            LEFT JOIN shop s ON o.shop_id = s.shop_id
            WHERE o.order_id = :order_id AND s.owner_username = :username
        """)

        verification = db.session.execute(verify_query, {
            'order_id': order_id,
            'username': request.current_store_owner_username
        }).fetchone()

        if not verification:
            return jsonify({"status": 403, "msg": "无权访问该订单"})

        # 查询配送信息
        delivery_query = text("""
            SELECT 
                d.disp_id,
                d.deliver_time,
                dp.dispatcher_name,
                dp.dispatcher_phone
            FROM delivery d
            LEFT JOIN dispatcher dp ON d.disp_id = dp.dispatcher_id
            WHERE d.order_id = :order_id
        """)

        delivery_data = db.session.execute(delivery_query, {'order_id': order_id}).fetchone()

        if delivery_data:
            delivery_info = {
                'disp_id': delivery_data[0],
                'deliver_time': delivery_data[1],
                'dispatcher_name': delivery_data[2],
                'dispatcher_phone': delivery_data[3]
            }
            return jsonify(status=200, data=delivery_info, msg="获取配送信息成功")
        else:
            return jsonify(status=404, msg="未找到配送信息", data=None)

    except Exception as e:
        print(f"获取配送信息错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 销售统计相关接口
@app.route("/api/sales/statistics/owner/<string:username>", methods=["GET"])
@cross_origin()
@store_owner_required
def get_sales_statistics(username):
    try:
        print(f"=== 开始处理销售统计请求，用户名: {username} ===")

        # 验证权限
        if username != request.current_store_owner_username:
            return jsonify({"status": 403, "msg": "只能访问自己的销售数据"})

        # 获取查询参数
        days = request.args.get('days', 7, type=int)
        print(f"查询时间范围: {days}天")

        # 查询商家拥有的店铺
        shop_query = text("""
            SELECT shop_id, shop_name FROM shop WHERE owner_username = :username
        """)
        shops = db.session.execute(shop_query, {'username': username}).fetchall()
        print(f"查询到的店铺: {shops}")

        if not shops:
            return jsonify(status=404, msg="未找到店铺信息", data={})

        shop_ids = [shop[0] for shop in shops]
        print(f"店铺ID列表: {shop_ids}")

        # 构建参数字典
        params = {'days': days, 'username': username}

        # 为每个shop_id创建命名参数
        shop_id_params = {}
        for i, shop_id in enumerate(shop_ids):
            param_name = f'shop_id_{i}'
            shop_id_params[param_name] = shop_id
            params[param_name] = shop_id

        # 构建IN子句
        in_clause = ','.join([f':{param_name}' for param_name in shop_id_params.keys()])

        # 由于create_time是VARCHAR，我们需要用字符串比较来处理时间范围
        # 计算起始日期字符串
        from datetime import datetime, timedelta
        start_date_obj = datetime.now() - timedelta(days=days)
        start_date_str = start_date_obj.strftime('%Y-%m-%d')
        print(f"起始日期字符串: {start_date_str}")

        # 直接使用字符串比较（因为create_time格式是'YYYY-MM-DD HH:MM:SS'）
        # 字符串比较时，'2025-11-21' > '2025-09-01' 是可以比较的
        params['start_date'] = start_date_str

        # 基础统计查询 - 使用字符串比较
        stats_query = text(f"""
            SELECT 
                COUNT(DISTINCT o.order_id) as total_orders,
                COALESCE(SUM(od.subtotal), 0) as total_revenue,
                CASE 
                    WHEN COUNT(DISTINCT o.order_id) > 0 THEN COALESCE(SUM(od.subtotal), 0) / COUNT(DISTINCT o.order_id)
                    ELSE 0 
                END as avg_order_value
            FROM oorder o
            LEFT JOIN order_detail od ON o.order_id = od.order_id
            WHERE o.shop_id IN ({in_clause})
            AND o.create_time IS NOT NULL
            AND o.create_time != ''
            AND SUBSTRING(o.create_time, 1, 10) >= :start_date
        """)

        print(f"执行统计查询: {stats_query}")
        print(f"查询参数: {params}")

        stats_result = db.session.execute(stats_query, params).fetchone()
        print(f"基础统计结果: {stats_result}")

        # 处理基础统计结果
        if stats_result:
            stats_dict = {
                'total_orders': stats_result[0] or 0,
                'total_revenue': float(stats_result[1] or 0),
                'avg_order_value': float(stats_result[2] or 0)
            }
        else:
            stats_dict = {
                'total_orders': 0,
                'total_revenue': 0.0,
                'avg_order_value': 0.0
            }

        # 今日统计 - 直接比较日期部分
        today_date = datetime.now().strftime('%Y-%m-%d')
        params['today_date'] = today_date

        today_stats_query = text(f"""
            SELECT 
                COUNT(DISTINCT o.order_id) as today_orders,
                COALESCE(SUM(od.subtotal), 0) as today_revenue
            FROM oorder o
            LEFT JOIN order_detail od ON o.order_id = od.order_id
            WHERE o.shop_id IN ({in_clause})
            AND o.create_time IS NOT NULL
            AND o.create_time != ''
            AND SUBSTRING(o.create_time, 1, 10) = :today_date
        """)

        print(f"今日统计查询: {today_stats_query}")

        today_stats = db.session.execute(today_stats_query, params).fetchone()
        print(f"今日统计结果: {today_stats}")

        today_dict = {
            'today_orders': today_stats[0] if today_stats else 0,
            'today_revenue': float(today_stats[1] if today_stats else 0)
        }

        # 热销商品统计
        popular_dishes_query = text(f"""
            SELECT 
                d.dish_name,
                SUM(od.quantity) as total_sold,
                SUM(od.subtotal) as total_revenue
            FROM order_detail od
            JOIN oorder o ON od.order_id = o.order_id
            JOIN dish d ON od.dish_id = d.dish_id
            WHERE o.shop_id IN ({in_clause})
            AND o.create_time IS NOT NULL
            AND o.create_time != ''
            AND SUBSTRING(o.create_time, 1, 10) >= :start_date
            GROUP BY d.dish_id, d.dish_name
            ORDER BY total_sold DESC
            LIMIT 5
        """)

        popular_dishes = db.session.execute(popular_dishes_query, params).fetchall()
        print(f"热销商品结果: {popular_dishes}")

        popular_dishes_list = []
        for dish in popular_dishes:
            popular_dishes_list.append({
                'dish_name': dish[0],
                'total_sold': dish[1] or 0,
                'total_revenue': float(dish[2] or 0)
            })

        # 销售趋势数据
        trend_query = text(f"""
            SELECT 
                SUBSTRING(o.create_time, 1, 10) as date,
                COUNT(DISTINCT o.order_id) as order_count,
                COALESCE(SUM(od.subtotal), 0) as daily_revenue
            FROM oorder o
            LEFT JOIN order_detail od ON o.order_id = od.order_id
            WHERE o.shop_id IN ({in_clause})
            AND o.create_time IS NOT NULL
            AND o.create_time != ''
            AND SUBSTRING(o.create_time, 1, 10) >= :start_date
            GROUP BY SUBSTRING(o.create_time, 1, 10)
            ORDER BY date
        """)

        trend_data = db.session.execute(trend_query, params).fetchall()
        print(f"销售趋势结果: {trend_data}")

        trend_list = []
        for trend in trend_data:
            trend_list.append({
                'date': str(trend[0]),  # 已经是字符串格式的日期
                'order_count': trend[1] or 0,
                'daily_revenue': float(trend[2] or 0)
            })

        # 店铺销售排行
        shop_stats_query = text(f"""
            SELECT 
                s.shop_name,
                COUNT(DISTINCT o.order_id) as order_count,
                COALESCE(SUM(od.subtotal), 0) as total_revenue
            FROM oorder o
            LEFT JOIN order_detail od ON o.order_id = od.order_id
            JOIN shop s ON o.shop_id = s.shop_id
            WHERE s.owner_username = :username
            AND o.create_time IS NOT NULL
            AND o.create_time != ''
            AND SUBSTRING(o.create_time, 1, 10) >= :start_date
            GROUP BY s.shop_id, s.shop_name
            ORDER BY total_revenue DESC
        """)

        shop_stats = db.session.execute(shop_stats_query, params).fetchall()
        print(f"店铺排行结果: {shop_stats}")

        shop_stats_list = []
        for shop in shop_stats:
            shop_stats_list.append({
                'shop_name': shop[0],
                'order_count': shop[1] or 0,
                'total_revenue': float(shop[2] or 0)
            })

        # 格式化返回数据
        statistics = {
            'summary': {
                'total_orders': stats_dict['total_orders'],
                'total_revenue': stats_dict['total_revenue'],
                'avg_order_value': stats_dict['avg_order_value'],
                'today_orders': today_dict['today_orders'],
                'today_revenue': today_dict['today_revenue']
            },
            'popular_dishes': popular_dishes_list,
            'sales_trend': trend_list,
            'shop_stats': shop_stats_list,
            'time_range': days,
            'start_date': start_date_str,
            'today_date': today_date
        }

        print(f"最终返回数据: {statistics}")
        return jsonify(status=200, data=statistics, msg="获取销售统计成功")

    except Exception as e:
        print(f"获取销售统计错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify(status=500, msg="系统错误")


# 获取订单状态分布 - 修复时间处理
@app.route("/api/sales/order-status/owner/<string:username>", methods=["GET"])
@cross_origin()
@store_owner_required
def get_order_status_stats(username):
    try:
        if username != request.current_store_owner_username:
            return jsonify({"status": 403, "msg": "只能访问自己的销售数据"})

        days = request.args.get('days', 30, type=int)

        # 计算起始日期
        from datetime import datetime, timedelta
        start_date_obj = datetime.now() - timedelta(days=days)
        start_date_str = start_date_obj.strftime('%Y-%m-%d')

        # 查询商家店铺
        shop_query = text("SELECT shop_id FROM shop WHERE owner_username = :username")
        shops = db.session.execute(shop_query, {'username': username}).fetchall()

        if not shops:
            return jsonify(status=404, msg="未找到店铺信息", data=[])

        shop_ids = [shop[0] for shop in shops]

        # 构建参数字典
        params = {'start_date': start_date_str, 'username': username}

        # 为每个shop_id创建命名参数
        shop_id_params = {}
        for i, shop_id in enumerate(shop_ids):
            param_name = f'shop_id_{i}'
            shop_id_params[param_name] = shop_id
            params[param_name] = shop_id

        # 构建IN子句
        in_clause = ','.join([f':{param_name}' for param_name in shop_id_params.keys()])

        status_query = text(f"""
            SELECT 
                checked as status,
                COUNT(*) as count
            FROM oorder 
            WHERE shop_id IN ({in_clause})
            AND create_time IS NOT NULL
            AND create_time != ''
            AND SUBSTRING(create_time, 1, 10) >= :start_date
            GROUP BY checked
            ORDER BY checked
        """)

        status_data = db.session.execute(status_query, params).fetchall()
        print(f"订单状态查询结果: {status_data}")

        status_stats = [
            {
                'status': status[0],
                'count': status[1],
                'label': {0: '待发货', 1: '配送中', 2: '已完成'}.get(status[0], '未知')
            } for status in status_data
        ]

        return jsonify(status=200, data=status_stats, msg="获取订单状态统计成功")

    except Exception as e:
        print(f"获取订单状态统计错误: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify(status=500, msg="系统错误")


# 获取用户订单异常列表
@app.route("/api/user/issues", methods=["GET"])
@cross_origin()
def get_user_issues():
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        # 获取查询参数
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))
        status = request.args.get('status')
        issue_type = request.args.get('issue_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # 构建查询条件
        where_clauses = ["user_phone = :user_phone"]
        params = {"user_phone": user_phone}

        if status:
            where_clauses.append("status = :status")
            params["status"] = status

        if issue_type:
            where_clauses.append("issue_type = :issue_type")
            params["issue_type"] = issue_type

        if start_date:
            where_clauses.append("DATE(created_time) >= :start_date")
            params["start_date"] = start_date

        if end_date:
            where_clauses.append("DATE(created_time) <= :end_date")
            params["end_date"] = end_date

        where_sql = " AND ".join(where_clauses)

        # 计算总数
        count_sql = f"SELECT COUNT(*) FROM order_issue WHERE {where_sql}"
        total = db.session.execute(text(count_sql), params).scalar() or 0

        # 获取数据
        offset = (page - 1) * size
        query_sql = f"""
            SELECT 
                issue_id, order_id, issue_type, urgency, title, 
                description, image_url, expected_solution, status,
                created_time, updated_time
            FROM order_issue
            WHERE {where_sql}
            ORDER BY 
                CASE urgency 
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END,
                created_time DESC
            LIMIT :limit OFFSET :offset
        """

        params.update({"limit": size, "offset": offset})
        issues = db.session.execute(text(query_sql), params).fetchall()

        # 获取统计信息
        stats_sql = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed
            FROM order_issue
            WHERE user_phone = :user_phone
        """

        stats_result = db.session.execute(text(stats_sql), {"user_phone": user_phone}).fetchone()

        stats = {
            "total": stats_result[0] or 0,
            "pending": stats_result[1] or 0,
            "processing": stats_result[2] or 0,
            "resolved": stats_result[3] or 0,
            "closed": stats_result[4] or 0
        }

        # 格式化数据
        issues_list = []
        for issue in issues:
            issues_list.append({
                "issue_id": issue[0],
                "order_id": issue[1],
                "issue_type": issue[2],
                "urgency": issue[3],
                "title": issue[4],
                "description": issue[5],
                "image_url": issue[6],
                "expected_solution": issue[7],
                "status": issue[8],
                "created_time": issue[9].strftime('%Y-%m-%d %H:%M:%S') if issue[9] else None,
                "updated_time": issue[10].strftime('%Y-%m-%d %H:%M:%S') if issue[10] else None
            })

        return jsonify(status=200, data={
            "issues": issues_list,
            "total": total,
            "page": page,
            "size": size,
            "stats": stats
        })

    except Exception as e:
        print(f"获取订单异常列表错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 获取订单异常统计数量
@app.route("/api/user/issues/count", methods=["GET"])
@cross_origin()
def get_user_issues_count():
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        count_sql = """
            SELECT COUNT(*) as pending_count
            FROM order_issue
            WHERE user_phone = :user_phone 
            AND status IN ('pending', 'processing')
        """

        result = db.session.execute(text(count_sql), {"user_phone": user_phone}).fetchone()

        return jsonify(status=200, data={
            "pending_count": result[0] or 0 if result else 0
        })

    except Exception as e:
        print(f"获取订单异常数量错误: {e}")
        return jsonify(status=200, data={"pending_count": 0})


# 获取可报告问题的订单列表
@app.route("/api/user/issues/available-orders", methods=["GET"])
@cross_origin()
def get_available_orders_for_issues():
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        # 获取最近90天的订单，且订单状态为已完成
        # 注意：由于 create_time 是 VARCHAR，我们需要将其转换为日期进行比较
        query_sql = """
            SELECT 
                o.order_id, o.shop_name, o.order_money, 
                o.checked, o.create_time
            FROM oorder o
            WHERE o.cons_phone = :user_phone
            AND (
                STR_TO_DATE(o.create_time, '%Y-%m-%d %H:%i:%s') >= DATE_SUB(NOW(), INTERVAL 90 DAY)
                OR STR_TO_DATE(o.create_time, '%Y-%m-%d %H:%i:%s') IS NULL
            )
            AND o.checked = 2  -- 只查询已完成的订单
            AND NOT EXISTS (
                SELECT 1 FROM order_issue oi 
                WHERE oi.order_id = o.order_id 
                AND oi.user_phone = :user_phone
                AND oi.status NOT IN ('closed')  -- 排除非关闭状态的已报告问题
            )
            ORDER BY STR_TO_DATE(o.create_time, '%Y-%m-%d %H:%i:%s') DESC
            LIMIT 50
        """

        orders = db.session.execute(text(query_sql), {"user_phone": user_phone}).fetchall()

        orders_list = []
        for order in orders:
            # create_time 是字符串，直接返回即可
            create_time_str = order[4] if order[4] else None

            orders_list.append({
                "order_id": order[0],
                "shop_name": order[1],
                "order_money": float(order[2]) if order[2] else 0,
                "checked": order[3],
                "create_time": create_time_str  # 直接返回字符串
            })

        # 如果找不到符合条件的订单，返回最近3个已完成订单（无时间限制）
        if not orders_list:
            fallback_sql = """
                SELECT 
                    o.order_id, o.shop_name, o.order_money, 
                    o.checked, o.create_time
                FROM oorder o
                WHERE o.cons_phone = :user_phone
                AND o.checked = 2  -- 已完成
                ORDER BY STR_TO_DATE(o.create_time, '%Y-%m-%d %H:%i:%s') DESC
                LIMIT 3
            """

            fallback_orders = db.session.execute(text(fallback_sql), {"user_phone": user_phone}).fetchall()

            for order in fallback_orders:
                orders_list.append({
                    "order_id": order[0],
                    "shop_name": order[1],
                    "order_money": float(order[2]) if order[2] else 0,
                    "checked": order[3],
                    "create_time": order[4] if order[4] else None  # 直接返回字符串
                })

        print(f"为用户 {user_phone} 找到 {len(orders_list)} 个可用订单")  # 调试日志
        return jsonify(status=200, data=orders_list)

    except Exception as e:
        print(f"获取可用订单错误: {e}")
        import traceback
        traceback.print_exc()  # 打印完整的错误堆栈
        return jsonify(status=500, msg="系统错误")

# 提交订单异常报告
@app.route("/api/user/issues", methods=["POST"])
@cross_origin()
def submit_order_issue():
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        data = request.json
        if not data:
            return jsonify(status=400, msg="请求数据不能为空")

        # 验证必填字段
        required_fields = ['order_id', 'issue_type', 'title', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify(status=400, msg=f"{field}不能为空")

        order_id = data.get('order_id')
        issue_type = data.get('issue_type')
        urgency = data.get('urgency', 'medium')
        title = data.get('title')
        description = data.get('description')
        image_url = data.get('image_url', '')
        expected_solution = data.get('expected_solution', '')

        # 验证订单是否存在且属于当前用户
        order_check = db.session.execute(
            text('SELECT order_id FROM oorder WHERE order_id = :order_id AND cons_phone = :user_phone'),
            {'order_id': order_id, 'user_phone': user_phone}
        ).fetchone()

        if not order_check:
            return jsonify(status=403, msg="订单不存在或无权限")

        # 插入订单异常记录
        insert_sql = """
            INSERT INTO order_issue 
            (order_id, user_phone, issue_type, urgency, title, description, image_url, expected_solution, status)
            VALUES 
            (:order_id, :user_phone, :issue_type, :urgency, :title, :description, :image_url, :expected_solution, 'pending')
        """

        db.session.execute(text(insert_sql), {
            'order_id': order_id,
            'user_phone': user_phone,
            'issue_type': issue_type,
            'urgency': urgency,
            'title': title,
            'description': description,
            'image_url': image_url,
            'expected_solution': expected_solution
        })

        # 添加一条跟进记录
        issue_id_result = db.session.execute(
            text("SELECT LAST_INSERT_ID()")
        ).fetchone()

        if issue_id_result:
            issue_id = issue_id_result[0]

            followup_sql = """
                INSERT INTO issue_followup 
                (issue_id, followup_type, content, created_by)
                VALUES 
                (:issue_id, 'user', :content, :created_by)
            """

            db.session.execute(text(followup_sql), {
                'issue_id': issue_id,
                'content': f'用户提交问题报告：{title}',
                'created_by': f'用户 {user_phone}'
            })

        db.session.commit()

        return jsonify(status=200, msg="问题报告提交成功")

    except Exception as e:
        db.session.rollback()
        print(f"提交订单异常报告错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 获取订单异常详情
@app.route("/api/user/issues/<int:issue_id>", methods=["GET"])
@cross_origin()
def get_order_issue_detail(issue_id):
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        # 获取问题详情
        query_sql = """
            SELECT 
                issue_id, order_id, issue_type, urgency, title, 
                description, image_url, expected_solution, status,
                created_time, updated_time
            FROM order_issue
            WHERE issue_id = :issue_id AND user_phone = :user_phone
        """

        issue = db.session.execute(
            text(query_sql),
            {'issue_id': issue_id, 'user_phone': user_phone}
        ).fetchone()

        if not issue:
            return jsonify(status=404, msg="问题不存在或无权限")

        issue_data = {
            "issue_id": issue[0],
            "order_id": issue[1],
            "issue_type": issue[2],
            "urgency": issue[3],
            "title": issue[4],
            "description": issue[5],
            "image_url": issue[6],
            "expected_solution": issue[7],
            "status": issue[8],
            "created_time": issue[9].strftime('%Y-%m-%d %H:%M:%S') if issue[9] else None,
            "updated_time": issue[10].strftime('%Y-%m-%d %H:%M:%S') if issue[10] else None
        }

        return jsonify(status=200, data=issue_data)

    except Exception as e:
        print(f"获取订单异常详情错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 获取订单异常跟进记录
@app.route("/api/user/issues/<int:issue_id>/followups", methods=["GET"])
@cross_origin()
def get_issue_followups(issue_id):
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        # 验证问题属于当前用户
        issue_check = db.session.execute(
            text('SELECT issue_id FROM order_issue WHERE issue_id = :issue_id AND user_phone = :user_phone'),
            {'issue_id': issue_id, 'user_phone': user_phone}
        ).fetchone()

        if not issue_check:
            return jsonify(status=403, msg="无权限查看此问题的跟进记录")

        # 获取跟进记录
        query_sql = """
            SELECT 
                followup_id, followup_type, content, image_url, 
                created_by, created_time
            FROM issue_followup
            WHERE issue_id = :issue_id
            ORDER BY created_time ASC
        """

        followups = db.session.execute(text(query_sql), {'issue_id': issue_id}).fetchall()

        followups_list = []
        for followup in followups:
            followups_list.append({
                "followup_id": followup[0],
                "followup_type": followup[1],
                "content": followup[2],
                "image_url": followup[3],
                "created_by": followup[4],
                "created_time": followup[5].strftime('%Y-%m-%d %H:%M:%S') if followup[5] else None
            })

        return jsonify(status=200, data=followups_list)

    except Exception as e:
        print(f"获取跟进记录错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 添加跟进记录
@app.route("/api/user/issues/<int:issue_id>/followups", methods=["POST"])
@cross_origin()
def add_issue_followup(issue_id):
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        data = request.json
        if not data:
            return jsonify(status=400, msg="请求数据不能为空")

        content = data.get('content', '')
        image_url = data.get('image_url', '')

        if not content:
            return jsonify(status=400, msg="跟进内容不能为空")

        # 验证问题属于当前用户
        issue_check = db.session.execute(
            text('SELECT issue_id, status FROM order_issue WHERE issue_id = :issue_id AND user_phone = :user_phone'),
            {'issue_id': issue_id, 'user_phone': user_phone}
        ).fetchone()

        if not issue_check:
            return jsonify(status=403, msg="无权限添加跟进")

        # 如果问题已关闭或已解决，不允许添加跟进
        if issue_check[1] in ['closed', 'resolved']:
            return jsonify(status=400, msg="问题已处理完成，不能添加跟进")

        # 插入跟进记录
        insert_sql = """
            INSERT INTO issue_followup 
            (issue_id, followup_type, content, image_url, created_by)
            VALUES 
            (:issue_id, 'user', :content, :image_url, :created_by)
        """

        db.session.execute(text(insert_sql), {
            'issue_id': issue_id,
            'content': content,
            'image_url': image_url,
            'created_by': f'用户 {user_phone}'
        })

        # 更新问题状态为处理中（如果是待处理状态）
        if issue_check[1] == 'pending':
            update_sql = """
                UPDATE order_issue 
                SET status = 'processing', updated_time = NOW()
                WHERE issue_id = :issue_id
            """
            db.session.execute(text(update_sql), {'issue_id': issue_id})

        db.session.commit()

        return jsonify(status=200, msg="跟进添加成功")

    except Exception as e:
        db.session.rollback()
        print(f"添加跟进记录错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 标记问题为已解决
@app.route("/api/user/issues/<int:issue_id>/resolve", methods=["PUT"])
@cross_origin()
def resolve_order_issue(issue_id):
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        # 验证问题属于当前用户
        issue_check = db.session.execute(
            text('SELECT issue_id FROM order_issue WHERE issue_id = :issue_id AND user_phone = :user_phone'),
            {'issue_id': issue_id, 'user_phone': user_phone}
        ).fetchone()

        if not issue_check:
            return jsonify(status=403, msg="无权限操作此问题")

        # 更新问题状态
        update_sql = """
            UPDATE order_issue 
            SET status = 'resolved', updated_time = NOW()
            WHERE issue_id = :issue_id
        """

        db.session.execute(text(update_sql), {'issue_id': issue_id})

        # 添加一条系统跟进记录
        followup_sql = """
            INSERT INTO issue_followup 
            (issue_id, followup_type, content, created_by)
            VALUES 
            (:issue_id, 'system', '用户确认问题已解决', '系统')
        """

        db.session.execute(text(followup_sql), {'issue_id': issue_id})

        db.session.commit()

        return jsonify(status=200, msg="问题已标记为已解决")

    except Exception as e:
        db.session.rollback()
        print(f"标记问题为已解决错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 上传图片（通用接口）
@app.route("/api/upload", methods=["POST"])
@cross_origin()
def upload_image():
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        if 'file' not in request.files:
            return jsonify(status=400, msg="没有上传文件")

        file = request.files['file']
        if file.filename == '':
            return jsonify(status=400, msg="没有选择文件")

        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify(status=400, msg="不支持的文件类型")

        # 生成文件名
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
        unique_id = str(uuid.uuid4())[:8]
        filename = f"issue_{user_phone}_{unique_id}.{ext}"

        # 保存路径
        upload_dir = get_frontend_image_path("issue")
        os.makedirs(upload_dir, exist_ok=True)

        # 保存文件
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # 生成访问URL
        image_url = f"/images/issue/{filename}"

        return jsonify(status=200, msg="上传成功", data={"url": image_url})

    except Exception as e:
        print(f"上传图片错误: {e}")
        return jsonify(status=500, msg="上传失败")


# 管理端：处理订单异常（管理员用）
@app.route("/api/manager/issues/<int:issue_id>/process", methods=["POST", "PUT", "OPTIONS"])
@cross_origin()
@admin_required
def process_order_issue(issue_id):
    """处理订单异常"""
    try:
        # 处理OPTIONS预检请求
        if request.method == 'OPTIONS':
            return jsonify(status=200)
            
        data = request.json
        if not data:
            return jsonify(status=400, msg="请求数据不能为空")
            
        # 获取处理信息（兼容前端格式）
        action = data.get('action', '')
        comment = data.get('comment', '')
        
        # 映射前端action到后端status
        status_mapping = {
            'processing': 'processing',
            'resolved': 'resolved', 
            'closed': 'closed'
        }
        
        status = status_mapping.get(action, 'processing')
        process_result = comment or f"状态更新为：{status}"
        solution = comment  # 使用comment作为solution
        
        if not action:
            return jsonify(status=400, msg="处理操作不能为空")
            
        # 验证问题是否存在
        issue_check = db.session.execute(
            text('SELECT issue_id, status FROM order_issue WHERE issue_id = :issue_id'),
            {'issue_id': issue_id}
        ).fetchone()
            
        if not issue_check:
            return jsonify(status=404, msg="订单异常不存在")
            
        # 更新问题状态（只更新status字段，因为表结构中没有其他处理字段）
        update_sql = """
            UPDATE order_issue 
            SET status = :status,
                updated_time = NOW()
            WHERE issue_id = :issue_id
        """
        
        admin_phone = request.current_admin_phone
        
        db.session.execute(text(update_sql), {
            'status': status,
            'issue_id': issue_id
        })
        
        # 添加处理记录
        followup_sql = """
            INSERT INTO issue_followup 
            (issue_id, followup_type, content, created_by)
            VALUES 
            (:issue_id, 'admin_process', :content, :admin_phone)
        """
        
        followup_content = f"管理员处理：{process_result}"
        if solution:
            followup_content += f"，解决方案：{solution}"
            
        db.session.execute(text(followup_sql), {
            'issue_id': issue_id,
            'content': followup_content,
            'admin_phone': admin_phone
        })
        
        db.session.commit()
        
        return jsonify(status=200, msg="处理成功")
        
    except Exception as e:
        db.session.rollback()
        print(f"处理订单异常错误: {e}")
        return jsonify(status=500, msg="系统错误")


# 管理端：获取所有订单异常（管理员用）
@app.route("/api/manager/issues", methods=["GET"])
@cross_origin()
@admin_required
def get_all_issues():
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))
        status = request.args.get('status')
        issue_type = request.args.get('issue_type')
        urgency = request.args.get('urgency')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # 构建查询条件
        where_clauses = ["1=1"]
        params = {}

        if status:
            where_clauses.append("status = :status")
            params["status"] = status

        if issue_type:
            where_clauses.append("issue_type = :issue_type")
            params["issue_type"] = issue_type

        if urgency:
            where_clauses.append("urgency = :urgency")
            params["urgency"] = urgency

        if start_date:
            where_clauses.append("DATE(created_time) >= :start_date")
            params["start_date"] = start_date

        if end_date:
            where_clauses.append("DATE(created_time) <= :end_date")
            params["end_date"] = end_date

        where_sql = " AND ".join(where_clauses)

        # 计算总数
        count_sql = f"SELECT COUNT(*) FROM order_issue WHERE {where_sql}"
        total = db.session.execute(text(count_sql), params).scalar() or 0

        # 获取数据
        offset = (page - 1) * size
        query_sql = f"""
            SELECT 
                oi.issue_id, oi.order_id, oi.user_phone, oi.issue_type, 
                oi.urgency, oi.title, oi.description, oi.image_url, 
                oi.expected_solution, oi.status, oi.created_time, oi.updated_time,
                u.username, o.shop_name
            FROM order_issue oi
            LEFT JOIN user u ON oi.user_phone = u.telephone
            LEFT JOIN oorder o ON oi.order_id = o.order_id
            WHERE {where_sql}
            ORDER BY 
                CASE oi.urgency 
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END,
                oi.created_time DESC
            LIMIT :limit OFFSET :offset
        """

        params.update({"limit": size, "offset": offset})
        issues = db.session.execute(text(query_sql), params).fetchall()

        # 格式化数据
        issues_list = []
        for issue in issues:
            issues_list.append({
                "issue_id": issue[0],
                "order_id": issue[1],
                "user_phone": issue[2],
                "issue_type": issue[3],
                "urgency": issue[4],
                "title": issue[5],
                "description": issue[6],
                "image_url": issue[7],
                "expected_solution": issue[8],
                "status": issue[9],
                "created_time": issue[10].strftime('%Y-%m-%d %H:%M:%S') if issue[10] else None,
                "updated_time": issue[11].strftime('%Y-%m-%d %H:%M:%S') if issue[11] else None,
                "username": issue[12],
                "shop_name": issue[13]
            })

        return jsonify(status=200, data={
            "issues": issues_list,
            "total": total,
            "page": page,
            "size": size
        })

    except Exception as e:
        print(f"获取所有订单异常错误: {e}")
        return jsonify(status=500, msg="系统错误")


# ==================== 地址管理接口 ====================

@app.route("/api/user/addresses", methods=["GET"])
@cross_origin()
def get_user_addresses():
    """获取用户所有收货地址"""
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        # 查询用户所有地址
        query = text("""
            SELECT 
                address_id, cons_name, cons_phone, address_label,
                province, city, district, street,
                is_default, status, created_time, updated_time
            FROM user_address 
            WHERE user_phone = :user_phone AND status = 1
            ORDER BY is_default DESC, updated_time DESC
        """)

        addresses_data = db.session.execute(query, {'user_phone': user_phone}).fetchall()

        addresses = []
        for row in addresses_data:
            address = {
                'address_id': row[0],
                'cons_name': row[1],
                'cons_phone': row[2],
                'address_label': row[3],
                'province': row[4],
                'city': row[5],
                'district': row[6],
                'street': row[7],
                'is_default': bool(row[8]),
                'status': row[9],
                'created_time': row[10].strftime('%Y-%m-%d %H:%M:%S') if row[10] else '',
                'updated_time': row[11].strftime('%Y-%m-%d %H:%M:%S') if row[11] else ''
            }
            addresses.append(address)

        return jsonify(status=200, data=addresses)

    except Exception as e:
        print(f"获取用户地址错误: {e}")
        return jsonify(status=500, msg="系统错误")


@app.route("/api/user/addresses", methods=["POST"])
@cross_origin()
def add_user_address():
    """添加新地址"""
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        data = request.json
        if not data:
            return jsonify(status=400, msg="请求数据不能为空")

        # 验证必填字段
        required_fields = ['cons_name', 'cons_phone', 'province', 'city', 'district', 'street']
        for field in required_fields:
            if not data.get(field):
                return jsonify(status=400, msg=f"{field}不能为空")

        cons_name = data.get('cons_name')
        cons_phone = data.get('cons_phone')
        address_label = data.get('address_label', 'home')
        province = data.get('province')
        city = data.get('city')
        district = data.get('district')
        street = data.get('street')
        is_default = data.get('is_default', 0)

        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', cons_phone):
            return jsonify(status=400, msg="手机号格式不正确")

        # 如果设置为默认地址，需要先取消其他默认地址
        if is_default:
            db.session.execute(
                text("UPDATE user_address SET is_default = 0 WHERE user_phone = :user_phone"),
                {'user_phone': user_phone}
            )

        # 插入新地址
        insert_query = text("""
            INSERT INTO user_address 
            (user_phone, cons_name, cons_phone, address_label, 
             province, city, district, street, is_default)
            VALUES 
            (:user_phone, :cons_name, :cons_phone, :address_label,
             :province, :city, :district, :street, :is_default)
        """)

        db.session.execute(insert_query, {
            'user_phone': user_phone,
            'cons_name': cons_name,
            'cons_phone': cons_phone,
            'address_label': address_label,
            'province': province,
            'city': city,
            'district': district,
            'street': street,
            'is_default': is_default
        })

        db.session.commit()

        return jsonify(status=200, msg="地址添加成功")

    except Exception as e:
        db.session.rollback()
        print(f"添加地址错误: {e}")
        return jsonify(status=500, msg="系统错误")


@app.route("/api/user/addresses/<int:address_id>", methods=["PUT"])
@cross_origin()
def update_user_address(address_id):
    """更新地址信息"""
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        data = request.json
        if not data:
            return jsonify(status=400, msg="请求数据不能为空")

        # 验证地址是否存在且属于当前用户
        check_query = text("""
            SELECT address_id FROM user_address 
            WHERE address_id = :address_id AND user_phone = :user_phone AND status = 1
        """)

        address_exists = db.session.execute(
            check_query,
            {'address_id': address_id, 'user_phone': user_phone}
        ).fetchone()

        if not address_exists:
            return jsonify(status=404, msg="地址不存在或无权修改")

        # 获取要更新的字段
        cons_name = data.get('cons_name')
        cons_phone = data.get('cons_phone')
        address_label = data.get('address_label')
        province = data.get('province')
        city = data.get('city')
        district = data.get('district')
        street = data.get('street')
        is_default = data.get('is_default')

        # 构建更新字段和参数
        update_fields = []
        params = {'address_id': address_id, 'user_phone': user_phone}

        if cons_name is not None:
            update_fields.append("cons_name = :cons_name")
            params['cons_name'] = cons_name

        if cons_phone is not None:
            if not re.match(r'^1[3-9]\d{9}$', cons_phone):
                return jsonify(status=400, msg="手机号格式不正确")
            update_fields.append("cons_phone = :cons_phone")
            params['cons_phone'] = cons_phone

        if address_label is not None:
            update_fields.append("address_label = :address_label")
            params['address_label'] = address_label

        if province is not None:
            update_fields.append("province = :province")
            params['province'] = province

        if city is not None:
            update_fields.append("city = :city")
            params['city'] = city

        if district is not None:
            update_fields.append("district = :district")
            params['district'] = district

        if street is not None:
            update_fields.append("street = :street")
            params['street'] = street

        if is_default is not None:
            # 如果设置为默认地址，需要先取消其他默认地址
            if is_default:
                db.session.execute(
                    text("UPDATE user_address SET is_default = 0 WHERE user_phone = :user_phone"),
                    {'user_phone': user_phone}
                )
            update_fields.append("is_default = :is_default")
            params['is_default'] = is_default

        if not update_fields:
            return jsonify(status=400, msg="没有需要更新的字段")

        # 构建更新语句
        update_query = text(f"""
            UPDATE user_address 
            SET {', '.join(update_fields)}, updated_time = NOW()
            WHERE address_id = :address_id AND user_phone = :user_phone
        """)

        result = db.session.execute(update_query, params)
        db.session.commit()

        if result.rowcount == 0:
            return jsonify(status=404, msg="地址不存在或更新失败")

        return jsonify(status=200, msg="地址更新成功")

    except Exception as e:
        db.session.rollback()
        print(f"更新地址错误: {e}")
        return jsonify(status=500, msg="系统错误")


@app.route("/api/user/addresses/<int:address_id>", methods=["DELETE"])
@cross_origin()
def delete_user_address(address_id):
    """删除地址（逻辑删除）"""
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        # 检查地址是否存在且属于当前用户
        check_query = text("""
            SELECT address_id, is_default FROM user_address 
            WHERE address_id = :address_id AND user_phone = :user_phone AND status = 1
        """)

        address_info = db.session.execute(
            check_query,
            {'address_id': address_id, 'user_phone': user_phone}
        ).fetchone()

        if not address_info:
            return jsonify(status=404, msg="地址不存在或无权删除")

        # 如果是默认地址，不能直接删除（可以先设置其他地址为默认）
        if address_info.is_default:
            # 检查是否有其他地址
            other_addresses_query = text("""
                SELECT address_id FROM user_address 
                WHERE user_phone = :user_phone AND address_id != :address_id AND status = 1
                LIMIT 1
            """)

            other_address = db.session.execute(
                other_addresses_query,
                {'user_phone': user_phone, 'address_id': address_id}
            ).fetchone()

            if not other_address:
                return jsonify(status=400, msg="不能删除唯一的默认地址，请先添加新地址")

        # 逻辑删除（将状态设为0）
        delete_query = text("""
            UPDATE user_address 
            SET status = 0, is_default = 0, updated_time = NOW()
            WHERE address_id = :address_id AND user_phone = :user_phone
        """)

        result = db.session.execute(delete_query, {
            'address_id': address_id,
            'user_phone': user_phone
        })

        db.session.commit()

        if result.rowcount == 0:
            return jsonify(status=404, msg="地址删除失败")

        # 如果删除的是默认地址，将最近更新的地址设为默认
        if address_info.is_default:
            set_new_default_query = text("""
                UPDATE user_address 
                SET is_default = 1 
                WHERE address_id = (
                    SELECT address_id FROM user_address 
                    WHERE user_phone = :user_phone AND status = 1
                    ORDER BY updated_time DESC 
                    LIMIT 1
                )
            """)
            db.session.execute(set_new_default_query, {'user_phone': user_phone})
            db.session.commit()

        return jsonify(status=200, msg="地址删除成功")

    except Exception as e:
        db.session.rollback()
        print(f"删除地址错误: {e}")
        return jsonify(status=500, msg="系统错误")


@app.route("/api/user/addresses/<int:address_id>/set-default", methods=["PATCH"])
@cross_origin()
def set_default_address(address_id):
    """设置默认地址"""
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        # 检查地址是否存在且属于当前用户
        check_query = text("""
            SELECT address_id FROM user_address 
            WHERE address_id = :address_id AND user_phone = :user_phone AND status = 1
        """)

        address_exists = db.session.execute(
            check_query,
            {'address_id': address_id, 'user_phone': user_phone}
        ).fetchone()

        if not address_exists:
            return jsonify(status=404, msg="地址不存在或无权操作")

        try:
            # 开启事务
            # 1. 将所有地址设为非默认
            db.session.execute(
                text("UPDATE user_address SET is_default = 0 WHERE user_phone = :user_phone"),
                {'user_phone': user_phone}
            )

            # 2. 将指定地址设为默认
            set_default_query = text("""
                UPDATE user_address 
                SET is_default = 1, updated_time = NOW()
                WHERE address_id = :address_id AND user_phone = :user_phone
            """)

            result = db.session.execute(set_default_query, {
                'address_id': address_id,
                'user_phone': user_phone
            })

            db.session.commit()

            if result.rowcount == 0:
                return jsonify(status=404, msg="设置默认地址失败")

            return jsonify(status=200, msg="设置默认地址成功")

        except Exception as e:
            db.session.rollback()
            raise e

    except Exception as e:
        print(f"设置默认地址错误: {e}")
        return jsonify(status=500, msg="系统错误")


@app.route("/api/user/default-address", methods=["GET"])
@cross_origin()
def get_default_address():
    """获取用户的默认地址"""
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        query = text("""
            SELECT 
                address_id, cons_name, cons_phone, address_label,
                province, city, district, street,
                is_default, status, created_time, updated_time
            FROM user_address 
            WHERE user_phone = :user_phone AND is_default = 1 AND status = 1
            LIMIT 1
        """)

        address_data = db.session.execute(query, {'user_phone': user_phone}).fetchone()

        if not address_data:
            return jsonify(status=404, msg="未设置默认地址")

        address = {
            'address_id': address_data[0],
            'cons_name': address_data[1],
            'cons_phone': address_data[2],
            'address_label': address_data[3],
            'province': address_data[4],
            'city': address_data[5],
            'district': address_data[6],
            'street': address_data[7],
            'is_default': bool(address_data[8]),
            'status': address_data[9],
            'created_time': address_data[10].strftime('%Y-%m-%d %H:%M:%S') if address_data[10] else '',
            'updated_time': address_data[11].strftime('%Y-%m-%d %H:%M:%S') if address_data[11] else ''
        }

        return jsonify(status=200, data=address)

    except Exception as e:
        print(f"获取默认地址错误: {e}")
        return jsonify(status=500, msg="系统错误")


# ==================== 地址验证相关接口 ====================

@app.route("/api/user/addresses/validate-phone", methods=["POST"])
@cross_origin()
def validate_phone():
    """验证手机号格式"""
    try:
        data = request.json
        phone = data.get('phone', '')

        if not phone:
            return jsonify(status=400, msg="手机号不能为空")

        if re.match(r'^1[3-9]\d{9}$', phone):
            return jsonify(status=200, valid=True, msg="手机号格式正确")
        else:
            return jsonify(status=200, valid=False, msg="手机号格式不正确")

    except Exception as e:
        print(f"验证手机号错误: {e}")
        return jsonify(status=500, msg="系统错误")


@app.route("/api/user/addresses/count", methods=["GET"])
@cross_origin()
def get_address_count():
    """获取用户地址数量"""
    try:
        user_phone = get_token_phone(request.headers.get('token'))
        if not user_phone:
            return jsonify(status=401, msg="用户未登录")

        query = text("""
            SELECT COUNT(*) as address_count
            FROM user_address 
            WHERE user_phone = :user_phone AND status = 1
        """)

        result = db.session.execute(query, {'user_phone': user_phone}).fetchone()

        address_count = result[0] if result else 0

        return jsonify(status=200, data={"address_count": address_count})

    except Exception as e:
        print(f"获取地址数量错误: {e}")
        return jsonify(status=500, msg="系统错误")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
    with app.app_context():
        init_review_likes_cache()
    # 开启了debug模式
