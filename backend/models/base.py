"""
数据库基础模型
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

Base = declarative_base()


class TimestampMixin:
    """时间戳混入类"""
    created_at = Column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )


class UUIDMixin:
    """UUID 主键混入类"""
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        nullable=False
    )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """基础模型类"""
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        # 自动生成表名（类名转下划线）
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
    def to_dict(self):
        """转换为字典"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value
        return result
