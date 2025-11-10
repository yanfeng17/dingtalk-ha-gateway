# DingTalk Home Assistant Gateway

高性能钉钉（DingTalk）消息网关，用于连接钉钉和 Home Assistant。

## ✨ 特性

- ✅ **实时消息接收** - Stream 模式或 Webhook 推送
- ✅ **消息发送** - 支持文本和 Markdown 消息
- ✅ **WebSocket 推送** - 实时推送到 Home Assistant
- ✅ **REST API** - 完整的 HTTP API
- ✅ **高性能** - 优化的异步架构
- ✅ **易部署** - 支持本地运行和云端部署

## 📋 版本

**当前版本：v0.1.0**

### 核心功能
- Stream 模式连接（推荐，无需公网IP）
- Webhook 模式支持（需要公网地址）
- 异步消息处理架构
- WebSocket 实时推送

## 🚀 快速开始

### 本地部署

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入钉钉应用凭证
```

#### 3. 启动服务

```bash
python app.py
```

服务将运行在 `http://0.0.0.0:8099`

### ☁️ 云端部署

#### AWS EC2 部署（推荐）

**一键部署**：
```bash
curl -fsSL https://raw.githubusercontent.com/yanfeng17/dingtalk-ha-gateway/master/deploy.sh | bash
```

**详细指南**：📖 [AWS 部署完整教程](AWS_DEPLOYMENT.md)

支持其他云平台（阿里云、腾讯云、Google Cloud、Azure）

## 🔌 API 端点

### 健康检查
```
GET /health
```

### 发送文本消息
```
POST /send_message
{
  "target": "userid123",
  "content": "Hello"
}
```

### 发送 Markdown 消息
```
POST /send_markdown
{
  "target": "userid123",
  "title": "通知",
  "content": "# 标题\n内容"
}
```

### 钉钉 Webhook（仅 Webhook 模式）
```
POST /dingtalk/webhook
```

### WebSocket 连接
```
WS /ws
```

## 🏗️ 架构

```
钉钉服务器 ←→ Gateway (FastAPI) ←→ Home Assistant
              │
              ├─ WebSocket 推送
              ├─ REST API
              └─ Stream/Webhook 接收
```

## 🔧 配置

所有配置通过环境变量设置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `CHANNEL_TYPE` | 通道类型 | `dingtalk` |
| `GATEWAY_HOST` | 监听地址 | `0.0.0.0` |
| `GATEWAY_PORT` | 监听端口 | `8099` |
| `GATEWAY_TOKEN` | API 访问令牌（可选） | - |
| `DINGTALK_CLIENT_ID` | 钉钉应用 Client ID（新版） | **必填** |
| `DINGTALK_CLIENT_SECRET` | 钉钉应用 Client Secret（新版） | **必填** |
| `DINGTALK_USE_STREAM` | 使用 Stream 模式 | `true` |
| `DINGTALK_WEBHOOK_SECRET` | Webhook 签名密钥（可选） | - |

> **⚠️ 注意**：新版本使用 `CLIENT_ID` 和 `CLIENT_SECRET`，不再需要 `AGENT_ID`。查看 [迁移指南](./MIGRATION_GUIDE.md) 了解详情。

## 🌐 部署

### 本地运行（推荐使用 Stream 模式）

Stream 模式不需要公网 IP，适合本地开发和家庭使用。

```bash
# 配置 .env
DINGTALK_USE_STREAM=true
DINGTALK_CLIENT_ID=your_client_id
DINGTALK_CLIENT_SECRET=your_client_secret

# 启动
python app.py
```

### 云端部署（可选 Webhook 模式）

如果需要使用 Webhook 模式，需要公网 IP 和域名：

```bash
# 配置
DINGTALK_USE_STREAM=false
DINGTALK_WEBHOOK_SECRET=your_secret

# 在钉钉开放平台配置 Webhook URL
# https://your-domain.com/dingtalk/webhook
```

## 📖 钉钉开放平台配置

### 1. 创建企业内部应用

1. 访问 [钉钉开放平台](https://open-dev.dingtalk.com/)
2. 创建企业内部应用
3. 记录 **Client ID** 和 **Client Secret**（凭证与基础信息中）

### 2. 配置权限

在应用管理页面配置以下权限：
- 企业内部机器人消息发送 `qyapi_robot.send`
- 接收企业会话消息 `robot.receive`

### 3. 选择连接模式

**Stream 模式（推荐）：**
- 开发管理 → Stream 推送
- 开启 Stream 推送
- 订阅事件：选择"机器人接收消息"

**Webhook 模式：**
- 开发管理 → 事件订阅
- 配置 Webhook 地址：`https://your-domain.com/dingtalk/webhook`
- 配置加密密钥

## 🤝 配套项目

- [dingtalk-ha-integration](../dingtalk-ha-integration) - Home Assistant 自定义集成

## 🔍 故障排查

### Stream 模式连接失败
```bash
# 检查依赖
pip install dingtalk-stream

# 检查 AppKey 和 AppSecret 是否正确
# 检查网络连接
```

### Webhook 无法接收消息
- 确保服务有公网 IP
- 检查钉钉平台 Webhook 配置
- 验证签名密钥是否正确

## 📝 许可证

MIT License

## 🙏 致谢

基于 Home Assistant 生态构建，参考飞书集成架构设计。

---

**享受您的智能家居钉钉集成！** 🏠📱
