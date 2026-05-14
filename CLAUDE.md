# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Food delivery management system (外卖餐饮管理系统) — a university database course project. Vue.js 2.6 frontend + Flask 2.3 backend + MySQL 5.7 database. Three roles: regular users, merchants, and admins.

## Requirements

- **Node.js** >= 14.x
- **Python** >= 3.8
- **MySQL** >= 5.7
- **Redis** >= 5.0 (optional, for caching — falls back to in-memory dict if unavailable)

## Commands

### Backend (后端代码/)

```bash
# Install dependencies
cd 后端代码
pip install -r requirements.txt

# Start dev server (runs on http://localhost:5000)
python app.py
```

### Frontend (前端代码/sjk/)

```bash
cd 前端代码/sjk
npm install
npm run serve      # Dev server on http://localhost:8080
npm run build      # Production build to dist/
npm run lint       # ESLint
```

### Database

```bash
# Import schema and seed data
mysql -u root -p dba < 数据库代码/dba.sql

# Migrate plaintext passwords to bcrypt hashes (one-time)
cd 后端代码
python migrate_passwords.py
```

### Production deployment (backend)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Frontend: `npm run build` produces `dist/` for static hosting (Nginx, etc.).

## Architecture

### Backend (`app.py` — monolithic, ~5900 lines)

All models, routes, and business logic live in a single file. The `models/`, `routes/`, and `services/` directories exist but are empty — they are intended refactoring targets.

- **`config.py`** — Database URI (`mysql+pymysql://`), Redis, CORS, and session config via `BaseConfig` class.
- **`auth.py`** — JWT token encode/decode using PyJWT (HS256, 1-day expiry). Tokens are passed in the `token` request header.
- **`utils/password_util.py`** — bcrypt password hashing/verification. A duplicate `PasswordUtil` class also exists inline in `app.py` (the inline version is the one actually used at runtime).
- **`migrate_passwords.py`** — Standalone script to hash existing plaintext passwords in the database.

**Key patterns in app.py:**
- Raw SQL via `db.session.execute(text(...))` — there are only 2 ORM models (`Review`, `ReviewLike`). Everything else uses string SQL.
- `get_token_phone(token)` helper extracts the user's phone from a JWT token.
- `admin_required` / `super_admin_required` decorators enforce role-based access (role=1 for admin, is_super=1 for super admin).
- Redis is used for caching but falls back to an in-memory dict if Redis is unavailable.
- Image uploads are saved directly into the frontend's `public/images/` directory, with Chinese filenames converted to pinyin.
- A DeepSeek API key is hardcoded (used for AI recommendation features at `/api/recommend/*`).

**API route groups:**
| Prefix | Role | Purpose |
|---|---|---|
| `/api/user/*` | All | Login, register, profile, orders, addresses, cart, reviews |
| `/api/shops/*` | Public | Shop listing, dishes, reviews |
| `/api/cart/*` | User | Shopping cart CRUD |
| `/api/order/*` | User | Place orders from cart |
| `/api/manager/*` | Admin | User/shop/dispatcher/delivery management, order processing |
| `/api/manage/*` | Admin | Admin profile |
| `/api/shop/owner/*` | Merchant | Shop & dish CRUD, order status, sales statistics |
| `/api/review/*` | All | Submit reviews, like reviews |
| `/api/recommend/*` | Public | AI-powered shop/dish/hot-review recommendations |

### Frontend (Vue.js 2.6 + Element UI)

- **Entry**: `src/main.js` — mounts Vue, installs Element UI, sets up Axios interceptors (separate `admin_token` for admin API calls).
- **Router** (`src/router/index.js`) — History mode. Core routes: `/login`, `/user` (user dashboard), `/manage` (admin dashboard), `/store` (merchant dashboard), `/shops`, `/shop/:id`, `/cart`.
- **API** (`src/api/index.js`) — Axios instance with dynamic base URL (auto-detects `localhost` vs LAN IP). All API calls use this instance.
- **Views** are organized by role:
  - `src/views/auth/` — Login/Register
  - `src/views/user/` — User profile, order lists (unsent/sending/finished), address management
  - `src/views/admin/` — Dashboard, shop/user/dispatcher management, order/delivery/issue management
  - `src/views/store/` — Shop/dish management, order processing, sales analytics
  - `src/views/public/` — Shop list, shop detail, cart, recommendations
- **Components** (`src/components/`) — Shared order/delivery/user widgets used across admin views.
- `vue.config.js` binds dev server to `0.0.0.0:8080` (LAN-accessible). No API proxy configured — the frontend makes direct CORS requests to port 5000.

### Database (MySQL 5.7, `dba` schema)

16 tables: `user`, `shop`, `dish`, `cart`, `oorder`, `order_detail`, `orderway`, `delivery`, `dispatcher`, `review`, `review_like`, `order_issue`, `issue_followup`, `user_address`, `user_msg`.

Key relationships:
- `user.telephone` is the primary user identifier (used as FK throughout)
- `shop` → `dish` (1:N), `shop` → `oorder` (1:N)
- `oorder` → `order_detail` (1:N, each detail references a `dish`)
- `oorder` → `delivery` (1:1, references `dispatcher`)
- `review` can target a `shop` or a `dish` (controlled by `review_type`)
- `order_issue` → `issue_followup` (1:N)

### Configuration notes

- `config.py` contains hardcoded DB credentials (`root/root`) and Redis password. The DeepSeek API key is embedded in `app.py` line ~153. Do not commit these to public repos.
- CORS is permissive in dev — allows all localhost/192.168 origins across many ports.
- Frontend API base URL defaults to `http://localhost:5000` for local dev, or `http://192.168.0.100:5000` for LAN access from mobile devices.
- The README suggests a `.env` file pattern for DB/JWT/Redis config, but the actual code reads from `config.py` directly — no `.env` loading is implemented.

### Key dependencies

- **pypinyin** — converts Chinese filenames to pinyin for image uploads
- **bcrypt** — password hashing (used via inline `PasswordUtil` in `app.py`, not `utils/password_util.py`)
- **PyJWT** — JWT token encode/decode (HS256, 1-day expiry)
- **ECharts** — used in merchant dashboard for sales data visualization
