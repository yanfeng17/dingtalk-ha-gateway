#!/bin/bash
#
# DingTalk Gateway - AWS 自动部署脚本
# 用途：一键部署 DingTalk Gateway 到 Ubuntu 服务器
# 支持：Ubuntu 20.04/22.04
#

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  $1${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
}

# 检查是否以 root 运行
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "请不要以 root 用户运行此脚本！"
        print_info "正确用法: ./deploy.sh"
        exit 1
    fi
}

# 检查操作系统
check_os() {
    print_info "检查操作系统..."
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        if [[ "$ID" != "ubuntu" ]]; then
            print_warning "此脚本主要为 Ubuntu 设计，其他系统可能需要修改"
        fi
        print_success "操作系统: $PRETTY_NAME"
    else
        print_error "无法检测操作系统类型"
        exit 1
    fi
}

# 更新系统
update_system() {
    print_header "更新系统包"
    print_info "运行 apt update..."
    sudo apt update
    print_success "系统包列表已更新"
}

# 安装 Python 3.11
install_python() {
    print_header "安装 Python 3.11"
    
    # 检查 Python 3.11 是否已安装
    if command -v python3.11 &> /dev/null; then
        PYTHON_VERSION=$(python3.11 --version)
        print_success "Python 3.11 已安装: $PYTHON_VERSION"
        return
    fi
    
    print_info "安装 Python 3.11..."
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev
    
    print_success "Python 3.11 安装完成"
    python3.11 --version
}

# 安装 Git
install_git() {
    print_header "安装 Git"
    
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_success "Git 已安装: $GIT_VERSION"
        return
    fi
    
    print_info "安装 Git..."
    sudo apt install -y git
    print_success "Git 安装完成"
}

# 克隆代码
clone_repo() {
    print_header "克隆代码仓库"
    
    REPO_URL="https://github.com/yanfeng17/dingtalk-ha-gateway.git"
    TARGET_DIR="$HOME/dingtalk-ha-gateway"
    
    if [[ -d "$TARGET_DIR" ]]; then
        print_warning "目录 $TARGET_DIR 已存在"
        read -p "是否删除并重新克隆？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$TARGET_DIR"
            print_info "已删除旧目录"
        else
            print_info "跳过克隆，使用现有目录"
            return
        fi
    fi
    
    print_info "从 GitHub 克隆代码..."
    git clone "$REPO_URL" "$TARGET_DIR"
    print_success "代码克隆完成: $TARGET_DIR"
}

# 创建虚拟环境
create_venv() {
    print_header "创建 Python 虚拟环境"
    
    cd "$HOME/dingtalk-ha-gateway"
    
    if [[ -d "venv" ]]; then
        print_warning "虚拟环境已存在，跳过创建"
        return
    fi
    
    print_info "创建虚拟环境..."
    python3.11 -m venv venv
    print_success "虚拟环境创建完成"
}

# 安装依赖
install_dependencies() {
    print_header "安装 Python 依赖"
    
    cd "$HOME/dingtalk-ha-gateway"
    
    print_info "激活虚拟环境..."
    source venv/bin/activate
    
    print_info "升级 pip..."
    pip install --upgrade pip -q
    
    print_info "安装依赖包（这可能需要几分钟）..."
    pip install -r requirements.txt -q
    
    print_success "依赖安装完成"
    deactivate
}

# 配置环境变量
configure_env() {
    print_header "配置环境变量"
    
    cd "$HOME/dingtalk-ha-gateway"
    
    if [[ -f ".env" ]]; then
        print_warning ".env 文件已存在"
        read -p "是否重新配置？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "跳过配置"
            return
        fi
    fi
    
    print_info "复制配置模板..."
    cp .env.example .env
    
    print_info ""
    print_info "现在需要配置钉钉应用凭证"
    print_info "请访问钉钉开放平台获取: https://open-dev.dingtalk.com/"
    print_info ""
    
    read -p "请输入 DINGTALK_CLIENT_ID: " CLIENT_ID
    read -p "请输入 DINGTALK_CLIENT_SECRET: " CLIENT_SECRET
    read -p "请输入 DINGTALK_AGENT_ID: " AGENT_ID
    
    # 可选：API Token
    print_info ""
    print_info "是否设置 Gateway API Token？（推荐，增强安全性）"
    read -p "设置 Token？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        # 生成随机 token
        GATEWAY_TOKEN=$(openssl rand -hex 32)
        print_success "已生成随机 Token: $GATEWAY_TOKEN"
        print_warning "请保存此 Token，配置 HA 时需要使用！"
    else
        GATEWAY_TOKEN=""
    fi
    
    # 写入配置
    print_info "写入配置文件..."
    cat > .env << EOF
# Gateway Configuration
CHANNEL_TYPE=dingtalk

# Gateway Server Settings
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8099
GATEWAY_TOKEN=$GATEWAY_TOKEN

# DingTalk Configuration
DINGTALK_CLIENT_ID=$CLIENT_ID
DINGTALK_CLIENT_SECRET=$CLIENT_SECRET
DINGTALK_AGENT_ID=$AGENT_ID

# Connection Mode
DINGTALK_USE_STREAM=true
EOF
    
    print_success "配置文件已创建: .env"
}

# 测试运行
test_run() {
    print_header "测试运行"
    
    cd "$HOME/dingtalk-ha-gateway"
    
    print_info "启动 Gateway 进行测试（5秒后自动停止）..."
    print_info "如果看到 'Gateway started' 表示成功"
    print_info ""
    
    source venv/bin/activate
    timeout 5 python app.py || true
    deactivate
    
    print_info ""
    read -p "是否看到 'Gateway started' 消息？(Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_success "测试成功！"
    else
        print_error "测试失败，请检查配置"
        print_info "手动测试命令:"
        print_info "  cd $HOME/dingtalk-ha-gateway"
        print_info "  source venv/bin/activate"
        print_info "  python app.py"
        exit 1
    fi
}

# 设置 systemd 服务
setup_service() {
    print_header "设置 systemd 服务"
    
    SERVICE_FILE="/etc/systemd/system/dingtalk-gateway.service"
    
    if [[ -f "$SERVICE_FILE" ]]; then
        print_warning "服务文件已存在"
        read -p "是否覆盖？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "跳过服务设置"
            return
        fi
    fi
    
    print_info "创建 systemd 服务文件..."
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=DingTalk Home Assistant Gateway
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/dingtalk-ha-gateway
Environment="PATH=$HOME/dingtalk-ha-gateway/venv/bin"
ExecStart=$HOME/dingtalk-ha-gateway/venv/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    print_info "重新加载 systemd..."
    sudo systemctl daemon-reload
    
    print_info "启用服务（开机自启）..."
    sudo systemctl enable dingtalk-gateway
    
    print_info "启动服务..."
    sudo systemctl start dingtalk-gateway
    
    sleep 2
    
    print_info "检查服务状态..."
    if sudo systemctl is-active --quiet dingtalk-gateway; then
        print_success "服务已启动！"
        sudo systemctl status dingtalk-gateway --no-pager
    else
        print_error "服务启动失败"
        print_info "查看日志:"
        sudo journalctl -u dingtalk-gateway -n 20 --no-pager
        exit 1
    fi
}

# 显示部署信息
show_summary() {
    print_header "部署完成"
    
    # 获取公网 IP
    PUBLIC_IP=$(curl -s ifconfig.me || echo "无法获取")
    
    echo ""
    print_success "🎉 DingTalk Gateway 已成功部署！"
    echo ""
    echo "======================================"
    echo "📋 部署信息"
    echo "======================================"
    echo "服务器公网IP: $PUBLIC_IP"
    echo "Gateway URL: http://$PUBLIC_IP:8099"
    echo "安装目录: $HOME/dingtalk-ha-gateway"
    echo "配置文件: $HOME/dingtalk-ha-gateway/.env"
    echo ""
    echo "======================================"
    echo "🔧 常用命令"
    echo "======================================"
    echo "查看服务状态:"
    echo "  sudo systemctl status dingtalk-gateway"
    echo ""
    echo "查看实时日志:"
    echo "  sudo journalctl -u dingtalk-gateway -f"
    echo ""
    echo "重启服务:"
    echo "  sudo systemctl restart dingtalk-gateway"
    echo ""
    echo "停止服务:"
    echo "  sudo systemctl stop dingtalk-gateway"
    echo ""
    echo "======================================"
    echo "🔗 下一步"
    echo "======================================"
    echo "1. 确保 EC2 安全组开放了 8099 端口"
    echo "2. 在 Home Assistant 中配置 Gateway URL"
    echo "3. 测试消息收发功能"
    echo ""
    
    if [[ -n "$GATEWAY_TOKEN" ]]; then
        echo "⚠️  重要：你设置了 API Token"
        echo "Token: $GATEWAY_TOKEN"
        echo "请在 HA 中配置此 Token"
        echo ""
    fi
    
    echo "📚 查看完整文档:"
    echo "  https://github.com/yanfeng17/dingtalk-ha-gateway/blob/master/AWS_DEPLOYMENT.md"
    echo ""
}

# 主函数
main() {
    print_header "DingTalk Gateway 自动部署脚本"
    
    print_info "此脚本将自动部署 DingTalk Gateway 到你的服务器"
    print_info "整个过程大约需要 5-10 分钟"
    print_info ""
    read -p "是否继续？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "部署已取消"
        exit 0
    fi
    
    check_root
    check_os
    update_system
    install_python
    install_git
    clone_repo
    create_venv
    install_dependencies
    configure_env
    test_run
    setup_service
    show_summary
    
    print_success "全部完成！"
}

# 运行主函数
main "$@"
