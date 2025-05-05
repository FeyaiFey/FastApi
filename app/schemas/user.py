from typing import Optional
from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime

class UserBase(BaseModel):
    """用户模型"""
    Id: uuid.UUID
    UserName: str
    Email: EmailStr
    DepartmentId: uuid.UUID
    Role: str
    Status: str
    AvatarUrl: str
    CreatedAt: datetime
    UpdatedAt: datetime
    
class UserLogin(BaseModel):
    """用户登录模型"""
    Email: EmailStr
    Password: str

class UserRegister(BaseModel):
    """用户注册模型"""
    UserName: str
    Email: EmailStr
    Password: str
    ConfirmPassword: str
    DepartmentId: uuid.UUID

class UserInfo(BaseModel):
    """用户信息模型"""
    Id: uuid.UUID
    UserName: str
    Email: EmailStr
    DepartmentName: str
    Role: str
    AvatarUrl: str
    
class UserLoginResponse(UserInfo):
    """用户登录响应模型"""
    token: str
