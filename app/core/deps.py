from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.security import verify_token
from app.exceptions.base import AuthenticationError
from app.core.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """获取当前用户"""
    # 验证令牌
    payload = verify_token(token)
    if not payload:
        raise AuthenticationError(message="无效的认证令牌")
    
    # 获取用户ID
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError(message="无效的认证令牌")
    
    # 获取用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AuthenticationError(message="用户不存在")
    
    if not user.is_active:
        raise AuthenticationError(message="用户已被禁用")
    
    return user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前超级用户"""
    if not current_user.is_superuser:
        raise AuthenticationError(message="权限不足")
    return current_user 