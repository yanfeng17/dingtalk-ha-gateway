# 钉钉 API 迁移指南

## ⚠️ 重要变更：从旧版本迁移到新版本

钉钉开放平台已更新 Stream 模式的认证方式。本项目已适配新版本。

## 📋 主要变更

### 认证凭证变更

#### 旧版本（已过时）
```bash
DINGTALK_APP_KEY=dingxxxxxxxx
DINGTALK_APP_SECRET=xxxxxxxxxx
DINGTALK_AGENT_ID=123456789  # ❌ 不再需要
```

#### 新版本（当前）
```bash
DINGTALK_CLIENT_ID=dingxxxxxxxx
DINGTALK_CLIENT_SECRET=xxxxxxxxxx
# ✅ 不再需要 AGENT_ID
```

## 🔄 如何迁移

### 1. 在钉钉开放平台获取新凭证

1. 访问 https://open-dev.dingtalk.com/
2. 进入你的应用详情页
3. 在"凭证与基础信息"中查看：
   - **Client ID** (原 AppKey) 
   - **Client Secret** (原 AppSecret)

### 2. 更新 `.env` 配置

将旧的配置：
```bash
DINGTALK_APP_KEY=xxx
DINGTALK_APP_SECRET=xxx
DINGTALK_AGENT_ID=xxx
```

改为新的配置：
```bash
DINGTALK_CLIENT_ID=xxx
DINGTALK_CLIENT_SECRET=xxx
```

### 3. 重启服务

```bash
# 停止旧服务
# Ctrl+C 或 kill 进程

# 启动新服务
python app.py
```

## 📝 API 变更说明

### Stream SDK 初始化

#### 旧版本
```python
from dingtalk_stream import DingTalkStreamClient

# 旧版本可能使用 Credential 类
credential = DingTalkStreamClient.Credential(app_key, app_secret)
client = DingTalkStreamClient(credential)
```

#### 新版本（当前）
```python
from dingtalk_stream import DingTalkStreamClient

# 新版本直接传递 client_id 和 client_secret
client = DingTalkStreamClient(client_id, client_secret)  # ✅
```

### 发送消息 API

新版本不再需要 `agent_id` 参数：

#### 旧版本
```python
data = {
    "agent_id": agent_id,  # ❌ 不再需要
    "userid_list": target,
    "msg": {...}
}
```

#### 新版本
```python
data = {
    "userid_list": target,
    "msg": {...}
}
```

## ✅ 兼容性说明

- **SDK 版本**：需要 `dingtalk-stream >= 0.8.0`
- **Python 版本**：Python 3.11+
- **API 端点**：保持不变
- **功能支持**：所有功能保持兼容

## 🐛 常见问题

### Q: 我的旧配置还能用吗？

**A:** 不能。钉钉已弃用旧的 AppKey/AppSecret/AgentId 认证方式，必须使用新的 ClientId/ClientSecret。

### Q: 如何获取 ClientId 和 ClientSecret？

**A:** 访问钉钉开放平台 → 你的应用 → 凭证与基础信息。ClientId 和 ClientSecret 就显示在那里。

### Q: 需要重新创建应用吗？

**A:** 不需要。现有应用的 ClientId 就是原来的 AppKey，ClientSecret 就是 AppSecret。只是名称变了。

### Q: 为什么不需要 AgentId 了？

**A:** Stream 模式下，钉钉平台会自动关联应用，不需要额外指定 AgentId。

## 📚 参考资料

- [钉钉 Stream 模式文档](https://open.dingtalk.com/document/development/introduction-to-stream-mode)
- [dingtalk-stream SDK](https://pypi.org/project/dingtalk-stream/)
- [本项目 README](./README.md)

---

**更新日期**: 2025-11-09  
**适用版本**: v0.1.0+
