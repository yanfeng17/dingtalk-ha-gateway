# 钉钉消息发送模式说明

## 📱 两种消息显示方式

### 1. 聊天框消息 ✅ 推荐
- **显示位置**：与机器人的聊天对话框中
- **用户体验**：就像和人聊天一样，在聊天界面中显示
- **使用方式**：通过 `session_webhook` 发送

### 2. 工作通知消息 📢
- **显示位置**：钉钉的"工作通知"中
- **用户体验**：类似系统通知，不在聊天框显示
- **使用方式**：通过企业内部应用API发送（需要agent_id）

## 🔄 智能切换机制

本项目已实现**自动智能切换**：

```
用户发消息给机器人
      ↓
保存 session_webhook（有效期2小时）
      ↓
HA发送消息时：
  ├─ 有活跃的webhook？→ 发到聊天框 ✅
  └─ 没有或已过期？→ 发到工作通知 📢
```

## 📊 使用场景对比

| 场景 | 聊天框消息 | 工作通知 |
|------|-----------|---------|
| **用户刚和机器人聊过天** | ✅ 自动使用 | - |
| **用户2小时内未聊天** | ❌ webhook过期 | ✅ 自动降级 |
| **主动推送通知** | ❌ 无webhook | ✅ 使用 |
| **对话式交互** | ✅ 完美 | ❌ 体验差 |

## 🎯 工作原理

### Session Webhook 机制

当用户给机器人发送消息时，钉钉会提供一个临时的 `session_webhook`：

```json
{
  "session_webhook": "https://oapi.dingtalk.com/robot/send?access_token=xxx",
  "session_webhook_expired_time": 1699999999000
}
```

**特点：**
- ✅ 发送的消息直接显示在聊天框
- ✅ 无需 agent_id
- ⏰ 有效期约2小时
- 🔒 只能回复给发送者

### 发送流程

```python
# 1. 用户发消息
用户: "你好"
  ↓
# 2. Gateway接收并缓存webhook
缓存: {
    "user123": {
        "webhook": "https://...",
        "expired_at": 1699999999000
    }
}
  ↓
# 3. HA回复消息
HA: "你好，有什么可以帮你？"
  ↓
# 4. Gateway智能选择发送方式
if webhook存在且未过期:
    → 使用webhook发送（聊天框）✅
else:
    → 使用工作通知API（工作通知）📢
```

## 📝 日志识别

### 聊天框发送成功
```
[DingTalk] ✅ Message sent to chat via webhook: user123
```

### 工作通知发送
```
[DingTalk] 📢 Sending via work notification (no active webhook for user123)
[DingTalk] Work notification sent to user123
```

### Webhook过期降级
```
[DingTalk] Webhook send failed, fallback to work notification: ...
[DingTalk] Work notification sent to user123
```

## 💡 使用建议

### 对于对话式交互
1. 引导用户先给机器人发消息
2. 在用户消息后的2小时内回复
3. 这样消息会显示在聊天框中

### 对于主动推送
- 主动推送通知会显示在工作通知中
- 这是正常的，因为没有对话上下文

### 保持聊天框活跃
- 定期与用户互动
- 每次用户发消息都会刷新webhook有效期

## 🔧 故障排查

### 消息还是显示在工作通知？

检查日志：

1. **用户最近是否发过消息？**
   ```
   [DingTalk] Cached session_webhook for user123  ← 应该有这条
   ```

2. **Webhook是否存在？**
   ```
   [DingTalk] ✅ Message sent to chat via webhook  ← 成功
   或
   [DingTalk] 📢 Sending via work notification    ← 没有webhook
   ```

3. **Webhook是否过期？**
   - 查看时间差是否超过2小时

### 强制使用聊天框

**唯一方法**：让用户先给机器人发一条消息，然后在2小时内回复。

## 🎓 技术细节

### Webhook URL 示例
```
https://oapi.dingtalk.com/robot/send?access_token=xxx&sessionWebhook=xxx
```

### 发送格式
```json
{
  "msgtype": "text",
  "text": {
    "content": "消息内容"
  }
}
```

### 工作通知 API
```
POST /topapi/message/corpconversation/asyncsend_v2
需要: agent_id + access_token
```

## 📚 参考文档

- [钉钉机器人文档](https://open.dingtalk.com/document/orgapp/robot-overview)
- [Session Webhook说明](https://open.dingtalk.com/document/orgapp/receive-message)
- [工作通知API](https://open.dingtalk.com/document/orgapp/asynchronous-sending-of-enterprise-session-messages)

---

**总结**：本项目已实现智能切换，优先使用聊天框，自动降级到工作通知。用户体验最佳！✨
