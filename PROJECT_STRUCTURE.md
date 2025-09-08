# 项目结构 - 前后端分离架构

## 📁 根目录结构

```
chat_agent/
├── frontend/              # 前端 React 应用
├── backend/               # 后端 Python 应用
├── docs/                  # 项目文档
├── docker-compose.yml     # Docker 编排配置
├── README.md              # 项目说明
├── PROJECT_STRUCTURE.md   # 本文件
├── WARP.md                # Warp 开发指南
└── .gitignore             # Git 忽略配置
```

## 🔧 后端结构 (Backend)

```
backend/
├── api/                   # FastAPI 应用 (REST + WebSocket/SSE)
│   └── README.md
├── workers/               # Celery 工作节点和后台任务
│   └── README.md
├── agents/                # 领域专家 Agent
│   ├── keyword/           # 关键词分析 Agent
│   ├── content/           # 内容优化 Agent
│   ├── technical/         # 技术 SEO Agent
│   ├── geo/               # 地理优化 Agent
│   └── link/              # 链接建设 Agent
├── graph/                 # LangGraph 工作流编排
│   └── README.md
├── services/              # 外部服务集成
│   └── README.md
├── schemas/               # Pydantic 数据模型
│   └── README.md
├── models/                # 数据库模型 (SQLAlchemy)
│   └── README.md
├── scripts/               # 实用脚本
│   └── README.md
├── mock-data/             # 测试数据
│   └── README.md
├── tests/                 # 单元和集成测试
├── requirements.txt       # Python 依赖
├── .env.example           # 环境变量示例
├── Dockerfile             # Docker 配置
└── README.md              # 后端说明文档
```

## ⚡ 前端结构 (Frontend)

```
frontend/
├── src/                   # 源代码
│   ├── api/               # API 客户端和服务层
│   │   ├── client.ts
│   │   ├── services/
│   │   └── types/
│   ├── streams/           # SSE/WebSocket 实时通信
│   ├── stores/            # Zustand 状态管理
│   ├── pages/             # 页面组件
│   │   ├── Dashboard/
│   │   ├── Analysis/
│   │   ├── Results/
│   │   └── KPI/
│   ├── features/          # 业务功能模块
│   │   ├── batch-analysis/
│   │   ├── agent-flow/
│   │   └── optimization/
│   ├── components/        # 通用 UI 组件
│   ├── hooks/             # 自定义 React Hooks
│   ├── types/             # TypeScript 类型定义
│   ├── utils/             # 工具函数
│   └── i18n/              # 国际化配置
├── public/                # 静态资源
├── tests/                 # 前端测试
├── package.json           # 前端依赖管理
├── vite.config.ts         # Vite 配置
├── tsconfig.json          # TypeScript 配置
├── tailwind.config.js     # Tailwind CSS 配置
├── .env.development       # 开发环境变量
├── .env.production        # 生产环境变量
├── Dockerfile             # Docker 配置
└── setup.sh               # 初始化脚本
```

## 📚 文档结构 (Documentation)

```
docs/
├── README.md              # 文档导航
├── architecture/          # 架构文档
│   ├── README.md          # 架构编目索引
│   ├── system-catalog.yml # 系统架构编目
│   ├── data-catalog.yml   # 数据模型编目
│   ├── frontend-catalog.yml # 前端组件编目
│   ├── integration-catalog.yml # 集成架构编目
│   ├── project-overview.md # 项目概览
│   ├── frontend-architecture.md # 前端架构设计
│   └── diagrams.md        # 系统架构图
├── api/                   # API 文档
│   └── api-specification.md # API 接口规范
├── methodology/           # 方法论文档
│   └── geo.md             # GEO 方法论
└── guides/                # 实施指南
```

## 🚫 Git 忽略规则

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/

# Node
node_modules/
dist/
build/
*.log

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
.dockerignore
```

## 🏃 快速启动

### 使用 Docker Compose
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]
```

### 本地开发

**后端:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

**前端:**
```bash
cd frontend
npm install  # 或 ./setup.sh
npm run dev
```

## 🔗 服务访问

- 前端应用: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- RabbitMQ: http://localhost:15672
- Flower: http://localhost:5555

