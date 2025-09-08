"""
分析洞察模型
"""

from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel


class KeywordInsight(BaseModel):
    """关键词分析洞察"""
    __tablename__ = "keyword_insights"
    
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"), nullable=False)
    data = Column(JSONB, nullable=False)
    
    # 关系
    run = relationship("Run", back_populates="keyword_insights")


class ContentInsight(BaseModel):
    """内容分析洞察"""
    __tablename__ = "content_insights"
    
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"), nullable=False)
    data = Column(JSONB, nullable=False)
    
    # 关系
    run = relationship("Run", back_populates="content_insights")


class TechnicalInsight(BaseModel):
    """技术 SEO 洞察"""
    __tablename__ = "technical_insights"
    
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"), nullable=False)
    data = Column(JSONB, nullable=False)
    
    # 关系
    run = relationship("Run", back_populates="technical_insights")


class GeoInsight(BaseModel):
    """地理优化洞察"""
    __tablename__ = "geo_insights"
    
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"), nullable=False)
    data = Column(JSONB, nullable=False)
    
    # 关系
    run = relationship("Run", back_populates="geo_insights")


class LinkInsight(BaseModel):
    """链接分析洞察"""
    __tablename__ = "link_insights"
    
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"), nullable=False)
    data = Column(JSONB, nullable=False)
    
    # 关系
    run = relationship("Run", back_populates="link_insights")
