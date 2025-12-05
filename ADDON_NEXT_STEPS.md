# DingTalk Gateway Addon - 下一步操作指南

恭喜！🎉 所有Addon必需文件已创建完成。

## ✅ 已完成的工作

- ✅ **config.json** - Addon配置文件
- ✅ **Dockerfile** - 容器镜像定义
- ✅ **build.yaml** - 多架构构建配置
- ✅ **run.sh** - 启动脚本
- ✅ **.dockerignore** - Docker构建排除文件
- ✅ **repository.json** - 仓库元数据
- ✅ **DOCS.md** - Addon使用文档
- ✅ **ADDON_INSTALL.md** - 详细安装指南
- ✅ **gateway/config.py** - 已适配Addon环境

## 📋 下一步：本地测试

### 方式1：直接在HAOS上测试（推荐）

#### 步骤1：上传文件到HAOS

**使用Samba共享：**
1. 确保HAOS上安装了Samba add-on
2. 通过网络访问：
   - Windows: `\\homeassistant\addon\local`
   - macOS: `smb://homeassistant/addon/local`
3. 创建文件夹 `dingtalk-ha-gateway`
4. 将整个项目文件夹内容复制进去（**排除venv、__pycache__、.git等**）

**或使用SSH：**
```bash
# 在本地电脑执行
mkdir -p /addon/local
scp -r /path/to/dingtalk-ha-gateway root@homeassistant.local:/addon/local/
```

#### 步骤2：刷新加载项页面

1. 打开Home Assistant
2. 进入 **设置** → **加载项**
3. 刷新页面（Ctrl+F5）
4. 在 **本地加载项** 部分找到 **DingTalk Gateway**

**注意**：本地add-on会自动显示，无需添加仓库路径

#### 步骤3：安装测试

1. 在加载项商店找到 **DingTalk Gateway**（显示Local标签）
2. 点击安装
3. 配置钉钉凭证（参考ADDON_INSTALL.md）
4. 启动并查看日志
5. 测试消息收发

### 方式2：使用Docker本地构建测试

**前提**：本机安装Docker

```bash
# 1. 进入项目目录
cd dingtalk-ha-gateway

# 2. 构建镜像
docker build --build-arg BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest -t dingtalk-gateway:test .

# 3. 运行测试
docker run -it --rm \
  -e DINGTALK_CLIENT_ID="your_client_id" \
  -e DINGTALK_CLIENT_SECRET="your_secret" \
  -e DINGTALK_AGENT_ID="your_agent_id" \
  -e DINGTALK_USE_STREAM="true" \
  -p 8099:8099 \
  dingtalk-gateway:test

# 4. 测试API
curl http://localhost:8099/health
```

## 🚀 发布到GitHub

### 步骤1：准备图标

在发布前，需要替换占位符图标：

1. **准备图标文件**：
   - `icon.png` - 256x256 像素
   - `logo.png` - 512x512 像素
   - 建议使用钉钉相关图标

2. **替换文件**：
   ```bash
   # 删除占位符
   rm icon.png logo.png
   
   # 复制你的图标文件
   cp /path/to/your/icon.png .
   cp /path/to/your/logo.png .
   ```

### 步骤2：提交到Git

```bash
# 查看修改
git status

# 添加新文件
git add config.json Dockerfile build.yaml run.sh .dockerignore
git add repository.json DOCS.md ADDON_INSTALL.md ADDON_NEXT_STEPS.md
git add gateway/config.py

# 提交
git commit -m "Add Home Assistant Add-on support

- Add config.json for addon configuration
- Add Dockerfile for multi-arch build
- Add run.sh startup script
- Add comprehensive documentation
- Update config.py for addon compatibility

Co-authored-by: factory-droid[bot] <138933559+factory-droid[bot]@users.noreply.github.com>"

# 推送到GitHub
git push origin master
```

### 步骤3：创建Release（可选）

1. 访问GitHub仓库
2. 点击 **Releases** → **Create a new release**
3. 填写：
   - Tag: `v0.1.1`
   - Title: `v0.1.1 - Add Home Assistant Add-on Support`
   - 描述：添加版本更新说明
4. 发布

## 📦 用户安装方式

完成上述步骤后，用户可以通过以下方式安装：

### 方式A：通过GitHub URL

1. 打开Home Assistant
2. 进入 **设置** → **加载项** → **⋮** → **仓库**
3. 添加：`https://github.com/yanfeng17/dingtalk-ha-gateway`
4. 在加载项商店安装 **DingTalk Gateway**

### 方式B：本地安装

1. 下载项目文件到HAOS的 `/addons/` 目录
2. 添加本地仓库路径
3. 从加载项商店安装

## 🔍 测试检查清单

在发布前，确保测试以下功能：

- [ ] Addon能成功安装
- [ ] 配置界面显示正常
- [ ] 配置参数能正确保存
- [ ] Addon能成功启动
- [ ] 日志显示Stream连接成功
- [ ] 能接收钉钉消息
- [ ] 能发送消息到钉钉
- [ ] API健康检查正常（/health）
- [ ] REST Command调用正常
- [ ] 重启后自动启动（如果启用）
- [ ] 看门狗能检测并重启异常服务

## ⚠️ 注意事项

### 1. 敏感信息保护

确保以下文件**不要**提交到Git：
- `.env` - 包含真实凭证
- `venv/` - Python虚拟环境
- `__pycache__/` - Python缓存
- `.git/` 中的本地配置

### 2. 图标文件

- 当前的 `icon.png` 和 `logo.png` 是占位符
- 发布前务必替换为实际图标
- 推荐尺寸：
  - icon.png: 256x256 px
  - logo.png: 512x512 px

### 3. 版本管理

更新时需要同步修改：
- `config.json` 中的 `version`
- `Dockerfile` 中的 `LABEL io.hass.version`
- Git tag

### 4. 多架构支持

目前配置支持以下架构：
- aarch64 (ARM 64位，如树莓派4)
- amd64 (x86_64，如NUC)
- armhf (ARM 32位)
- armv7 (ARMv7)
- i386 (32位x86)

如需调整，修改 `config.json` 中的 `arch` 字段。

## 📚 相关文档

- **用户文档**：`ADDON_INSTALL.md` - 详细安装指南
- **Addon说明**：`DOCS.md` - 在HA界面显示的文档
- **项目README**：`README.md` - 项目整体说明
- **AWS部署**：`AWS_DEPLOYMENT.md` - 云服务器部署（可选）

## 🐛 遇到问题？

### 构建失败

**检查Dockerfile**：
- 确认基础镜像可访问
- 确认所有依赖都在requirements.txt中
- 尝试手动构建测试

### 启动失败

**查看日志**：
```bash
# 在HAOS上查看系统日志
ha addons logs dingtalk_gateway
```

**常见原因**：
- 配置参数未填写
- 环境变量读取失败
- Python依赖缺失
- 端口冲突

### Stream连接失败

**检查网络**：
- HAOS网络配置
- 防火墙规则
- DNS解析

**检查凭证**：
- Client ID/Secret是否正确
- 钉钉开发者后台配置

## 🎯 后续优化建议

### 功能增强

1. **添加配置选项**：
   - 日志级别
   - 超时时间
   - 重连策略

2. **消息功能**：
   - 支持图片消息
   - 支持卡片消息
   - 消息模板

3. **监控功能**：
   - 连接状态sensor
   - 消息统计
   - 错误通知

### 用户体验

1. **Ingress支持**：
   - 添加Web管理界面
   - 在HA侧边栏显示

2. **多语言**：
   - 英文翻译
   - 界面本地化

3. **示例自动化**：
   - 提供YAML模板
   - 一键导入

## ✅ 发布前最终检查

- [ ] 所有TODO项已完成
- [ ] 代码已测试通过
- [ ] 文档已更新
- [ ] 图标已替换
- [ ] 敏感信息已清理
- [ ] .gitignore配置正确
- [ ] Git提交信息清晰
- [ ] GitHub仓库README已更新
- [ ] Release notes已准备

---

## 🎉 完成！

你现在已经将DingTalk Gateway成功转换为Home Assistant Add-on！

**接下来**：
1. 本地测试所有功能
2. 提交代码到GitHub
3. 通知用户可以安装使用
4. 收集反馈持续改进

**祝你成功！** 🚀

如有问题，欢迎查看项目文档或提交Issue。

---

**项目地址**: https://github.com/yanfeng17/dingtalk-ha-gateway  
**作者**: yanfeng17  
**更新时间**: 2025-12-05
