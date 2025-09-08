# SEO & GEO 优化系统

> 基于 LangGraph 的多 Agent SEO & GEO 智能优化平台

## 🎯 项目简介

本项目是一个利用 AI 技术的智能化 SEO（搜索引擎优化）和 GEO（地理位置优化）系统。通过多个专业化的 AI Agent 协作，为网站提供全面的优化分析和建议。

### 核心特性

- 🤖 **多 Agent 协作**：5个专业化Agent（关键词、内容、技术、地理、链接）并行分析
- 🔄 **LangGraph 编排**：灵活的工作流管理和状态共享
- 📊 **实时分析**：SSE推送任务进度，实时查看分析结果
- 🌍 **地理优化**：本地搜索优化、Google My Business集成
- 📈 **KPI 监控**：持续跟踪优化效果和关键指标
- 🔐 **企业级架构**：前后端分离、微服务架构、容器化部署

## 🏗️ 技术栈

### 后端
- **框架**: FastAPI (Python 3.11+)
- **AI框架**: LangGraph + LangChain
- **数据库**: PostgreSQL 15+
- **缓存**: Redis 7+
- **消息队列**: RabbitMQ + Celery
- **AI服务**: OpenAI GPT-4 / Azure OpenAI

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI框架**: TailwindCSS + HeadlessUI
- **状态管理**: Zustand + React Query
- **可视化**: Recharts + React Flow

### DevOps
- **容器化**: Docker + Docker Compose
- **API网关**: Kong Gateway
- **监控**: Prometheus + Grafana
- **日志**: ELK Stack
- **CI/CD**: GitHub Actions

## 📁 项目结构

```
chat_agent/
├── frontend/               # 前端 React 应用
│   ├── src/               # 源代码
│   ├── public/            # 静态资源
│   └── setup.sh           # 前端初始化脚本
├── backend/               # 后端 Python 应用
│   ├── api/               # FastAPI 接口
│   ├── agents/            # AI Agents
│   ├── workers/           # Celery 任务
│   ├── graph/             # LangGraph 工作流
│   └── requirements.txt   # Python 依赖
├── docs/                  # 项目文档
│   ├── architecture/      # 架构文档
│   ├── api/              # API 文档
│   └── methodology/       # 方法论文档
├── docker-compose.yml     # Docker 编排配置
└── README.md             # 本文件
```

## 🚀 快速开始

### 前置要求

- Docker & Docker Compose
- Node.js 18+ (前端开发)
- Python 3.11+ (后端开发)

### 1. 克隆项目

```bash
git clone https://github.com/your-org/chat_agent.git
cd chat_agent
```

### 2. 使用 Docker Compose 启动

```bash
# 复制环境变量文件
cp backend/.env.example backend/.env
# 编辑 .env 文件，填入必要的 API 密钥

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 访问服务

- 前端应用: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- RabbitMQ 管理界面: http://localhost:15672 (admin/admin123)
- Flower (Celery监控): http://localhost:5555

## 🛠️ 开发指南

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

详见 [前端 README](frontend/README.md)

### 后端开发

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

详见 [后端 README](backend/README.md)

## 📚 文档

- [架构设计](docs/architecture/)
  - [系统架构编目](docs/architecture/system-catalog.yml)
  - [数据模型设计](docs/architecture/data-catalog.yml)
  - [前端架构设计](docs/architecture/frontend-architecture.md)
  - [API 接口规范](docs/api/api-specification.md)
- [GEO 方法论](docs/methodology/geo.md)
- [开发指南](WARP.md)

## 🔧 配置说明

### 必需的环境变量

```env
# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Google APIs
GOOGLE_API_KEY=your-google-api-key
GOOGLE_SEARCH_CONSOLE_CLIENT_ID=your-client-id
GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET=your-client-secret

# 数据库
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# 更多配置见 backend/.env.example
```

## 🧪 测试

### 运行后端测试
```bash
cd backend
pytest tests/
```

### 运行前端测试
```bash
cd frontend
npm test
```

## 📊 系统架构图

```mermaid
graph TB
    FE[React Frontend] --> GW[API Gateway]
    GW --> API[FastAPI Backend]
    API --> WORKER[Celery Workers]
    WORKER --> LG[LangGraph]
    LG --> AGENTS[AI Agents]
    API --> DB[(PostgreSQL)]
    API --> CACHE[(Redis)]
    WORKER --> MQ[RabbitMQ]
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👥 团队

- 项目负责人: [Your Name]
- 技术负责人: [Tech Lead]
- AI 工程师: [AI Engineer]
- 前端开发: [Frontend Dev]
- 后端开发: [Backend Dev]

## 📞 联系我们

- Email: contact@seo-geo-system.com
- Issues: [GitHub Issues](https://github.com/your-org/chat_agent/issues)

---

⭐ 如果这个项目对您有帮助，请给我们一个 Star！
