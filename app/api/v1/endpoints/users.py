from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Query, status
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db_session
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserInfo, User as UserSchema, UserCreate, UserUpdate, UserRegister
from app.services.user import user_service
from app.core.logger import get_logger
from app.exceptions.base import NotFoundError, ValidationError

router = APIRouter()
logger = get_logger(__name__)

@router.get("/", response_model=List[UserSchema])
async def get_users(
    db: Session = Depends(get_db_session),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    include_relations: bool = Query(True, description="是否包含关联信息（角色、部门）"),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户列表
    """
    return await user_service.get_users(
        db, 
        skip=skip, 
        limit=limit, 
        include_relations=include_relations
    )

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    include_relations: bool = Query(True, description="是否包含关联信息（角色、部门）"),
    current_user: User = Depends(get_current_user)
):
    """
    根据ID获取用户
    """
    user = await user_service.get_user(db, user_id, include_relations=include_relations)
    if not user:
        raise NotFoundError("用户不存在")
    return user

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: Session = Depends(get_db_session),
    user_in: UserCreate,
    current_user: User = Depends(get_current_user)
):
    """
    创建用户（管理员用）
    """
    return await user_service.create_user_admin(db, user_in)

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    更新用户信息
    """
    return await user_service.update_user(db, user_id, user_update)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    删除用户
    """
    await user_service.delete_user(db, user_id)
    return None

@router.patch("/{user_id}/status", response_model=UserSchema)
async def change_user_status(
    user_id: uuid.UUID,
    status: str = Query(..., regex="^[01]$", description="状态：0-禁用，1-启用"),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    更改用户状态
    """
    return await user_service.change_user_status(db, user_id, status)

@router.patch("/{user_id}/role", response_model=UserSchema)
async def change_user_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    更改用户角色
    """
    return await user_service.change_user_role(db, user_id, role_id)

@router.get("/email/{email}", response_model=UserSchema)
async def get_user_by_email(
    email: str,
    db: Session = Depends(get_db_session),
    include_relations: bool = Query(True, description="是否包含关联信息（角色、部门）"),
    current_user: User = Depends(get_current_user)
):
    """
    根据邮箱获取用户
    """
    user = await user_service.get_user_by_email(db, email, include_relations=include_relations)
    if not user:
        raise NotFoundError("用户不存在")
    return user

@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    上传用户头像
    - 验证文件类型和大小
    - 保存头像文件
    - 更新用户头像URL
    """
    return await user_service.update_avatar(db, current_user.Id, file)

@router.post("/{user_id}/avatar")
async def admin_upload_avatar(
    user_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    管理员为用户上传头像
    """
    return await user_service.update_avatar(db, user_id, file)