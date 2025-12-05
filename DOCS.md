# DingTalk Gateway - Home Assistant Add-on

钉钉消息网关，支持Stream推送模式，无需公网IP。

## 功能特性

- ✅ **Stream推送模式** - 无需公网IP，直接连接钉钉服务器
- ✅ **双向消息** - 接收和发送钉钉消息
- ✅ **低延迟** - 本地运行，毫秒级响应
- ✅ **自动重连** - 网络中断自动恢复
- ✅ **安全认证** - 支持API访问令牌
- ✅ **易于配置** - 通过Home Assistant界面配置

## 安装步骤

### 方式1：通过本地Add-on安装（开发测试）

1. **准备文件**
   - 将整个项目文件夹复制到Home Assistant的 `/addons/dingtalk-ha-gateway` 目录
   - 如果使用Samba，可以通过网络共享访问

2. **添加本地仓库**
   - 进入 **Supervisor** → **Add-on Store**
   - 点击右上角菜单（三个点）→ **Repositories**
   - 添加路径：`/addons/dingtalk-ha-gateway`

3. **安装Add-on**
   - 在Add-on Store中找到 **DingTalk Gateway**
   - 点击安装

### 方式2：通过GitHub仓库安装（推荐）

1. **添加仓库**
   - 进入 **Supervisor** → **Add-on Store**
   - 点击右上角菜单（三个点）→ **Repositories**
   - 添加：`https://github.com/yanfeng17/dingtalk-ha-gateway`

2. **安装Add-on**
   - 刷新页面，找到 **DingTalk Gateway**
   - 点击安装

## 配置说明

### 获取钉钉凭证

1. **登录钉钉开发者后台**
   - 访问：https://open-dev.dingtalk.com/

2. **创建企业内部应用**
   - 选择 **应用开发** → **企业内部开发** → **创建应用**
   - 填写应用名称和描述

3. **获取凭证**
   - **Client ID**：应用凭证页面的 `Client ID`
   - **Client Secret**：应用凭证页面的 `Client Secret`
   - **Agent ID**：应用基础信息页面的 `AgentId`

4. **配置事件订阅**
   - 进入应用 → **开发配置** → **事件订阅**
   - 选择 **Stream 模式推送**
   - 点击 **已完成接入，验证连接通道**

5. **配置权限**
   - 进入 **权限管理**
   - 开通以下权限：
     - `qyapi_chat_manage` - 消息管理
     - `qyapi_robot_sendmsg` - 机器人发送消息

### Add-on 配置

在Add-on配置页面填写：

```yaml
dingtalk_client_id: "dingxxxxxxxxxx"        # 必填：钉钉应用Client ID
dingtalk_client_secret: "your_secret_here"  # 必填：钉钉应用Client Secret
dingtalk_agent_id: "123456789"              # 必填：钉钉应用Agent ID
use_stream: true                             # 推荐：使用Stream模式
gateway_token: ""                            # 可选：API访问令牌（增加安全性）
webhook_secret: ""                           # 可选：Webhook模式的签名密钥
```

### 配置项说明

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `dingtalk_client_id` | 字符串 | ✅ | 钉钉应用的Client ID |
| `dingtalk_client_secret` | 密码 | ✅ | 钉钉应用的Client Secret |
| `dingtalk_agent_id` | 字符串 | ✅ | 钉钉应用的Agent ID |
| `use_stream` | 布尔 | ✅ | 是否使用Stream模式（推荐true） |
| `gateway_token` | 密码 | ⬜ | API访问令牌，留空则不验证 |
| `webhook_secret` | 密码 | ⬜ | Webhook模式的签名密钥 |

## 使用方法

### 在Home Assistant中发送消息

#### 方式1：使用REST API

```yaml
# 配置 RESTful command
rest_command:
  send_dingtalk:
    url: "http://localhost:8099/send_message"
    method: POST
    headers:
      Content-Type: "application/json"
      X-Access-Token: "your_token_here"  # 如果配置了gateway_token
    payload: >
      {
        "target": "{{ userid }}",
        "content": "{{ message }}"
      }

# 使用示例
service: rest_command.send_dingtalk
data:
  userid: "manager123"
  message: "前门已打开！"
```

#### 方式2：使用自动化

```yaml
automation:
  - alias: "门打开通知"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: "on"
    action:
      - service: rest_command.send_dingtalk
        data:
          userid: "manager123"
          message: "⚠️ 前门已打开！时间：{{ now().strftime('%H:%M:%S') }}"
```

### API 接口

#### 健康检查
```bash
GET http://localhost:8099/health
```

#### 发送文本消息
```bash
POST http://localhost:8099/send_message
Content-Type: application/json
X-Access-Token: your_token_here

{
  "target": "user_id",
  "content": "消息内容"
}
```

#### 发送Markdown消息
```bash
POST http://localhost:8099/send_markdown
Content-Type: application/json
X-Access-Token: your_token_here

{
  "target": "user_id",
  "title": "标题",
  "content": "**加粗** *斜体* [链接](url)"
}
```

## 查看日志

1. 进入 **Supervisor** → **DingTalk Gateway**
2. 点击 **日志** 标签
3. 查看实时日志输出

正常运行时会看到：
```
[INFO] Starting DingTalk Gateway...
[INFO] Stream mode: True
[INFO] [DingTalk] Client initialized
[INFO] [DingTalk] Starting Stream connection...
[INFO] Gateway started on http://0.0.0.0:8099
```

## 常见问题

### 1. Add-on无法启动

**检查配置**：
- 确认Client ID、Client Secret、Agent ID填写正确
- 检查是否有多余的空格或引号

**查看日志**：
```
DingTalk Client ID is required!
```
说明配置未填写或格式错误。

### 2. Stream连接超时

**可能原因**：
- 网络问题，无法连接钉钉服务器
- 凭证错误

**解决方法**：
1. 检查Home Assistant网络连接
2. 验证钉钉凭证是否正确
3. 确认钉钉开发者后台已启用Stream模式

### 3. 收不到消息

**检查事件订阅**：
1. 登录钉钉开发者后台
2. 进入应用 → **开发配置** → **事件订阅**
3. 确认选择了 **Stream 模式推送**
4. 点击 **已完成接入，验证连接通道**

**检查权限**：
- 确认应用有消息接收权限
- 在群聊中需要@机器人

### 4. 无法发送消息

**检查Agent ID**：
- 发送消息需要正确的Agent ID
- 在钉钉开发者后台应用基础信息页面查看

**检查权限**：
- 应用需要有发送消息的权限
- 目标用户需要在应用可见范围内

### 5. API返回401错误

**原因**：
- 配置了`gateway_token`但请求未携带
- Token不匹配

**解决**：
- 在请求头添加：`X-Access-Token: your_token_here`
- 或者移除`gateway_token`配置

## 性能优化

### 资源占用
- **内存**：约50-100MB
- **CPU**：空闲时<1%，消息处理时<5%
- **网络**：Stream连接维持长连接，流量极小

### 适用硬件
- ✅ Raspberry Pi 3/4
- ✅ x86_64 服务器
- ✅ NUC等迷你PC
- ✅ 虚拟机

## 安全建议

1. **设置Gateway Token**
   - 配置`gateway_token`以保护API接口
   - 使用强密码（建议20位以上随机字符）

2. **限制网络访问**
   - Gateway默认监听所有接口（0.0.0.0:8099）
   - 如果仅内网使用，无需额外配置
   - 不要将8099端口暴露到公网

3. **定期更新**
   - 关注Add-on更新通知
   - 及时升级到最新版本

## 技术支持

- **项目主页**：https://github.com/yanfeng17/dingtalk-ha-gateway
- **问题反馈**：https://github.com/yanfeng17/dingtalk-ha-gateway/issues
- **钉钉开发文档**：https://open.dingtalk.com/

## 版本历史

### v0.1.1 (2025-11-10)
- ✅ 支持Stream推送模式
- ✅ 支持双向消息收发
- ✅ 支持Markdown消息
- ✅ 优化消息延迟
- ✅ 添加Home Assistant Add-on支持

## 许可证

MIT License - 详见 [LICENSE](https://github.com/yanfeng17/dingtalk-ha-gateway/blob/master/LICENSE)

---

**作者**: yanfeng17  
**更新时间**: 2025-12-05  
**版本**: v0.1.1
