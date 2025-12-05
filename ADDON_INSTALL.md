# DingTalk Gateway - Home Assistant Add-on 安装指南

本文档详细说明如何将DingTalk Gateway安装为Home Assistant Add-on。

## 📋 前提条件

- ✅ 运行Home Assistant OS或Supervised版本
- ✅ 有Supervisor访问权限
- ✅ 钉钉企业账号和已创建的应用

## 🎯 优势对比

| 特性 | Addon模式 | AWS部署 |
|------|----------|---------|
| 公网IP | ❌ 不需要 | ✅ 需要 |
| 延迟 | 🚀 极低（本地） | ⏱️ 较高（网络） |
| 费用 | 💰 免费 | 💸 $10-20/月 |
| 维护 | ✨ 自动更新 | 🔧 需手动维护 |
| 配置 | 🖱️ UI界面 | ⌨️ SSH命令行 |

## 📦 安装方式

### 方式一：本地Add-on安装（用于开发测试）

适合开发者和想要自定义的用户。完成后会在"本地加载项"部分显示。

#### 步骤1：准备文件

**选项A：通过Samba共享（最简单）**

1. 确保已安装Samba add-on
2. 通过网络访问Home Assistant
   - Windows: `\\homeassistant\addon`
   - macOS: `smb://homeassistant/addon`
   - Linux: `smb://homeassistant/addon`
3. 进入 `local` 文件夹（如果没有则创建）
4. 创建文件夹 `dingtalk-ha-gateway`
5. 将项目所有文件复制到此文件夹

**选项B：通过SSH（进阶用户）**

```bash
# 1. SSH连接到Home Assistant
ssh root@homeassistant.local

# 2. 创建addon目录
mkdir -p /addon/local/dingtalk-ha-gateway

# 3. 上传文件（在本地电脑执行）
scp -r /path/to/dingtalk-ha-gateway/* root@homeassistant.local:/addon/local/dingtalk-ha-gateway/
```

#### 步骤2：刷新加载项页面

1. 打开Home Assistant
2. 进入 **设置** → **加载项**
3. 刷新页面（Ctrl+F5 或 Cmd+R）
4. 在 **本地加载项** 部分找到 **DingTalk Gateway**

**注意**：本地add-on会自动显示，无需添加仓库路径

#### 步骤3：安装Add-on

1. 在加载项商店中找到 **DingTalk Gateway**（Local）
2. 点击进入
3. 点击 **安装**
4. 等待安装完成（约1-3分钟）

---

### 方式二：通过GitHub仓库安装（推荐用于生产）

适合普通用户，可以自动获取更新。

#### 步骤1：添加仓库

1. 打开Home Assistant
2. 进入 **设置** → **加载项**
3. 点击右上角 **⋮** 菜单
4. 选择 **仓库**
5. 添加以下URL：
   ```
   https://github.com/yanfeng17/dingtalk-ha-gateway
   ```
6. 点击 **添加**

#### 步骤2：安装Add-on

1. 刷新加载项商店页面
2. 找到 **DingTalk Gateway**
3. 点击进入
4. 点击 **安装**
5. 等待安装完成

---

## ⚙️ 配置Add-on

### 步骤1：获取钉钉凭证

#### 1.1 登录钉钉开发者后台
访问：https://open-dev.dingtalk.com/

#### 1.2 创建企业内部应用
1. 点击 **应用开发** → **企业内部开发**
2. 点击 **创建应用**
3. 填写应用信息：
   - 应用名称：`Home Assistant Gateway`
   - 应用描述：`智能家居消息网关`
   - 上传应用图标（可选）
4. 点击 **确认创建**

#### 1.3 获取应用凭证

**获取Client ID和Client Secret：**
1. 进入应用详情页
2. 点击 **凭证与基础信息**
3. 记录以下信息：
   - **Client ID**：`dingxxxxxxxxxx`（复制）
   - **Client Secret**：点击 **查看** 并复制

**获取Agent ID：**
1. 在同一页面找到 **基础信息**
2. 记录 **AgentId**：`123456789`（复制）

#### 1.4 配置事件订阅（重要！）

1. 点击 **开发配置** → **事件订阅**
2. 选择 **Stream 模式推送**
3. 点击 **已完成接入，验证连接通道**
4. 点击 **保存**

#### 1.5 配置权限

1. 点击 **权限管理**
2. 搜索并开通以下权限：
   - ✅ `qyapi_chat_manage` - 消息管理
   - ✅ `qyapi_robot_sendmsg` - 机器人发送消息
   - ✅ `qyapi_get_user` - 获取用户信息（可选）
3. 点击 **确认**

### 步骤2：配置Add-on

1. 在Home Assistant中打开 **DingTalk Gateway** add-on
2. 点击 **配置** 标签
3. 填写配置信息：

```yaml
dingtalk_client_id: "dingxxxxxxxxxx"        # 从钉钉开发者后台复制
dingtalk_client_secret: "your_secret_here"  # 从钉钉开发者后台复制
dingtalk_agent_id: "123456789"              # 从钉钉开发者后台复制
use_stream: true                             # 使用Stream模式（推荐）
gateway_token: ""                            # 可选：设置API访问令牌
webhook_secret: ""                           # Webhook模式的密钥（Stream模式不需要）
```

#### 配置建议

**基础配置（必填）：**
- `dingtalk_client_id` - 必须填写
- `dingtalk_client_secret` - 必须填写
- `dingtalk_agent_id` - 必须填写
- `use_stream` - 保持 `true`

**安全配置（推荐）：**
- `gateway_token` - 建议设置一个随机字符串（20位以上）
  - 示例：`a8f3d9e2c7b6h5j4k1m9n0p2q3r8s7t6`
  - 用于保护API接口，防止未授权访问

**高级配置（可选）：**
- `webhook_secret` - 仅在使用Webhook模式时需要

### 步骤3：启动Add-on

1. 点击 **保存** 保存配置
2. 返回 **信息** 标签
3. 开启以下选项：
   - ✅ **开机启动** - 推荐开启
   - ✅ **看门狗** - 推荐开启（自动重启失败的服务）
   - ⬜ **显示在侧边栏** - 可选
4. 点击 **启动**

### 步骤4：验证运行

#### 查看日志

1. 点击 **日志** 标签
2. 正常运行应看到：

```
[INFO] Loading DingTalk Gateway configuration...
[INFO] Starting DingTalk Gateway...
[INFO] Stream mode: True
[INFO] Client ID: dingxxxxxx...
[INFO] [DingTalk] Client initialized
[INFO] [DingTalk] Starting Stream connection...
[INFO] open connection, url=https://api.dingtalk.com/v1.0/gateway/connections/open
[INFO] endpoint is {'endpoint': 'wss://wss-open-connection.dingtalk.com:443/connect', 'ticket': '...'}
[INFO] Gateway started on http://0.0.0.0:8099
```

#### 测试API

打开 **终端**（SSH或命令行工具）：

```bash
# 测试健康检查
curl http://homeassistant.local:8099/health

# 应该返回：
{"status":"ok","channel":"dingtalk"}
```

---

## 🚀 在Home Assistant中使用

### 方法1：配置REST Command

编辑 `configuration.yaml`：

```yaml
rest_command:
  send_dingtalk:
    url: "http://localhost:8099/send_message"
    method: POST
    headers:
      Content-Type: "application/json"
      X-Access-Token: "your_gateway_token_here"  # 如果配置了gateway_token
    payload: >
      {
        "target": "{{ userid }}",
        "content": "{{ message }}"
      }
```

重启Home Assistant后使用：

```yaml
service: rest_command.send_dingtalk
data:
  userid: "manager123"
  message: "前门已打开！"
```

### 方法2：在自动化中使用

```yaml
automation:
  - alias: "入侵检测通知"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion_sensor
        to: "on"
    condition:
      - condition: state
        entity_id: alarm_control_panel.home
        state: "armed_away"
    action:
      - service: rest_command.send_dingtalk
        data:
          userid: "manager123"
          message: "⚠️ 检测到异常移动！时间：{{ now().strftime('%H:%M:%S') }}"
```

### 方法3：获取用户ID

在钉钉中发送消息给机器人（需要@机器人），然后查看Add-on日志：

```
[INFO] Received message from 张三: 你好
```

日志中会显示用户名，但你需要通过钉钉API或开发者后台获取用户ID。

**或者使用钉钉开发者工具：**
1. 登录钉钉开发者后台
2. 进入 **权限管理** → **通讯录管理**
3. 查看用户列表，获取 `userid`

---

## 🔧 常见问题

### 问题1：安装失败

**症状**：点击安装后一直转圈或报错

**解决方法**：
1. 检查网络连接
2. 查看Supervisor日志：
   - 设置 → 系统 → 日志 → Supervisor
3. 确认Home Assistant版本 ≥ 2023.1
4. 尝试重启Supervisor

### 问题2：配置保存后无法启动

**症状**：点击启动后立即停止

**解决方法**：
1. 查看Add-on日志
2. 常见错误提示：
   ```
   DingTalk Client ID is required!
   ```
   说明配置项未填写或格式错误

3. 检查配置格式：
   - 字符串需要用引号包裹：`"value"`
   - 布尔值不需要引号：`true` 或 `false`
   - 不要有多余的空格

### 问题3：Stream连接超时

**症状**：日志显示
```
[ERROR] Failed to start Stream connection: timed out during opening handshake
```

**解决方法**：
1. 检查Home Assistant网络连接
2. 确认防火墙没有阻止443端口出站
3. 验证钉钉凭证是否正确
4. 确认钉钉开发者后台已启用Stream模式

### 问题4：收不到消息

**可能原因**：
1. 事件订阅未配置
2. 未@机器人（群聊中）
3. 应用权限不足

**解决方法**：
1. 检查钉钉开发者后台事件订阅配置
2. 在群聊中发送消息时需要@机器人
3. 检查应用权限是否开通
4. 查看Add-on日志是否有消息接收记录

### 问题5：无法发送消息

**可能原因**：
1. Agent ID错误
2. 目标用户不在应用可见范围
3. 权限不足

**解决方法**：
1. 核对Agent ID是否正确
2. 在钉钉开发者后台 → 应用可见范围 → 添加用户
3. 检查发送消息权限是否开通
4. 查看日志错误信息

### 问题6：API返回401错误

**症状**：调用API时返回
```json
{"detail":"Invalid access token"}
```

**解决方法**：
1. 如果配置了`gateway_token`，在请求头添加：
   ```
   X-Access-Token: your_token_here
   ```
2. 或者在Add-on配置中删除`gateway_token`（留空）

---

## 📊 监控和维护

### 查看运行状态

1. 进入 **设置** → **加载项** → **DingTalk Gateway**
2. 查看状态指示：
   - 🟢 绿色：运行正常
   - 🔴 红色：已停止
   - 🟡 黄色：启动中

### 查看资源使用

在Add-on详情页可以看到：
- CPU使用率
- 内存使用量
- 网络流量

正常情况下：
- CPU: < 5%
- 内存: 50-100MB
- 网络: 极小（长连接维持）

### 更新Add-on

**自动更新（推荐）**：
1. 开启 **自动更新**选项
2. Add-on会在有新版本时自动更新

**手动更新**：
1. 当有新版本时，会显示 **更新** 按钮
2. 点击更新
3. 等待完成后重启

### 备份和恢复

**包含在Home Assistant快照中**：
- Add-on配置会自动包含在系统快照中
- 恢复快照时会恢复Add-on配置

**导出配置**：
1. 进入Add-on配置页面
2. 复制配置内容保存到安全位置

---

## 🔐 安全最佳实践

### 1. 设置强密码

```yaml
gateway_token: "a8f3d9e2c7b6h5j4k1m9n0p2q3r8s7t6u5v4w3x2y1z0"
```

使用密码生成器创建随机字符串（推荐20位以上）。

### 2. 限制网络访问

如果不需要外网访问：
1. 在路由器防火墙中阻止8099端口外网访问
2. 仅允许内网设备访问

### 3. 定期更新

- 开启自动更新
- 关注GitHub releases获取安全更新通知

### 4. 保护凭证

- 不要在公共场合展示配置截图
- 不要将配置文件上传到公共仓库
- 如果泄露，立即在钉钉开发者后台重置Secret

---

## 📚 进阶配置

### 多应用支持

如果需要支持多个钉钉应用，可以：
1. 安装多个Add-on实例（不同端口）
2. 或使用反向代理路由到不同应用

### 自定义日志级别

暂时不支持通过UI配置，可以通过修改源码实现。

### 集成到Lovelace界面

创建自定义卡片显示消息历史（需要额外开发）。

---

## 🆘 获取帮助

### 文档资源

- **项目README**：[查看详细文档](https://github.com/yanfeng17/dingtalk-ha-gateway)
- **钉钉开放平台**：https://open.dingtalk.com/document/
- **Home Assistant文档**：https://www.home-assistant.io/docs/

### 报告问题

遇到Bug或有功能建议？

1. 查看 [已知问题](https://github.com/yanfeng17/dingtalk-ha-gateway/issues)
2. 提交新Issue：https://github.com/yanfeng17/dingtalk-ha-gateway/issues/new
3. 提供以下信息：
   - Home Assistant版本
   - Add-on版本
   - 完整错误日志
   - 复现步骤

### 社区支持

- **Home Assistant中文论坛**
- **钉钉开发者社区**
- **GitHub Discussions**

---

## ✅ 安装检查清单

完成以下检查确保安装成功：

- [ ] Home Assistant版本 ≥ 2023.1
- [ ] Supervisor可访问
- [ ] 钉钉应用已创建
- [ ] Client ID、Client Secret、Agent ID已获取
- [ ] 事件订阅配置为Stream模式
- [ ] 应用权限已开通
- [ ] Add-on已安装
- [ ] 配置已填写并保存
- [ ] Add-on已启动
- [ ] 日志显示"Gateway started"
- [ ] API健康检查通过
- [ ] REST Command已配置
- [ ] 测试消息发送成功

---

**祝你使用愉快！🎉**

如有问题，欢迎提Issue或PR。

**作者**: yanfeng17  
**项目地址**: https://github.com/yanfeng17/dingtalk-ha-gateway  
**更新时间**: 2025-12-05  
**版本**: v0.1.1
