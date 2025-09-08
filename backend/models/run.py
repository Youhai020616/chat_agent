"""
分析运行模型
"""

from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Run(BaseModel):
    """分析运行模型"""
    __tablename__ = "runs"
    
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, running, completed, failed
    progress = Column(Float, default=0.0, nullable=False)
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    error = Column(Text)
    
    # 关系
    site = relationship("Site", back_populates="runs")
    keyword_insights = relationship("KeywordInsight", back_populates="run")
    content_insights = relationship("ContentInsight", back_populates="run")
    technical_insights = relationship("TechnicalInsight", back_populates="run")
    geo_insights = relationship("GeoInsight", back_populates="run")
    link_insights = relationship("LinkInsight", back_populates="run")
    action_plans = relationship("ActionPlan", back_populates="run")
