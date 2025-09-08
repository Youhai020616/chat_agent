"""
FastAPI 主应用

SEO & GEO 优化系统的 API 入口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from .routers import sites, runs, analysis, kpis
from .config import settings
from .database import init_db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    logger.info("Initializing database...")
    await init_db()
    logger.info("Application startup complete")
    
    yield
    
    # 关闭时清理资源
    logger.info("Application shutdown")


# 创建 FastAPI 应用
app = FastAPI(
    title="SEO & GEO Optimization API",
    description="基于 LangGraph 的多 Agent SEO & GEO 优化系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "version": "1.0.0"}


# 注册路由
app.include_router(sites.router, prefix="/api/v1/sites", tags=["sites"])
app.include_router(runs.router, prefix="/api/v1/runs", tags=["runs"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(kpis.router, prefix="/api/v1/kpis", tags=["kpis"])


# 根路径
@app.get("/")
async def root():
    """API 根路径"""
    return {
        "message": "SEO & GEO Optimization API",
        "version": "1.0.0",
        "docs": "/docs"
    }
