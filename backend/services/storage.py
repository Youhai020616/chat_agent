"""
数据存储服务

提供数据库操作的高级接口
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import uuid
import logging

from ..models import (
    Site, Run, Tenant, User,
    KeywordInsight, ContentInsight, TechnicalInsight, 
    GeoInsight, LinkInsight, ActionPlan, KPISnapshot
)
from ..graph.state import SEOState

logger = logging.getLogger(__name__)


class StorageService:
    """数据存储服务"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create_run(self, site_id: str, target_url: str, locale: str = "en-US") -> str:
        """创建新的分析运行"""
        try:
            run = Run(
                site_id=uuid.UUID(site_id),
                status="pending",
                progress=0.0
            )
            
            self.db.add(run)
            await self.db.commit()
            await self.db.refresh(run)
            
            logger.info(f"Created run {run.id} for site {site_id}")
            return str(run.id)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create run: {str(e)}")
            raise
    
    async def get_run(self, run_id: str) -> Optional[Run]:
        """获取运行记录"""
        try:
            result = await self.db.execute(
                select(Run)
                .options(selectinload(Run.site))
                .where(Run.id == uuid.UUID(run_id))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get run {run_id}: {str(e)}")
            return None
    
    async def update_run_status(self, run_id: str, status: str, progress: float = None, error: str = None):
        """更新运行状态"""
        try:
            update_data = {"status": status}
            if progress is not None:
                update_data["progress"] = progress
            if error is not None:
                update_data["error"] = error
            
            await self.db.execute(
                update(Run)
                .where(Run.id == uuid.UUID(run_id))
                .values(**update_data)
            )
            await self.db.commit()
            
            logger.info(f"Updated run {run_id} status to {status}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update run status: {str(e)}")
            raise
    
    async def save_keyword_insights(self, run_id: str, data: Dict[str, Any]):
        """保存关键词分析结果"""
        try:
            insight = KeywordInsight(
                run_id=uuid.UUID(run_id),
                data=data
            )
            self.db.add(insight)
            await self.db.commit()
            
            logger.info(f"Saved keyword insights for run {run_id}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to save keyword insights: {str(e)}")
            raise
    
    async def save_content_insights(self, run_id: str, data: Dict[str, Any]):
        """保存内容分析结果"""
        try:
            insight = ContentInsight(
                run_id=uuid.UUID(run_id),
                data=data
            )
            self.db.add(insight)
            await self.db.commit()
            
            logger.info(f"Saved content insights for run {run_id}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to save content insights: {str(e)}")
            raise
    
    async def save_technical_insights(self, run_id: str, data: Dict[str, Any]):
        """保存技术 SEO 分析结果"""
        try:
            insight = TechnicalInsight(
                run_id=uuid.UUID(run_id),
                data=data
            )
            self.db.add(insight)
            await self.db.commit()
            
            logger.info(f"Saved technical insights for run {run_id}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to save technical insights: {str(e)}")
            raise
    
    async def save_geo_insights(self, run_id: str, data: Dict[str, Any]):
        """保存地理优化分析结果"""
        try:
            insight = GeoInsight(
                run_id=uuid.UUID(run_id),
                data=data
            )
            self.db.add(insight)
            await self.db.commit()

            logger.info(f"Saved geo insights for run {run_id}")

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to save geo insights: {str(e)}")
            raise

    async def save_local_seo_insights(self, run_id: str, data: Dict[str, Any]):
        """保存本地SEO分析结果"""
        try:
            # 使用通用的GeoInsight表存储，添加类型标识
            insight_data = {
                "type": "local_seo",
                "data": data
            }
            insight = GeoInsight(
                run_id=uuid.UUID(run_id),
                data=insight_data
            )
            self.db.add(insight)
            await self.db.commit()

            logger.info(f"Saved local SEO insights for run {run_id}")

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to save local SEO insights: {str(e)}")
            raise

    async def save_gmb_insights(self, run_id: str, data: Dict[str, Any]):
        """保存GMB分析结果"""
        try:
            insight_data = {
                "type": "gmb",
                "data": data
            }
            insight = GeoInsight(
                run_id=uuid.UUID(run_id),
                data=insight_data
            )
            self.db.add(insight)
            await self.db.commit()

            logger.info(f"Saved GMB insights for run {run_id}")

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to save GMB insights: {str(e)}")
            raise

    async def save_geo_content_insights(self, run_id: str, data: Dict[str, Any]):
        """保存地理内容分析结果"""
        try:
            insight_data = {
                "type": "geo_content",
                "data": data
            }
            insight = GeoInsight(
                run_id=uuid.UUID(run_id),
                data=insight_data
            )
            self.db.add(insight)
            await self.db.commit()

            logger.info(f"Saved geo content insights for run {run_id}")

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to save geo content insights: {str(e)}")
            raise

    async def save_competitor_insights(self, run_id: str, data: Dict[str, Any]):
        """保存竞争对手分析结果"""
        try:
            # 使用通用的ContentInsight表存储，添加类型标识
            insight_data = {
                "type": "competitor",
                "data": data
            }
            insight = ContentInsight(
                run_id=uuid.UUID(run_id),
                data=insight_data
            )
            self.db.add(insight)
            await self.db.commit()

            logger.info(f"Saved competitor insights for run {run_id}")

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to save competitor insights: {str(e)}")
            raise
    
    async def save_link_insights(self, run_id: str, data: Dict[str, Any]):
        """保存链接分析结果"""
        try:
            insight = LinkInsight(
                run_id=uuid.UUID(run_id),
                data=data
            )
            self.db.add(insight)
            await self.db.commit()
            
            logger.info(f"Saved link insights for run {run_id}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to save link insights: {str(e)}")
            raise
    
    async def save_action_plan(self, run_id: str, items: List[Dict[str, Any]]):
        """保存优化行动计划"""
        try:
            action_plan = ActionPlan(
                run_id=uuid.UUID(run_id),
                items=items
            )
            self.db.add(action_plan)
            await self.db.commit()
            
            logger.info(f"Saved action plan for run {run_id}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to save action plan: {str(e)}")
            raise
    
    async def get_run_results(self, run_id: str) -> Optional[Dict[str, Any]]:
        """获取运行的完整结果"""
        try:
            # 获取运行记录
            run = await self.get_run(run_id)
            if not run:
                return None
            
            # 获取各种洞察
            keyword_result = await self.db.execute(
                select(KeywordInsight).where(KeywordInsight.run_id == uuid.UUID(run_id))
            )
            keyword_insight = keyword_result.scalar_one_or_none()
            
            content_result = await self.db.execute(
                select(ContentInsight).where(ContentInsight.run_id == uuid.UUID(run_id))
            )
            content_insight = content_result.scalar_one_or_none()
            
            technical_result = await self.db.execute(
                select(TechnicalInsight).where(TechnicalInsight.run_id == uuid.UUID(run_id))
            )
            technical_insight = technical_result.scalar_one_or_none()
            
            geo_result = await self.db.execute(
                select(GeoInsight).where(GeoInsight.run_id == uuid.UUID(run_id))
            )
            geo_insight = geo_result.scalar_one_or_none()
            
            link_result = await self.db.execute(
                select(LinkInsight).where(LinkInsight.run_id == uuid.UUID(run_id))
            )
            link_insight = link_result.scalar_one_or_none()
            
            action_plan_result = await self.db.execute(
                select(ActionPlan).where(ActionPlan.run_id == uuid.UUID(run_id))
            )
            action_plan = action_plan_result.scalar_one_or_none()
            
            return {
                "run": run.to_dict(),
                "keyword_insights": keyword_insight.data if keyword_insight else None,
                "content_insights": content_insight.data if content_insight else None,
                "technical_insights": technical_insight.data if technical_insight else None,
                "geo_insights": geo_insight.data if geo_insight else None,
                "link_insights": link_insight.data if link_insight else None,
                "action_plan": action_plan.items if action_plan else None,
            }
            
        except Exception as e:
            logger.error(f"Failed to get run results: {str(e)}")
            return None
