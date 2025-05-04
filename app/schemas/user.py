from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

class UserCreate(UserBase):
    """用户创建模型"""
    password: str

class UserResponse(UserBase):
    """用户响应模型"""
    id: int

    class Config:
        from_attributes = True 