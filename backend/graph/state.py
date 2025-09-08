"""
SEO 全局状态定义

基于 LangGraph 的状态管理，所有 Agent 共享此状态
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class SEOState:
    """SEO 分析的全局状态"""
    
    # 输入参数
    target_url: str
    locale: str = "en-US"
    site_id: Optional[str] = None
    run_id: Optional[str] = None
    
    # 爬虫数据
    crawl_data: Optional[Dict[str, Any]] = None
    crawl_status: str = "pending"  # pending, running, completed, failed
    
    # Agent 分析结果
    keyword_insights: Optional[Dict[str, Any]] = None
    content_insights: Optional[Dict[str, Any]] = None
    technical_insights: Optional[Dict[str, Any]] = None
    geo_insights: Optional[Dict[str, Any]] = None
    link_insights: Optional[Dict[str, Any]] = None
    serp_insights: Optional[Dict[str, Any]] = None
    local_seo_insights: Optional[Dict[str, Any]] = None
    gmb_insights: Optional[Dict[str, Any]] = None
    geo_content_insights: Optional[Dict[str, Any]] = None
    
    # 集成结果
    optimization_plan: Optional[List[Dict[str, Any]]] = None
    
    # 执行状态
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    progress: float = 0.0
    status: str = "pending"  # pending, running, completed, failed
    error: Optional[str] = None
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_progress(self, progress: float, status: Optional[str] = None):
        """更新执行进度"""
        self.progress = min(100.0, max(0.0, progress))
        if status:
            self.status = status
    
    def mark_started(self):
        """标记开始执行"""
        self.started_at = datetime.utcnow()
        self.status = "running"
        self.progress = 0.0
    
    def mark_completed(self):
        """标记执行完成"""
        self.finished_at = datetime.utcnow()
        self.status = "completed"
        self.progress = 100.0
    
    def mark_failed(self, error: str):
        """标记执行失败"""
        self.finished_at = datetime.utcnow()
        self.status = "failed"
        self.error = error
    
    def get_completed_agents(self) -> List[str]:
        """获取已完成的 Agent 列表"""
        completed = []
        if self.crawl_data:
            completed.append("crawler")
        if self.keyword_insights:
            completed.append("keyword")
        if self.content_insights:
            completed.append("content")
        if self.technical_insights:
            completed.append("technical")
        if self.geo_insights:
            completed.append("geo")
        if self.link_insights:
            completed.append("link")
        if self.serp_insights:
            completed.append("serp")
        if self.local_seo_insights:
            completed.append("local_seo")
        if self.gmb_insights:
            completed.append("gmb")
        if self.geo_content_insights:
            completed.append("geo_content")
        return completed
