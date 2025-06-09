from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
import uuid
from app.core.database import Base

class BaseModel(Base):
    """所有模型的基类"""
    __abstract__ = True

    Id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid1, index=True)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    UpdatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        """将模型转换为字典"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        } 