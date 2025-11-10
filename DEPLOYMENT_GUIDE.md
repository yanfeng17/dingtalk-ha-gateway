# 钉钉 Gateway 部署指南

本指南将帮助你一步步完成钉钉 Gateway 的完整部署。

> **⚠️ 重要提示**：本项目使用钉钉最新的 Stream 模式 API，使用 **Client ID** 和 **Client Secret** 进行认证，**不再需要 Agent ID**。如果你看到旧的教程提到 AgentId，请忽略。详见 [迁移指南](./MIGRATION_GUIDE.md)。

## 📋 前置准备

### 1. 系统要求
- Python 3.11 或更高版本
- pip 包管理器
- 网络连接

### 2. 钉钉开放平台账号
- 企业钉钉账号（管理员权限）
- 访问 [钉钉开放平台](https://open-dev.dingtalk.com/)

## 🚀 第一步：创建钉钉应用

### 1.1 登录钉钉开放平台

1. 访问 https://open-dev.dingtalk.com/
2. 使用管理员账号登录
3. 进入"应用开发" → "企业内部开发"

### 1.2 创建应用

1. 点击"创建应用"
2. 填写应用信息：
   - **应用名称**: Home Assistant Gateway
   - **应用描述**: 智能家居钉钉集成
   - **应用图标**: 上传一个图标（可选）
3. 点击"确认创建"

### 1.3 获取应用凭证

创建成功后，进入应用详情页面 → **凭证与基础信息**：

- **Client ID**: `dingxxxxxxxxxxxxxx`（类似这种格式）
- **Client Secret**: 点击"查看"获取，保存好！

**重要提示：** 
- ✅ 新版本只需要 Client ID 和 Client Secret
- ❌ **不需要 AgentId**（Stream 模式已弃用）
- Client Secret 只显示一次，请妥善保存！

> **说明**：Client ID 实际上就是原来的 AppKey，Client Secret 就是 AppSecret，只是名称更新了。

### 1.4 配置应用权限

在应用管理页面：

1. 进入"权限管理"
2. 添加以下权限：
   - ✅ 企业会话消息 → **机器人发送消息** (`qyapi_robot.send`)
   - ✅ 机器人接收消息 → **接收企业会话消息** (`robot.receive`)
3. 点击"保存"

### 1.5 配置消息订阅（Stream 模式 - 推荐）

1. 进入"开发管理" → "事件订阅"
2. 选择 **"Stream 推送"** 模式
3. 开启 Stream 推送
4. 订阅事件：
   - ✅ 勾选"机器人接收消息"
5. 保存配置

**为什么选择 Stream 模式？**
- ✅ 无需公网 IP
- ✅ 无需配置域名
- ✅ 更简单的部署
- ✅ 更稳定的连接

### 1.6 发布应用

1. 返回应用详情页
2. 点击"版本管理与发布"
3. 创建版本并发布
4. **添加可见范围**：选择需要使用机器人的部门或人员

## 🔧 第二步：部署 Gateway 服务

### 2.1 下载代码

```bash
cd /your/path/
git clone <your-repo>  # 或者直接复制代码目录
cd dingtalk-ha-gateway
```

### 2.2 安装 Python 依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2.3 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 文件
notepad .env  # Windows
# 或
nano .env     # Linux/Mac
```

填入以下配置：

```bash
# Gateway 基础配置
CHANNEL_TYPE=dingtalk
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8099
GATEWAY_TOKEN=your_secure_token_123  # 可选，建议设置

# 钉钉应用配置（从第一步获取）
# 注意：使用新版 Client ID 和 Client Secret
DINGTALK_CLIENT_ID=dingxxxxxxxxxxxxxx
DINGTALK_CLIENT_SECRET=your_client_secret_here

# Stream 模式（推荐，无需公网 IP）
DINGTALK_USE_STREAM=true
```

**安全提示：**
- 不要将 `.env` 文件提交到 Git
- 定期更换 `GATEWAY_TOKEN`
- 妥善保管 `DINGTALK_CLIENT_SECRET`

### 2.4 测试启动

```bash
# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 启动服务
python app.py
```

你应该看到类似输出：

```
[2025-11-09 16:00:00] INFO - __main__: Gateway manager started with channel: dingtalk
[2025-11-09 16:00:00] INFO - __main__: Message pipeline optimized for low latency
[2025-11-09 16:00:01] INFO - dingtalk_client: [DingTalk] Client initialized
[2025-11-09 16:00:02] INFO - dingtalk_client: [DingTalk] Starting Stream connection...
INFO:     Uvicorn running on http://0.0.0.0:8099 (Press CTRL+C to quit)
```

### 2.5 测试 API

打开另一个终端，测试健康检查：

```bash
curl http://localhost:8099/health
```

应该返回：
```json
{"status": "ok", "channel": "dingtalk"}
```

**验证配置：**
- 检查日志中是否有 `[DingTalk] Client initialized with client_id: dingxxxxxx...`
- 确认 Stream 连接状态：`[DingTalk] Starting Stream connection...`

## 🏠 第三步：集成 Home Assistant

### 3.1 安装 HA 集成

```bash
# 进入 Home Assistant 配置目录
cd /config

# 创建自定义组件目录（如果不存在）
mkdir -p custom_components

# 复制集成文件
cp -r /path/to/dingtalk-ha-integration/custom_components/dingtalk_gateway \
      custom_components/
```

### 3.2 重启 Home Assistant

```bash
# 通过 HA 界面重启，或者命令行：
ha core restart
```

### 3.3 添加集成

1. 打开 Home Assistant Web 界面
2. 进入 **配置** → **设备与服务**
3. 点击右下角 **"+ 添加集成"**
4. 搜索 **"DingTalk Gateway"**
5. 填写配置：
   - **Gateway 服务地址**: `http://localhost:8099`（如果 HA 和 Gateway 在同一台机器）
   - **访问令牌**: 填入 `.env` 中设置的 `GATEWAY_TOKEN`
6. 点击"提交"

### 3.4 验证安装

检查以下内容：

1. **实体**：进入"开发者工具" → "状态"
   - 应该看到 `sensor.dingtalk_gateway_last_message`

2. **服务**：进入"开发者工具" → "服务"
   - 应该看到 `dingtalk_gateway.send_message`
   - 应该看到 `dingtalk_gateway.send_markdown`

3. **日志**：检查 Home Assistant 日志
   ```
   Gateway WebSocket connected
   ```

## 🧪 第四步：测试功能

### 4.1 测试发送消息

在 HA 的"开发者工具" → "服务"中：

```yaml
service: dingtalk_gateway.send_message
data:
  target: "your_userid"  # 需要替换成你的钉钉 userid
  message: "测试消息：Hello from Home Assistant!"
```

**如何获取 userid？**
- 方法1：在钉钉开放平台"通讯录管理"中查看
- 方法2：先让别人发消息给机器人，从日志中看到 sender_id

### 4.2 测试接收消息

1. 在钉钉中找到你的应用机器人
2. 给机器人发送消息："你好"
3. 检查 HA 中的 Sensor 状态：
   - `sensor.dingtalk_gateway_last_message` 应该更新为"你好"

### 4.3 测试自动化

创建一个测试自动化：

```yaml
# configuration.yaml 或通过 UI 创建
automation:
  - alias: "钉钉测试自动化"
    trigger:
      - platform: event
        event_type: dingtalk_gateway_message
    action:
      - service: dingtalk_gateway.send_message
        data:
          target: "{{ trigger.event.data.sender }}"
          message: "收到你的消息：{{ trigger.event.data.content }}"
```

给机器人发消息，应该会自动回复。

## 🔒 第五步：生产环境优化

### 5.1 使用 Systemd 守护进程（Linux）

创建服务文件：

```bash
sudo nano /etc/systemd/system/dingtalk-gateway.service
```

内容：

```ini
[Unit]
Description=DingTalk Home Assistant Gateway
After=network.target

[Service]
Type=simple
User=homeassistant
WorkingDirectory=/opt/dingtalk-ha-gateway
Environment="PATH=/opt/dingtalk-ha-gateway/venv/bin"
ExecStart=/opt/dingtalk-ha-gateway/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable dingtalk-gateway
sudo systemctl start dingtalk-gateway
sudo systemctl status dingtalk-gateway
```

### 5.2 Windows 后台运行

使用 `nssm` 工具：

```bash
# 下载 nssm
# https://nssm.cc/download

# 安装服务
nssm install DingTalkGateway "C:\path\to\venv\Scripts\python.exe" "C:\path\to\app.py"
nssm set DingTalkGateway AppDirectory "C:\path\to\dingtalk-ha-gateway"
nssm start DingTalkGateway
```

### 5.3 Docker 部署（可选）

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8099

CMD ["python", "app.py"]
```

构建和运行：

```bash
docker build -t dingtalk-gateway .
docker run -d --name dingtalk-gateway \
  --env-file .env \
  -p 8099:8099 \
  --restart unless-stopped \
  dingtalk-gateway
```

## 📊 监控和维护

### 查看 Gateway 日志

```bash
# 如果使用 systemd
sudo journalctl -u dingtalk-gateway -f

# 如果直接运行
# 日志会输出到控制台
```

### 查看 HA 日志

Home Assistant 界面 → 配置 → 日志

或启用详细日志：

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.dingtalk_gateway: debug
```

### 常见问题

1. **Stream 连接失败**
   ```
   解决方法：
   - 检查网络连接
   - 确认 AppKey 和 AppSecret 正确
   - 重新生成 AppSecret
   ```

2. **收不到消息**
   ```
   解决方法：
   - 确认应用已发布
   - 检查可见范围设置
   - 确认订阅了正确的事件
   ```

3. **WebSocket 断开**
   ```
   解决方法：
   - 检查 Gateway 服务状态
   - 查看网络连接
   - 会自动重连，等待 1-60 秒
   ```

## ✅ 部署清单

- [ ] 钉钉应用已创建并配置
- [ ] 获取了 **Client ID** 和 **Client Secret**（新版凭证）
- [ ] 配置了应用权限
- [ ] 开启了 Stream 推送
- [ ] 应用已发布并设置可见范围
- [ ] Gateway 服务安装并运行
- [ ] HA 集成已安装并配置
- [ ] 测试发送消息成功
- [ ] 测试接收消息成功
- [ ] 测试自动化工作正常
- [ ] 配置了守护进程（生产环境）

> **📝 注意**：不需要配置 AgentId，这是旧版本的要求。

## 🎉 完成！

恭喜！你已经成功部署了钉钉 Home Assistant 集成。现在可以通过钉钉控制和监控你的智能家居了！

## 📚 进阶使用

- 查看 [README.md](./README.md) 了解更多 API 用法
- 查看 [示例自动化](../dingtalk-ha-integration/README.md#使用示例) 获取灵感
- 加入社区讨论和反馈问题

---

**祝你使用愉快！** 🚀
