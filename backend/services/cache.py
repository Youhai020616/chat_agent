"""
Redis 缓存服务

提供分布式缓存和会话存储
"""

import json
import logging
from typing import Any, Optional, Dict
from datetime import timedelta
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class CacheService:
    """Redis 缓存服务"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """连接到 Redis"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # 测试连接
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
    
    async def disconnect(self):
        """断开 Redis 连接"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            if not self.redis_client:
                await self.connect()
            
            # 序列化值
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            elif not isinstance(value, str):
                value = str(value)
            
            # 设置值
            result = await self.redis_client.set(key, value, ex=expire)
            return result
            
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {str(e)}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            if not self.redis_client:
                await self.connect()
            
            value = await self.redis_client.get(key)
            if value is None:
                return None
            
            # 尝试反序列化 JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {str(e)}")
            return None
    
    async def delete(self, key: str) -> bool:
        """删除缓存键"""
        try:
            if not self.redis_client:
                await self.connect()
            
            result = await self.redis_client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            if not self.redis_client:
                await self.connect()
            
            result = await self.redis_client.exists(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to check cache key {key}: {str(e)}")
            return False
    
    async def set_run_status(self, run_id: str, status: Dict[str, Any], expire: int = 3600):
        """设置运行状态"""
        key = f"run_status:{run_id}"
        return await self.set(key, status, expire)
    
    async def get_run_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """获取运行状态"""
        key = f"run_status:{run_id}"
        return await self.get(key)
    
    async def set_crawl_cache(self, url: str, data: Dict[str, Any], expire: int = 1800):
        """缓存爬虫结果（30分钟）"""
        key = f"crawl:{hash(url)}"
        return await self.set(key, data, expire)
    
    async def get_crawl_cache(self, url: str) -> Optional[Dict[str, Any]]:
        """获取爬虫缓存"""
        key = f"crawl:{hash(url)}"
        return await self.get(key)
    
    async def set_agent_cache(self, agent_name: str, url: str, data: Dict[str, Any], expire: int = 3600):
        """缓存 Agent 结果（1小时）"""
        key = f"agent:{agent_name}:{hash(url)}"
        return await self.set(key, data, expire)
    
    async def get_agent_cache(self, agent_name: str, url: str) -> Optional[Dict[str, Any]]:
        """获取 Agent 缓存"""
        key = f"agent:{agent_name}:{hash(url)}"
        return await self.get(key)


# 全局缓存实例
cache_service: Optional[CacheService] = None


async def get_cache() -> CacheService:
    """获取缓存服务实例"""
    global cache_service
    if cache_service is None:
        from ..api.config import settings
        cache_service = CacheService(settings.REDIS_URL)
        await cache_service.connect()
    return cache_service
