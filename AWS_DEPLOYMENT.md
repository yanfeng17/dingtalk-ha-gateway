# AWS EC2 部署指南

完整的 DingTalk Gateway 在亚马逊 EC2 服务器上的部署指南。

## 📋 前置要求

- AWS 账号
- 钉钉应用凭证（Client ID, Client Secret, Agent ID）
- 基本的 Linux 命令知识

## 🚀 快速部署（推荐）

### 方案 A: 使用自动化脚本

```bash
# 1. 连接到 EC2 实例
ssh -i your-key.pem ubuntu@your-ec2-ip

# 2. 下载并运行部署脚本
curl -fsSL https://raw.githubusercontent.com/yanfeng17/dingtalk-ha-gateway/master/deploy.sh | bash
```

### 方案 B: 手动部署

按照下面的详细步骤操作。

---

## 📝 详细部署步骤

### 第一步：创建 EC2 实例

#### 1.1 登录 AWS Console
访问：https://console.aws.amazon.com/ec2/

#### 1.2 启动实例
点击 **"Launch Instance"（启动实例）**

#### 1.3 配置实例
```
名称: dingtalk-gateway
镜像: Ubuntu Server 22.04 LTS (HVM), SSD Volume Type
架构: 64位 (x86)
实例类型: t2.micro 或 t3.micro（免费套餐）
密钥对: 创建新密钥对或使用现有的
  - 类型: RSA
  - 格式: .pem
  - 下载并妥善保管密钥文件
```

#### 1.4 配置网络（重要！）
**安全组设置**：

| 类型 | 协议 | 端口范围 | 源 | 说明 |
|------|------|---------|-----|------|
| SSH | TCP | 22 | My IP | SSH 访问 |
| Custom TCP | TCP | 8099 | Anywhere-IPv4 (0.0.0.0/0) | Gateway API（HA访问） |

⚠️ **注意**：
- 如果你的 HA 有固定公网 IP，建议将 8099 端口的源设置为你的 HA IP
- 如果 HA 在家里，可以使用 DDNS + 当前IP

#### 1.5 配置存储
```
根卷: 8 GB gp3 SSD（免费套餐足够）
```

#### 1.6 启动实例
- 检查配置
- 点击 **"Launch Instance"**
- 记录实例的**公网IP地址**

---

### 第二步：连接到 EC2 实例

#### 2.1 设置密钥权限（首次使用）

**Windows 用户**：
```powershell
# 使用 PowerShell
icacls your-key.pem /inheritance:r
icacls your-key.pem /grant:r "$($env:USERNAME):(R)"
```

**Mac/Linux 用户**：
```bash
chmod 400 your-key.pem
```

#### 2.2 连接到实例

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

例如：
```bash
ssh -i dingtalk-key.pem ubuntu@54.123.45.67
```

---

### 第三步：安装依赖

#### 3.1 更新系统
```bash
sudo apt update
sudo apt upgrade -y
```

#### 3.2 安装 Python 3.11+
```bash
# Ubuntu 22.04 默认是 Python 3.10，我们安装 3.11
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
```

#### 3.3 安装其他工具
```bash
sudo apt install -y git curl
```

#### 3.4 验证安装
```bash
python3.11 --version  # 应该显示 Python 3.11.x
git --version         # 应该显示 git version 2.x
```

---

### 第四步：部署代码

#### 4.1 克隆代码仓库
```bash
cd ~
git clone https://github.com/yanfeng17/dingtalk-ha-gateway.git
cd dingtalk-ha-gateway
```

#### 4.2 创建虚拟环境
```bash
python3.11 -m venv venv
source venv/bin/activate
```

#### 4.3 安装依赖包
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 第五步：配置环境变量

#### 5.1 复制配置模板
```bash
cp .env.example .env
```

#### 5.2 编辑配置文件
```bash
nano .env
```

#### 5.3 填写配置（重要！）
```bash
CHANNEL_TYPE=dingtalk
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8099

# 可选：设置访问令牌（推荐，增加安全性）
GATEWAY_TOKEN=your_random_secure_token_here

# 钉钉凭证（必填）
DINGTALK_CLIENT_ID=你的ClientID
DINGTALK_CLIENT_SECRET=你的ClientSecret
DINGTALK_AGENT_ID=你的AgentID

# 使用 Stream 模式（推荐）
DINGTALK_USE_STREAM=true
```

**保存文件**：
- 按 `Ctrl + O` 保存
- 按 `Enter` 确认
- 按 `Ctrl + X` 退出

---

### 第六步：测试运行

#### 6.1 手动测试
```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 启动 Gateway
python app.py
```

#### 6.2 查看日志
应该看到：
```
[2025-11-10 10:00:00] INFO - Starting DingTalk Gateway...
[2025-11-10 10:00:00] INFO - Stream mode enabled
[2025-11-10 10:00:01] INFO - Gateway started on http://0.0.0.0:8099
```

#### 6.3 测试 API（新开一个终端）
```bash
# 在本地电脑或 EC2 另一个会话中测试
curl http://YOUR_EC2_PUBLIC_IP:8099/health
```

应该返回：
```json
{"status":"healthy"}
```

#### 6.4 停止测试
按 `Ctrl + C` 停止服务

---

### 第七步：设置系统服务（开机自启）

#### 7.1 创建 systemd 服务文件
```bash
sudo nano /etc/systemd/system/dingtalk-gateway.service
```

#### 7.2 粘贴以下内容
```ini
[Unit]
Description=DingTalk Home Assistant Gateway
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/dingtalk-ha-gateway
Environment="PATH=/home/ubuntu/dingtalk-ha-gateway/venv/bin"
ExecStart=/home/ubuntu/dingtalk-ha-gateway/venv/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**保存并退出**：`Ctrl + O`, `Enter`, `Ctrl + X`

#### 7.3 启用并启动服务
```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable dingtalk-gateway

# 启动服务
sudo systemctl start dingtalk-gateway

# 查看状态
sudo systemctl status dingtalk-gateway
```

应该显示：`Active: active (running)`

#### 7.4 查看日志
```bash
# 实时查看日志
sudo journalctl -u dingtalk-gateway -f

# 查看最近的日志
sudo journalctl -u dingtalk-gateway -n 50
```

---

### 第八步：配置 Home Assistant

#### 8.1 修改 HA 集成配置

在 Home Assistant 中：

1. 进入 **配置** → **设备与服务**
2. 找到 **DingTalk Gateway** 集成
3. 点击 **配置**
4. 修改 **Gateway URL**：
   ```
   http://YOUR_EC2_PUBLIC_IP:8099
   ```
5. 如果设置了 `GATEWAY_TOKEN`，填写 **Access Token**
6. 保存

#### 8.2 测试连接

发送测试消息：
```yaml
service: dingtalk_gateway.send_message
data:
  target: "你的钉钉UserID"
  message: "测试消息 from AWS Gateway"
```

---

## 🔧 常用管理命令

### 服务管理
```bash
# 启动服务
sudo systemctl start dingtalk-gateway

# 停止服务
sudo systemctl stop dingtalk-gateway

# 重启服务
sudo systemctl restart dingtalk-gateway

# 查看状态
sudo systemctl status dingtalk-gateway

# 查看日志
sudo journalctl -u dingtalk-gateway -f
```

### 更新代码
```bash
cd ~/dingtalk-ha-gateway
git pull
sudo systemctl restart dingtalk-gateway
```

### 修改配置
```bash
cd ~/dingtalk-ha-gateway
nano .env
sudo systemctl restart dingtalk-gateway
```

---

## 🔐 安全加固（可选但推荐）

### 1. 配置 API Token
```bash
# 编辑 .env
nano .env

# 添加或修改
GATEWAY_TOKEN=a_very_long_random_secure_token_here_use_password_generator
```

### 2. 限制安全组访问
在 AWS Console 中，修改安全组：
- 将 8099 端口的源从 `0.0.0.0/0` 改为你的 HA 公网 IP
- 例如：`123.45.67.89/32`

### 3. 配置 Nginx 反向代理 + SSL（高级）

#### 安装 Nginx
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

#### 配置反向代理
```bash
sudo nano /etc/nginx/sites-available/dingtalk-gateway
```

内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8099;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 启用配置
```bash
sudo ln -s /etc/nginx/sites-available/dingtalk-gateway /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 配置 SSL（如果有域名）
```bash
sudo certbot --nginx -d your-domain.com
```

---

## 📊 监控和诊断

### 检查服务状态
```bash
sudo systemctl status dingtalk-gateway
```

### 查看实时日志
```bash
sudo journalctl -u dingtalk-gateway -f
```

### 查看资源使用
```bash
# CPU 和内存
htop

# 如果没有安装 htop
sudo apt install -y htop
```

### 测试网络连接
```bash
# 测试 Gateway 端口
curl http://localhost:8099/health

# 测试从外部访问
curl http://YOUR_EC2_PUBLIC_IP:8099/health
```

---

## 🐛 常见问题

### 问题 1：服务无法启动
```bash
# 查看详细错误
sudo journalctl -u dingtalk-gateway -n 100 --no-pager

# 检查配置文件
cat .env

# 手动测试
cd ~/dingtalk-ha-gateway
source venv/bin/activate
python app.py
```

### 问题 2：无法从 HA 访问
```bash
# 检查 EC2 安全组
# AWS Console → EC2 → Security Groups → 检查 8099 端口是否开放

# 检查防火墙
sudo ufw status
# 如果启用了，添加规则
sudo ufw allow 8099

# 测试端口监听
sudo netstat -tlnp | grep 8099
```

### 问题 3：Stream 连接失败
```bash
# 检查钉钉凭证
cat .env | grep DINGTALK

# 检查日志
sudo journalctl -u dingtalk-gateway | grep -i error
```

### 问题 4：内存不足
```bash
# 查看内存使用
free -h

# 如果 t2.micro 内存不够，考虑：
# 1. 升级到 t3.small
# 2. 添加 swap（临时方案）
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 💰 费用估算

### AWS EC2 费用（按月）

| 实例类型 | vCPU | 内存 | 免费套餐 | 按需价格（美国东部） |
|---------|------|------|---------|---------------------|
| t2.micro | 1 | 1GB | 750小时/月免费 | ~$8.50/月 |
| t3.micro | 2 | 1GB | 否 | ~$7.50/月 |
| t3.small | 2 | 2GB | 否 | ~$15/月 |

### 流量费用
- 出站流量：前 1GB 免费，之后约 $0.09/GB
- DingTalk Gateway 流量很小，通常 < 1GB/月

### 总估算
- **免费套餐用户**：前 12 个月，t2.micro 几乎免费
- **付费用户**：约 $10-20/月（取决于实例类型）

---

## 🔄 自动化部署脚本

我们提供了一键部署脚本 `deploy.sh`：

```bash
curl -fsSL https://raw.githubusercontent.com/yanfeng17/dingtalk-ha-gateway/master/deploy.sh -o deploy.sh
chmod +x deploy.sh
./deploy.sh
```

脚本会自动：
1. 安装依赖
2. 克隆代码
3. 配置虚拟环境
4. 引导你配置 .env
5. 设置 systemd 服务
6. 启动服务

---

## 📚 其他云平台

本指南主要针对 AWS，但也适用于其他云平台：

- **阿里云 ECS**：类似步骤，使用安全组开放 8099 端口
- **腾讯云 CVM**：类似步骤，使用安全组开放 8099 端口
- **Google Cloud**：使用 VM 实例，配置防火墙规则
- **Azure**：使用虚拟机，配置网络安全组

关键都是：**开放 8099 端口 + 正确配置环境变量**

---

## ✅ 部署检查清单

- [ ] EC2 实例已创建并运行
- [ ] 安全组开放了 8099 端口
- [ ] Python 3.11+ 已安装
- [ ] 代码已克隆
- [ ] 虚拟环境已创建
- [ ] 依赖已安装
- [ ] .env 已正确配置
- [ ] 手动测试成功
- [ ] systemd 服务已配置
- [ ] 服务已启动并设置开机自启
- [ ] 从 HA 可以访问 Gateway
- [ ] 消息收发测试通过

---

## 🎉 完成！

恭喜！你已经成功在 AWS EC2 上部署了 DingTalk Gateway。

**下一步**：
- 配置 Home Assistant 中的自动化
- 设置消息通知规则
- 监控服务运行状态

**需要帮助？**
- 查看项目 README: https://github.com/yanfeng17/dingtalk-ha-gateway
- 提交 Issue: https://github.com/yanfeng17/dingtalk-ha-gateway/issues

---

**作者**: yanfeng17  
**更新时间**: 2025-11-10  
**版本**: v0.1.1
