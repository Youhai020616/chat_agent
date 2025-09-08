"""
KPI 快照模型
"""

from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel


class KPISnapshot(BaseModel):
    """KPI 快照"""
    __tablename__ = "kpi_snapshots"
    
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False)
    ts = Column(DateTime(timezone=True), nullable=False)
    gsc_data = Column(JSONB)  # Google Search Console 数据
    cwv_data = Column(JSONB)  # Core Web Vitals 数据
    ai_data = Column(JSONB)   # AI 提及数据
    gmb_data = Column(JSONB)  # Google My Business 数据
    
    # 关系
    site = relationship("Site", back_populates="kpi_snapshots")
