"""
优化行动计划模型
"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel


class ActionPlan(BaseModel):
    """优化行动计划"""
    __tablename__ = "action_plans"
    
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"), nullable=False)
    items = Column(JSONB, nullable=False)  # 行动项列表
    
    # 关系
    run = relationship("Run", back_populates="action_plans")
