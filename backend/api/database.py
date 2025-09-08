"""
数据库连接和会话管理
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging

from .config import settings
from ..models.base import Base

logger = logging.getLogger(__name__)

# 异步数据库引擎
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
)

# 同步数据库引擎（用于 Alembic 迁移）
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 同步会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)


async def init_db():
    """初始化数据库"""
    try:
        async with async_engine.begin() as conn:
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db():
    """获取同步数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
