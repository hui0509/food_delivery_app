># 🍔 外卖餐饮管理系统

> 一个功能完整的外卖餐饮管理全栈项目，基于Vue.js + Flask + MySQL技术栈开发

[![Vue.js](https://img.shields.io/badge/Vue.js-2.6.14-green)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-blue)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-5.7-orange)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## ✨ 项目简介

这是一个功能完整的外卖餐饮管理系统，支持多角色用户（普通用户、商家、管理员），实现了从浏览店铺、下单购买、支付配送到评价反馈的完整业务流程。

### 🎯 核心功能

| 用户类型 | 主要功能 |
|---------|---------|
| 👤 普通用户 | 浏览店铺、下单购买、评价、个人中心 |
| 🏪 商家用户 | 店铺管理、菜品管理、订单处理、数据统计 |
| 👨‍💼 管理员 | 用户管理、店铺审核、系统监控、数据报表 |

## 🚀 快速开始

### 环境要求

- **Node.js** >= 14.x
- **Python** >= 3.8
- **MySQL** >= 5.7
- **Redis** >= 5.0 (可选，用于缓存)

### 1. 克隆项目

```bash
git clone https://github.com/hui0509/food_delivery_app.git
cd food_delivery_app
```

### 2. 数据库设置

#### 创建数据库
```sql
CREATE DATABASE dba CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 导入数据表结构
```bash
# 进入数据库代码目录
cd 数据库代码

# 使用MySQL客户端导入
mysql -u root -p dba < dba.sql
```

### 3. 后端服务启动

#### 安装Python依赖
```bash
cd 后端代码
pip install -r requirements.txt
```

#### 配置环境变量
创建 `.env` 文件：
```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=dba

# Redis配置（可选）
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT密钥
JWT_SECRET=your_jwt_secret_key
```

#### 启动后端服务
```bash
# 开发环境
python app.py

# 或者使用优化版本
python app_optimized.py
```

后端服务将在 `http://localhost:5000` 启动

### 4. 前端服务启动

#### 安装Node.js依赖
```bash
cd 前端代码/sjk
npm install
```

#### 配置API地址
编辑 `src/api/index.js`，确保API地址指向后端服务：
```javascript
const baseURL = process.env.NODE_ENV === 'production' 
  ? 'http://your-production-domain.com:5000' 
  : 'http://localhost:5000';
```

#### 启动前端服务
```bash
npm run serve
```

前端服务将在 `http://localhost:8080` 启动

## 📱 功能演示

### 用户端功能
- **首页浏览**：热门店铺、推荐菜品
- **店铺详情**：菜品展示、用户评价
- **购物车**：添加商品、数量调整
- **下单支付**：地址选择、订单确认
- **订单管理**：历史订单、订单状态
- **个人中心**：个人信息、收货地址

![image](https://github.com/user-attachments/assets/0e351ff7-3489-4efd-879e-9d4aac793b93)
<img width="2511" height="1352" alt="image" src="https://github.com/user-attachments/assets/5c795f94-c153-4dd3-9f5c-65c963ef1d7f" />

### 商家端功能
- **店铺管理**：基本信息、营业状态
- **菜品管理**：添加菜品、价格调整
- **订单处理**：接单、备餐、发货
- **数据统计**：销售数据、用户评价

<img width="2548" height="1388" alt="image" src="https://github.com/user-attachments/assets/a1a4c3aa-132e-4bf5-84c4-475b98dc5cc7" />
<img width="2552" height="1409" alt="image" src="https://github.com/user-attachments/assets/8ce70a46-22ab-4cb6-ad3b-1a9b62d75b09" />


### 管理员功能
- **用户管理**：用户信息、权限设置
- **店铺审核**：新店铺审核、状态管理
- **系统监控**：系统状态、性能监控
<img width="2549" height="1375" alt="image" src="https://github.com/user-attachments/assets/09b3dc4e-03f2-4ea0-b46d-ec2171b8cdfc" />
<img width="2551" height="1341" alt="image" src="https://github.com/user-attachments/assets/f58e279e-b02b-4114-9018-45cf9776f798" />


## 🏗️ 项目结构

```
food-delivery-system/
├── 前端代码/                 # Vue.js前端项目
│   └── sjk/
│       ├── public/           # 静态资源
│       ├── src/
│       │   ├── api/          # API接口
│       │   ├── components/   # 公共组件
│       │   ├── views/        # 页面组件
│       │   ├── router/      # 路由配置
│       │   └── App.vue       # 根组件
│       └── package.json      # 项目配置
├── 后端代码/                 # Flask后端项目
│   ├── app.py               # 主应用文件
│   ├── app_optimized.py     # 优化版本
│   ├── auth.py              # 认证模块
│   ├── config.py            # 配置文件
│   ├── utils/               # 工具函数
│   └── requirements.txt     # Python依赖
├── 数据库代码/              # 数据库相关
│   └── dba.sql              # 数据库表结构
└── 课程报告/               # 项目文档
    ├── README.md           # 项目说明（本文件）
    └── 外卖餐饮管理系统课程报告.md  # 详细技术报告
```

## 🔧 配置说明

### 数据库配置
编辑 `后端代码/config.py`：
```python
class BaseConfig:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost:3306/dba'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### 前端配置
编辑 `前端代码/sjk/vue.config.js`：
```javascript
module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
}
```

## 🚀 部署指南

### 开发环境部署
1. 按照"快速开始"步骤操作
2. 确保所有服务正常启动
3. 访问 `http://localhost:8080` 测试

### 生产环境部署

#### 后端部署
```bash
# 使用Gunicorn部署
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 前端部署
```bash
# 构建生产版本
npm run build

# 部署到Nginx
# 将dist目录内容复制到Nginx的html目录
```

#### Nginx配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端API代理
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🐛 常见问题

### Q: 前端访问后端API出现跨域错误
A: 确保后端CORS配置正确，或使用前端代理配置

### Q: 数据库连接失败
A: 检查数据库服务是否启动，配置信息是否正确

### Q: 图片上传失败
A: 检查上传目录权限，确保有写入权限

### Q: JWT Token验证失败
A: 检查Token是否过期，或重新登录获取新Token

## 🔄 更新日志

### v1.0.0 (2026-02-13)
- ✅ 完成基础功能开发
- ✅ 实现多角色权限系统
- ✅ 优化前后端性能
- ✅ 完善项目文档

## 🤝 贡献指南

我们欢迎任何形式的贡献！

### 如何贡献
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 开发规范
- 遵循代码规范（ESLint + PEP8）
- 提交信息清晰明确
- 新功能需要包含测试用例
- 更新相关文档



## 📞 联系方式

- **项目主页**: https://github.com/hui0509/food_delivery_app
- **问题反馈**: https://github.com/hui0509/food_delivery_app/issues


## 🙏 致谢

感谢以下开源项目提供的技术支持：
- [HEU-Database-course-design]
  (https://github.com/wfloveiu/HEU-Database-course-design) - 数据库课程设计项目
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Flask](https://flask.palletsprojects.com/) - Python微框架
- [Element UI](https://element.eleme.io/) - Vue.js组件库
- [MySQL](https://www.mysql.com/) - 关系型数据库

---

⭐ 如果这个项目对你有帮助，请给我们一个Star！
