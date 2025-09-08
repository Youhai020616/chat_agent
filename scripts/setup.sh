#!/bin/bash

# 项目初始化脚本
# 用于设置开发环境和安装依赖

set -e

echo "🚀 开始初始化 SEO & GEO 优化系统..."

# 检查必要的工具
check_prerequisites() {
    echo "📋 检查必要工具..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 未安装，请先安装 Node.js 18+"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 未安装，请先安装 Python 3.11+"
        exit 1
    fi
    
    echo "✅ 所有必要工具已安装"
}

# 设置环境变量
setup_environment() {
    echo "🔧 设置环境变量..."
    
    if [ ! -f backend/.env ]; then
        cp backend/.env.example backend/.env
        echo "📄 已创建 backend/.env 文件，请编辑填入必要的 API 密钥"
    fi
    
    if [ ! -f frontend/.env.development ]; then
        cat > frontend/.env.development << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_APP_NAME=SEO & GEO 优化系统
EOF
        echo "📄 已创建 frontend/.env.development 文件"
    fi
}

# 安装前端依赖
setup_frontend() {
    echo "⚡ 安装前端依赖..."
    cd frontend
    npm install
    cd ..
    echo "✅ 前端依赖安装完成"
}

# 安装后端依赖
setup_backend() {
    echo "🐍 设置后端环境..."
    cd backend
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "📦 已创建 Python 虚拟环境"
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt
    
    cd ..
    echo "✅ 后端依赖安装完成"
}

# 初始化数据库
setup_database() {
    echo "🗄️ 初始化数据库..."
    
    # 启动数据库服务
    docker-compose up -d postgres redis
    
    # 等待数据库启动
    echo "⏳ 等待数据库启动..."
    sleep 10
    
    # 运行数据库迁移
    cd backend
    source venv/bin/activate
    # python manage.py migrate  # 根据实际情况调整
    cd ..
    
    echo "✅ 数据库初始化完成"
}

# 创建必要的目录
create_directories() {
    echo "📁 创建项目目录..."
    
    # 创建日志目录
    mkdir -p logs
    mkdir -p data/uploads
    mkdir -p data/exports
    
    # 创建前端构建目录
    mkdir -p frontend/dist
    
    echo "✅ 目录创建完成"
}

# 主函数
main() {
    echo "🎯 SEO & GEO 优化系统 - 项目初始化"
    echo "=================================="
    
    check_prerequisites
    setup_environment
    create_directories
    setup_frontend
    setup_backend
    setup_database
    
    echo ""
    echo "🎉 项目初始化完成！"
    echo ""
    echo "📋 下一步操作："
    echo "1. 编辑 backend/.env 文件，填入必要的 API 密钥"
    echo "2. 运行 ./scripts/dev.sh 启动开发环境"
    echo "3. 访问 http://localhost:3000 查看前端应用"
    echo "4. 访问 http://localhost:8000/docs 查看 API 文档"
    echo ""
    echo "📚 更多信息请查看 README.md"
}

# 执行主函数
main "$@"
