# WTO模拟谈判系统 - 部署指南

本文档提供了WTO模拟谈判系统的多种部署方式，包括本地部署、Docker部署和云服务器部署的完整指南。

🔥 **重要更新**: v3.1版本开始支持环境变量配置，保护敏感信息安全。请务必配置环境变量后再部署！

---

## 🚀 快速部署

### 环境要求
- Python 3.7+
- MongoDB 4.0+
- 8GB+ RAM（用于PDF文本提取）
- Git

### 主要依赖
```txt
Flask==2.3.3              # Web框架
pymongo==4.5.0            # MongoDB驱动
PyPDF2==3.0.1             # PDF文本提取
python-docx==1.1.2        # Word文档提取
reportlab==4.0.7          # PDF生成
jieba==0.42.1             # 中文分词
scikit-learn==1.4.1       # 文本相似度分析
requests==2.31.0          # HTTP请求
python-dotenv==1.0.0      # 环境变量管理
Flask-SocketIO==5.3.6     # WebSocket支持
Flask-Login==0.6.3        # 用户认证
Flask-JWT-Extended==4.5.3 # JWT认证
```

---

## ⚙️ 环境变量配置

⚠️ **重要**: v3.1版本开始使用环境变量管理敏感配置信息。部署前必须配置环境变量！

### 1. 复制模板文件
```bash
cp .env.example .env
```

### 2. 编辑配置文件
编辑 `.env` 文件，填入您的实际配置信息：

```bash
# ========================================
# 大模型API配置（必需）
# ========================================
LLM_API_KEY=sk-your-actual-api-key-here
LLM_API_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
LLM_MODEL=qwen-turbo

# ========================================
# Flask应用配置（必需）
# ========================================
FLASK_SECRET_KEY=your-flask-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES_HOURS=24

# ========================================
# 数据库配置（必需）
# ========================================
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=countriesDB

# ========================================
# 应用运行配置（可选）
# ========================================
DEBUG=True
HOST=0.0.0.0
PORT=5000
```

🔐 **安全提醒**: `.env` 文件已被 `.gitignore` 保护，不要提交到版本控制系统！

### 3. 验证配置
```bash
# 验证环境变量是否正确加载
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('LLM_API_KEY:', '已配置' if os.getenv('LLM_API_KEY', '').startswith('sk-') else '未配置')
print('MongoDB:', os.getenv('MONGODB_URI', '未配置'))
print('Flask Secret:', '已配置' if os.getenv('FLASK_SECRET_KEY') else '未配置')
"
```

---

## 💻 本地部署（推荐新手）

### 1. 克隆项目
```bash
git clone <repository-url>
cd project_new
```

### 2. 安装Python依赖
```bash
pip install -r requirements.txt
```

如果安装速度慢，可以使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 3. 配置环境变量
```bash
# 复制模板文件
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用其他编辑器
# 填入您的实际配置信息（参考上文环境变量配置部分）
```

### 4. 启动MongoDB
```bash
# Windows
net start MongoDB

# macOS/Linux
sudo systemctl start mongod

# 验证MongoDB是否启动
mongosh --eval "db.adminCommand('ismaster')"
```

### 5. 验证配置
```bash
# 验证环境变量配置
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('=== 配置验证 ===')
print('LLM_API_KEY:', '✅ 已配置' if os.getenv('LLM_API_KEY', '').startswith('sk-') else '❌ 未配置')
print('MongoDB:', '✅ 已配置' if os.getenv('MONGODB_URI') else '❌ 未配置')
print('Flask Secret:', '✅ 已配置' if os.getenv('FLASK_SECRET_KEY') else '❌ 未配置')
print('JWT Secret:', '✅ 已配置' if os.getenv('JWT_SECRET_KEY') else '❌ 未配置')
"
```

### 6. 启动应用
```bash
python run.py
```

系统将启动在 http://127.0.0.1:5000

### 7. 访问系统
- **系统主页**: http://127.0.0.1:5000
- **主席控制台**: http://127.0.0.1:5000/chairman-selection
- **与会国门户**: http://127.0.0.1:5000/country-portal
- **API文档**: http://127.0.0.1:5000/api/docs

如果端口5000被占用，修改`.env`文件中的`PORT`变量：
```bash
PORT=5001
```

---

## 🐳 Docker部署（推荐生产环境）

### 1. 环境准备
- Docker
- Docker Compose

### 2. 克隆项目
```bash
git clone <repository-url>
cd project_new
```

### 3. 配置环境变量
```bash
# 复制模板文件
cp .env.example .env

# 编辑配置文件（重要！）
nano .env  # 或使用其他编辑器
# 填入您的实际配置信息，特别注意：
# - LLM_API_KEY: 您的阿里云通义千问API密钥
# - FLASK_SECRET_KEY: 随机生成的密钥字符串
# - JWT_SECRET_KEY: 随机生成的JWT密钥字符串
```

### 4. 启动服务
```bash
# 启动所有服务（包含MongoDB和应用）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看启动日志
docker-compose logs -f wto_app
```

### 5. 验证部署
```bash
# 检查应用容器是否正常运行
docker-compose ps

# 检查应用日志
docker-compose logs wto_app

# 测试API连接（在容器内）
docker-compose exec wto_app python test_declaration_api.py
```

### 6. 访问系统
- **系统主页**: http://localhost:5000
- **主席控制台**: http://localhost:5000/chairman-selection
- **与会国门户**: http://localhost:5000/country-portal
- **API文档**: http://localhost:5000/api/docs
- **Nginx代理**: http://localhost:80 (如果配置了Nginx)

### 7. 管理服务
```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 更新代码后重新构建
docker-compose up -d --build

# 查看实时日志
docker-compose logs -f

# 查看特定服务的日志
docker-compose logs -f wto_app
docker-compose logs -f mongo

# 进入容器调试
docker-compose exec wto_app bash
```

### 8. Docker配置说明

查看`docker-compose.yml`文件：
```yaml
version: '3.8'
services:
  wto_app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      # 文件上传目录
      - ./app/static/uploads:/app/app/static/uploads
      # 国家旗帜图片
      - ./app/static/flags:/app/app/static/flags
    environment:
      # 从.env文件加载所有环境变量
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_API_URL=${LLM_API_URL}
      - LLM_MODEL=${LLM_MODEL}
      - FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - MONGODB_URI=${MONGODB_URI}
      - DATABASE_NAME=${DATABASE_NAME}
      - DEBUG=${DEBUG}
      - PORT=${PORT}
    depends_on:
      - mongo
    restart: unless-stopped

  mongo:
    image: mongo:5.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped

volumes:
  mongodb_data:
```

**环境变量说明**：
- 所有环境变量都从`.env`文件自动加载到Docker容器中
- 使用`.env`文件而非直接在`docker-compose.yml`中设置敏感信息
- 容器重启策略设置为`unless-stopped`，确保服务稳定性
- MongoDB使用5.0版本，提供更好的性能和安全性

---

## ☁️ 云服务器部署

### 1. 服务器环境准备
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip mongodb nginx git

# CentOS/RHEL
sudo yum install python3 python3-pip mongodb-org nginx git
```

### 2. 部署应用
```bash
# 克隆项目
git clone <repository-url>
cd project_new

# 安装Python依赖
pip3 install -r requirements.txt

# 启动MongoDB服务
sudo systemctl start mongod
sudo systemctl enable mongod

# 验证MongoDB状态
sudo systemctl status mongod
```

### 3. 配置环境变量
```bash
# 复制模板文件
cp .env.example .env

# 编辑配置文件（重要！）
nano .env  # 或使用其他编辑器
# 填入您的实际配置信息：
# - LLM_API_KEY: 阿里云通义千问API密钥
# - FLASK_SECRET_KEY: 随机生成的密钥字符串
# - JWT_SECRET_KEY: 随机生成的JWT密钥字符串
# - MONGODB_URI: 数据库连接字符串
```

### 4. 验证配置
```bash
# 验证环境变量配置
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('=== 云服务器配置验证 ===')
print('LLM_API_KEY:', '✅ 已配置' if os.getenv('LLM_API_KEY', '').startswith('sk-') else '❌ 未配置')
print('MongoDB:', '✅ 已配置' if os.getenv('MONGODB_URI') else '❌ 未配置')
print('Flask Secret:', '✅ 已配置' if os.getenv('FLASK_SECRET_KEY') else '❌ 未配置')
print('JWT Secret:', '✅ 已配置' if os.getenv('JWT_SECRET_KEY') else '❌ 未配置')
"
```

### 5. 使用systemd管理服务
创建服务文件 `/etc/systemd/system/wto-app.service`：
```ini
[Unit]
Description=WTO Negotiation System
After=network.target mongodb.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project_new

# 环境变量配置
Environment=PATH=/usr/bin:/usr/local/bin
EnvironmentFile=/path/to/project_new/.env

# 启动命令
ExecStart=/usr/bin/python3 run.py
ExecReload=/bin/kill -HUP $MAINPID

# 重启策略
Restart=always
RestartSec=3

# 资源限制
LimitNOFILE=65536
MemoryLimit=512M

[Install]
WantedBy=multi-user.target
```

**服务配置说明**：
- `EnvironmentFile=/path/to/project_new/.env`: 自动加载.env文件中的环境变量
- `ExecReload`: 支持服务重载配置
- `LimitNOFILE=65536`: 增加文件描述符限制，支持大量并发连接
- `MemoryLimit=512M`: 限制内存使用，防止内存泄漏

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start wto-app
sudo systemctl enable wto-app
```

### 6. 安全配置
```bash
# 防火墙设置
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable

# SSL证书（推荐）
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# 备份配置文件
cp .env .env.backup
```

### 7. 日志监控
```bash
# 查看应用日志
sudo journalctl -u wto-app -f

# 查看错误日志
sudo journalctl -u wto-app -p err..alert

# 系统状态监控
sudo systemctl status wto-app
```

---

## ⚙️ 配置说明

### 环境变量配置（v3.1新特性）

从v3.1版本开始，系统使用环境变量管理所有配置信息，替代了硬编码方式。

#### .env文件配置
```bash
# ========================================
# 大模型API配置（必需）
# ========================================
LLM_API_KEY=sk-your-actual-api-key-here
LLM_API_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
LLM_MODEL=qwen-turbo

# ========================================
# Flask应用配置（必需）
# ========================================
FLASK_SECRET_KEY=your-flask-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES_HOURS=24

# ========================================
# 数据库配置（必需）
# ========================================
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=countriesDB

# ========================================
# 应用运行配置（可选）
# ========================================
DEBUG=False
HOST=0.0.0.0
PORT=5000
```

#### 传统环境变量方式（已弃用）
```bash
# 旧方式（仅供参考）
export LLM_API_KEY="your-api-key"
export MONGODB_URI="mongodb://localhost:27017/"
export FLASK_SECRET_KEY="your-secret-key"
```

> **⚠️ 重要**: 推荐使用`.env`文件方式，更加安全和便于管理。

### 数据库初始化
```bash
# 连接MongoDB
mongosh

# 创建数据库
use countriesDB

# 导入国家数据（如果有）
mongoimport --db countriesDB --collection countries_lc --file countries.json
```

### Nginx配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/project_new/app/static/;
        expires 30d;
    }
}
```

---

## 📊 监控和维护

### 日志管理
```bash
# 查看应用日志
tail -f app.log

# 查看Docker日志
docker-compose logs -f wto_app

# 查看系统日志
journalctl -u wto-app -f
```

### 性能监控
```bash
# 查看系统资源
htop
df -h
free -h

# 查看网络连接
netstat -tulpn | grep :5000
```

### 备份策略
```bash
# 备份MongoDB数据
mongodump --db countriesDB --out /backup/$(date +%Y%m%d)

# 备份上传文件
tar -czf /backup/uploads_$(date +%Y%m%d).tar.gz app/static/uploads/

# 恢复数据
mongorestore --db countriesDB /backup/20231201/countriesDB/
```

---

## 🔒 安全配置

### 防火墙设置
```bash
# Ubuntu/Debian
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

### SSL证书配置
```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 数据库安全
```bash
# 创建数据库用户
mongosh
use admin
db.createUser({
  user: "admin",
  pwd: "secure-password",
  roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase"]
})

# 启用认证
sudo nano /etc/mongod.conf
# 添加:
security:
  authorization: enabled
```

---

## 🚨 故障排除

### 部署故障诊断

#### MongoDB连接失败
```bash
# 检查MongoDB服务状态
sudo systemctl status mongod

# 检查端口是否被占用
sudo netstat -tulpn | grep 27017

# 重启MongoDB
sudo systemctl restart mongod

# 检查日志
sudo tail -f /var/log/mongodb/mongod.log
```

#### 端口被占用
```bash
# 查看端口占用
sudo lsof -i :5000

# 杀死进程
sudo kill -9 <PID>

# 或者修改端口
# 编辑 run.py 中的端口配置
```

#### 依赖包问题
```bash
# 清理缓存
pip cache purge

# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 权限问题
```bash
# 修复文件权限
sudo chown -R www-data:www-data /path/to/project_new
sudo chmod -R 755 /path/to/project_new

# 创建上传目录
sudo mkdir -p app/static/uploads
sudo chmod 777 app/static/uploads
```

#### Docker部署问题
```bash
# 查看容器日志
docker-compose logs -f wto_app

# 重建容器
docker-compose down
docker-compose up -d --build

# 检查资源使用
docker stats
```

### 常见问题

#### Q1: MongoDB连接失败？
```bash
# 检查MongoDB是否启动
mongosh

# Windows启动MongoDB
net start MongoDB

# 检查端口27017是否被占用
netstat -an | findstr 27017

# 检查MongoDB服务状态（Linux）
sudo systemctl status mongod

# 查看MongoDB日志（Linux）
sudo tail -f /var/log/mongodb/mongod.log
```

#### Q2: 依赖包安装失败？
```bash
# 清理pip缓存
pip cache purge

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 强制重新安装
pip install -r requirements.txt --force-reinstall

# 安装特定版本
pip install Flask==2.3.3 pymongo==4.5.0
```

#### Q3: 端口5000被占用？
```bash
# 查看端口占用
sudo lsof -i :5000

# 杀死进程
sudo kill -9 <PID>

# 或者修改端口
# 编辑 run.py 末尾：
app.run(debug=True, port=5001)  # 改为其他端口
```

#### Q4: Docker部署失败？
```bash
# 检查Docker服务
sudo systemctl status docker

# 清理Docker缓存
docker system prune -a

# 重建容器
docker-compose down
docker-compose up -d --build

# 查看详细日志
docker-compose logs -f wto_app
```

#### Q5: 上传文件权限问题？
```bash
# 创建上传目录
sudo mkdir -p app/static/uploads
sudo chmod 777 app/static/uploads

# 修复项目权限
sudo chown -R www-data:www-data /path/to/project_new
sudo chmod -R 755 /path/to/project_new
```

#### Q6: Nginx配置问题？
```bash
# 检查Nginx配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx

# 查看Nginx日志
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

#### Q7: 数据库备份和恢复？
```bash
# 备份MongoDB数据
mongodump --db countriesDB --out /backup/$(date +%Y%m%d)

# 备份上传文件
tar -czf /backup/uploads_$(date +%Y%m%d).tar.gz app/static/uploads/

# 恢复数据
mongorestore --db countriesDB /backup/20231201/countriesDB/
```

---

## 🔄 更新部署

### 代码更新
```bash
# 拉取最新代码
git pull origin main

# 重新安装依赖（如果有变化）
pip install -r requirements.txt

# 重启服务
# 本地部署
pkill -f "python run.py"
python run.py

# Docker部署
docker-compose up -d --build

# systemd服务
sudo systemctl restart wto-app
```

### 数据库迁移
```bash
# 备份当前数据
mongodump --db countriesDB --out /backup/pre_update

# 执行迁移脚本（如果有）
python migration_script.py

# 验证数据完整性
python test_data_integrity.py
```

---

## 📞 技术支持

如果遇到部署问题，请：

1. 查看日志文件获取详细错误信息
2. 检查系统资源使用情况
3. 确认网络连接和防火墙设置
4. 参考项目文档和常见问题
5. 提交Issue到项目仓库

---

## 📄 文档信息

- **文档版本**: v1.0
- **最后更新**: 2024-10-25
- **适用版本**: WTO模拟谈判系统 v3.0
- **维护者**: 开发团队

---

**部署成功！** 🎉 现在您可以开始使用WTO模拟谈判系统了。
