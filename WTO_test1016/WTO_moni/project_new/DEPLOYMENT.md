# WTO模拟谈判系统 - 部署指南

本文档提供了WTO模拟谈判系统的多种部署方式，包括本地部署、Docker部署和云服务器部署。

## 🚀 快速部署

### 方式一：本地部署（推荐新手）

#### 1. 环境准备
- Python 3.7+
- MongoDB 4.0+
- Git

#### 2. 安装步骤
```bash
# 克隆项目
git clone <repository-url>
cd project_new

# 安装依赖
pip install -r requirements.txt

# 启动MongoDB
# Windows
net start MongoDB
# macOS/Linux
sudo systemctl start mongod

# 启动应用
python start.py
```

#### 3. 访问系统
打开浏览器访问: http://localhost:5000

### 方式二：Docker部署（推荐生产环境）

#### 1. 环境准备
- Docker
- Docker Compose

#### 2. 一键部署
```bash
# 克隆项目
git clone <repository-url>
cd project_new

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f wto_app
```

#### 3. 访问系统
- 直接访问: http://localhost:5000
- 通过Nginx: http://localhost:80

#### 4. 管理服务
```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 更新代码后重新构建
docker-compose up -d --build
```

### 方式三：云服务器部署

#### 1. 服务器环境准备
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip mongodb nginx

# CentOS/RHEL
sudo yum install python3 python3-pip mongodb-org nginx
```

#### 2. 部署应用
```bash
# 克隆项目
git clone <repository-url>
cd project_new

# 安装依赖
pip3 install -r requirements.txt

# 启动MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# 配置Nginx
sudo cp nginx.conf /etc/nginx/nginx.conf
sudo systemctl restart nginx
```

#### 3. 使用systemd管理服务
```bash
# 创建服务文件
sudo tee /etc/systemd/system/wto-app.service << EOF
[Unit]
Description=WTO Negotiation System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project_new
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=/usr/bin/python3 start.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl start wto-app
sudo systemctl enable wto-app
```

## 🔧 配置说明

### 环境变量配置
```bash
# 数据库配置
export MONGO_URI="mongodb://localhost:27017/"
export MONGO_DB="countriesDB"

# 大模型API配置（可选）
export LLM_API_KEY="your-api-key"
export LLM_API_URL="https://api.openai.com/v1"
export LLM_MODEL="gpt-3.5-turbo"

# Flask配置
export FLASK_ENV="production"
export SECRET_KEY="your-secret-key"
```

### 数据库初始化
```bash
# 连接MongoDB
mongo

# 创建数据库
use countriesDB

# 导入国家数据（如果有）
mongoimport --db countriesDB --collection countries_lc --file countries.json
```

### Nginx配置
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
mongo
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

## 🚨 故障排除

### 常见问题

#### 1. MongoDB连接失败
```bash
# 检查MongoDB服务状态
sudo systemctl status mongod

# 检查端口是否被占用
sudo netstat -tulpn | grep 27017

# 重启MongoDB
sudo systemctl restart mongod
```

#### 2. 端口被占用
```bash
# 查看端口占用
sudo lsof -i :5000

# 杀死进程
sudo kill -9 <PID>

# 或者修改端口
# 编辑 config.py 中的 PORT 配置
```

#### 3. 权限问题
```bash
# 修复文件权限
sudo chown -R www-data:www-data /path/to/project_new
sudo chmod -R 755 /path/to/project_new

# 创建上传目录
sudo mkdir -p app/static/uploads
sudo chmod 777 app/static/uploads
```

#### 4. 依赖包问题
```bash
# 清理缓存
pip cache purge

# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 📞 技术支持

如果遇到问题，请：

1. 查看日志文件获取详细错误信息
2. 检查系统资源使用情况
3. 确认网络连接和防火墙设置
4. 参考项目文档和常见问题
5. 提交Issue到项目仓库

## 🔄 更新部署

### 代码更新
```bash
# 拉取最新代码
git pull origin main

# 重新安装依赖（如果有变化）
pip install -r requirements.txt

# 重启服务
# 本地部署
pkill -f "python start.py"
python start.py

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

