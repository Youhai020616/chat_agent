"""
应用配置

基于 Pydantic Settings 的配置管理
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """应用设置"""
    
    # 基础配置
    APP_NAME: str = "SEO & GEO Optimization API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://seo_geo_user:seo_geo_pass@localhost:5432/seo_geo_db"
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery 配置
    CELERY_BROKER_URL: str = "amqp://admin:admin123@localhost:5672/"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # OpenAI 配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.1
    
    # Google APIs 配置
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_CONSOLE_CLIENT_ID: Optional[str] = None
    GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET: Optional[str] = None
    
    # CORS 配置
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://localhost:3000"
    ]
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 爬虫配置
    CRAWLER_TIMEOUT: int = 30000  # 30 seconds
    CRAWLER_MAX_PAGES: int = 10
    CRAWLER_USER_AGENT: str = "Mozilla/5.0 (compatible; SEO-GEO-Bot/1.0)"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局设置实例
settings = Settings()
