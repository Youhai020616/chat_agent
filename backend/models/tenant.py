"""
租户和用户模型
"""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Tenant(BaseModel):
    """租户模型"""
    __tablename__ = "tenants"
    
    name = Column(String(255), nullable=False)
    
    # 关系
    users = relationship("User", back_populates="tenant")
    sites = relationship("Site", back_populates="tenant")


class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"
    
    email = Column(String(255), nullable=False, unique=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # 关系
    tenant = relationship("Tenant", back_populates="users")
