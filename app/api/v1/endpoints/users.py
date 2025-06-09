from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Query, status, Body
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db_session
from app.core.deps import get_current_user
from app.core.response import response_manager
from app.models.user import User
from app.schemas.user import UserInfo, User as UserSchema, UserCreate, UserUpdate, UserRegister, AvatarUpload
from app.schemas.response import SuccessResponse, PaginationResponse
from app.services.user import user_service
from app.core.logger import get_logger
from app.exceptions.base import NotFoundError, ValidationError

router = APIRouter()
logger = get_logger(__name__)

@router.get("/current", response_model=SuccessResponse[UserInfo])
async def get_current_user(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息
    """
    logger.info(f"获取当前用户信息: {current_user}")
    user_info = await user_service.get_current_user_info(db, current_user.Id)
    return response_manager.success(data=user_info, message="获取当前用户信息成功")

@router.post("/avatar", response_model=SuccessResponse[dict])
async def upload_avatar(
    data: dict,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """更新用户头像"""
    try:
        # 验证数据格式
        if not data or "avatar" not in data:
            raise ValidationError("缺少头像数据")
            
        avatar_data = data["avatar"]
        if not isinstance(avatar_data, str) or not avatar_data.startswith("data:image/"):
            raise ValidationError("无效的头像数据格式")
        
        # 更新用户头像
        await user_service.update_user_avatar(db, current_user.Id, avatar_data)

        return response_manager.success(message="头像更新成功")
    except Exception as e:
        logger.error(f"头像更新失败: {str(e)}")
        raise ValidationError("头像更新失败")


@router.get("/", response_model=PaginationResponse[UserSchema])
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
    users = await user_service.get_users(
        db, 
        skip=skip, 
        limit=limit, 
        include_relations=include_relations
    )
    
    # 获取总数
    total = await user_service.get_user_count(db)
    
    # 计算页码
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return response_manager.paginated(
        items=users,
        total=total,
        page=page,
        page_size=limit,
        message="用户列表查询成功"
    )

@router.get("/{user_id}", response_model=SuccessResponse[UserSchema])
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
    return response_manager.success(data=user, message="用户详情查询成功")

@router.post("/", response_model=SuccessResponse[UserSchema])
async def create_user(
    *,
    db: Session = Depends(get_db_session),
    user_in: UserCreate,
    current_user: User = Depends(get_current_user)
):
    """
    创建用户（管理员用）
    """
    user = await user_service.create_user_admin(db, user_in)
    return response_manager.created(data=user, message="用户创建成功")

@router.put("/{user_id}", response_model=SuccessResponse[UserSchema])
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    更新用户信息
    """
    user = await user_service.update_user(db, user_id, user_update)
    return response_manager.success(data=user, message="用户更新成功")

@router.delete("/{user_id}", response_model=SuccessResponse[None])
async def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    删除用户
    """
    await user_service.delete_user(db, user_id)
    return response_manager.success(message="用户删除成功")

@router.put("/{user_id}/status", response_model=SuccessResponse[UserSchema])
async def change_user_status(
    user_id: uuid.UUID,
    status: str = Query(..., regex="^[01]$", description="状态：0-禁用，1-启用"),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    更改用户状态
    """
    user = await user_service.change_user_status(db, user_id, status)
    status_text = "启用" if status == "1" else "禁用"
    return response_manager.success(data=user, message=f"用户状态已更新为{status_text}")

@router.put("/{user_id}/role", response_model=SuccessResponse[UserSchema])
async def change_user_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    更改用户角色
    """
    user = await user_service.change_user_role(db, user_id, role_id)
    return response_manager.success(data=user, message="用户角色更新成功")

@router.get("/email/{email}", response_model=SuccessResponse[UserSchema])
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
    return response_manager.success(data=user, message="用户详情查询成功")

@router.post("/avatar", response_model=SuccessResponse[dict])
async def upload_avatar(
    avatar_data: AvatarUpload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    上传用户头像
    - 接收Base64格式的图片数据
    - 验证并保存图片
    - 更新用户头像URL
    """
    result = await user_service.update_avatar_base64(db, current_user.Id, avatar_data.avatar)
    return response_manager.success(data=result, message="头像上传成功")

@router.post("/{user_id}/avatar", response_model=SuccessResponse[dict])
async def admin_upload_avatar(
    user_id: uuid.UUID,
    avatar_data: AvatarUpload,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    管理员为用户上传头像
    - 接收Base64格式的图片数据
    """
    result = await user_service.update_avatar_base64(db, user_id, avatar_data.avatar)
    return response_manager.success(data=result, message="头像上传成功")