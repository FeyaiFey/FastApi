from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.exceptions.base import AuthenticationError
from app.core.config import settings
from app.core.database import get_db, get_db_session
from app.models.user import User
from app.services.auth import auth_service
from app.core.logger import get_logger

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    db: Session = Depends(get_db_session),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    获取当前用户
    - 验证JWT token
    - 验证Redis中的token
    - 返回用户信息
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 获取用户信息
    user = db.query(User).filter(User.Id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # 验证Redis中的token
    is_valid = await auth_service.validate_token(user_id, token)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token已失效或已被登出",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前超级用户"""
    if not current_user.Role == "超级管理员":
        raise AuthenticationError(message="权限不足")
    return current_user 