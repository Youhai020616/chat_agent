# SEO & GEO 优化系统 - 后端服务

## 📁 项目结构

```
backend/
├── api/                 # FastAPI 应用 (REST + WebSocket/SSE)
├── workers/             # Celery 工作节点和后台任务
├── agents/              # 领域专家 Agent
│   ├── keyword/         # 关键词分析 Agent
│   ├── content/         # 内容优化 Agent
│   ├── technical/       # 技术 SEO Agent
│   ├── geo/             # 地理优化 Agent
│   └── link/            # 链接建设 Agent
├── graph/               # LangGraph 工作流编排
├── services/            # 外部服务集成
├── schemas/             # Pydantic 数据模型
├── models/              # 数据库模型 (SQLAlchemy)
├── scripts/             # 实用脚本
├── mock-data/           # 测试数据
├── tests/               # 单元和集成测试
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量示例
└── Dockerfile           # Docker 配置
```

## 🚀 快速开始

### 环境要求
- Python 3.10+
- PostgreSQL 15+
- Redis 6+
- RabbitMQ 3.12+

### 安装步骤

1. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
```

4. **初始化数据库**
```bash
alembic upgrade head
python scripts/init_db.py
```

5. **启动服务**

启动 API 服务：
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

启动 Celery Worker：
```bash
celery -A workers.celery_app worker --loglevel=info
```

启动 Celery Beat（定时任务）：
```bash
celery -A workers.celery_app beat --loglevel=info
```

## 🔧 开发指南

### 代码规范
- 使用 Black 格式化代码
- 使用 mypy 进行类型检查
- 遵循 PEP 8 规范

### 运行测试
```bash
pytest tests/
pytest tests/ --cov=.  # 带覆盖率报告
```

### 代码格式化
```bash
black .
isort .
flake8 .
mypy .
```

## 📚 API 文档

服务启动后，访问以下地址查看 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 环境变量

必需的环境变量：
- `DATABASE_URL`: PostgreSQL 连接字符串
- `REDIS_URL`: Redis 连接字符串
- `RABBITMQ_URL`: RabbitMQ 连接字符串
- `SECRET_KEY`: JWT 密钥
- `OPENAI_API_KEY`: OpenAI API 密钥
- `GOOGLE_API_KEY`: Google API 密钥
- 更多配置见 `.env.example`

## 🐳 Docker 部署

构建镜像：
```bash
docker build -t seo-geo-backend .
```

使用 docker-compose：
```bash
docker-compose up -d
```

## 📝 许可证

[MIT License](../LICENSE)
