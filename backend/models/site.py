"""
站点模型
"""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Site(BaseModel):
    """站点模型"""
    __tablename__ = "sites"
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    url = Column(String(2048), nullable=False)
    locale = Column(String(10), default="en-US", nullable=False)
    
    # 关系
    tenant = relationship("Tenant", back_populates="sites")
    runs = relationship("Run", back_populates="site")
    kpi_snapshots = relationship("KPISnapshot", back_populates="site")
