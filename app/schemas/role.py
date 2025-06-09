from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class RoleBase(BaseModel):
    """角色基础模型"""
    RoleName: str = Field(..., min_length=1, max_length=50, description="角色名称")
    RoleCode: str = Field(..., min_length=1, max_length=50, description="角色代码")
    Description: Optional[str] = Field(None, description="角色描述")
    Status: str = Field("1", description="状态:0-禁用;1-启用")