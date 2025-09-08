"""
分析运行 API 路由
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ...services.storage import StorageService

router = APIRouter()


class RunResponse(BaseModel):
    """运行响应模型"""
    id: str
    site_id: str
    status: str
    progress: float
    started_at: Optional[str]
    finished_at: Optional[str]
    error: Optional[str]


class RunResultsResponse(BaseModel):
    """运行结果响应模型"""
    run: RunResponse
    keyword_insights: Optional[Dict[str, Any]]
    content_insights: Optional[Dict[str, Any]]
    technical_insights: Optional[Dict[str, Any]]
    geo_insights: Optional[Dict[str, Any]]
    link_insights: Optional[Dict[str, Any]]
    action_plan: Optional[List[Dict[str, Any]]]


@router.get("/", response_model=List[RunResponse])
async def list_runs(
    site_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取运行列表"""
    try:
        # TODO: 实现运行列表查询
        return []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取运行详情"""
    try:
        storage = StorageService(db)
        run = await storage.get_run(run_id)
        
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        
        return RunResponse(
            id=str(run.id),
            site_id=str(run.site_id),
            status=run.status,
            progress=run.progress,
            started_at=run.started_at.isoformat() if run.started_at else None,
            finished_at=run.finished_at.isoformat() if run.finished_at else None,
            error=run.error
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{run_id}/results", response_model=RunResultsResponse)
async def get_run_results(
    run_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取运行结果"""
    try:
        storage = StorageService(db)
        results = await storage.get_run_results(run_id)
        
        if not results:
            raise HTTPException(status_code=404, detail="Run results not found")
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{run_id}")
async def delete_run(
    run_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除运行记录"""
    try:
        # TODO: 实现运行删除逻辑
        return {"message": "Run deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
