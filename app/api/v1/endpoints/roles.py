from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db_session
from app.core.deps import get_current_user
from app.core.response import response_manager
from app.models.user import User
from app.services.role import role_service
from app.schemas.role import Role, RoleCreate, RoleUpdate
from app.schemas.role_menu import RouteItem
from app.schemas.response import SuccessResponse, PaginationResponse
from app.core.logger import get_logger

logger = get_logger("roles.api")
router = APIRouter()

@router.post("/", response_model=SuccessResponse[Role])
async def create_role(
    *,
    db: Session = Depends(get_db_session),
    role_in: RoleCreate,
    current_user: User = Depends(get_current_user)
):
    """
    创建角色
    """
    role = await role_service.create_role(db, role_in)
    return response_manager.created(data=role, message="角色创建成功")

@router.get("/", response_model=PaginationResponse[Role])
async def read_roles(
    db: Session = Depends(get_db_session),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    status: Optional[str] = Query(None, description="角色状态筛选"),
    current_user: User = Depends(get_current_user)
):
    """
    获取角色列表
    """
    roles = await role_service.get_roles(db, skip=skip, limit=limit, status_filter=status)
    
    # 获取总数
    total = await role_service.get_role_count(db, status_filter=status)
    
    # 计算页码
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return response_manager.paginated(
        items=roles,
        total=total,
        page=page,
        page_size=limit,
        message="角色列表查询成功"
    )

@router.get("/{role_id}", response_model=SuccessResponse[Role])
async def read_role(
    role_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    根据ID获取角色
    """
    role = await role_service.get_role_by_id(db, role_id)
    return response_manager.success(data=role, message="角色详情查询成功")

@router.get("/{role_id}/menus", response_model=SuccessResponse[List[RouteItem]])
async def get_role_menus(
    role_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    获取角色的菜单路由
    - 需要登录权限
    - 返回该角色可访问的所有菜单，构建成前端路由格式
    - 数据结构与前端路由配置完全一致
    """
    routes = await role_service.get_role_menus(db, role_id)
    logger.info(f"获取角色 {role_id} 的菜单路由")
    return response_manager.success(data=routes, message="角色菜单路由查询成功")

@router.put("/{role_id}", response_model=SuccessResponse[Role])
async def update_role(
    role_id: uuid.UUID,
    role_update: RoleUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    更新角色
    """
    role = await role_service.update_role(db, role_id, role_update)
    return response_manager.success(data=role, message="角色更新成功")

@router.delete("/{role_id}", response_model=SuccessResponse[None])
async def delete_role(
    role_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    删除角色
    """
    await role_service.delete_role(db, role_id)
    return response_manager.success(message="角色删除成功")

@router.put("/{role_id}/status", response_model=SuccessResponse[Role])
async def change_role_status(
    role_id: uuid.UUID,
    status: str = Query(..., regex="^[01]$", description="状态：0-禁用，1-启用"),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    更改角色状态
    """
    role = await role_service.change_role_status(db, role_id, status)
    status_text = "启用" if status == "1" else "禁用"
    return response_manager.success(data=role, message=f"角色状态已更新为{status_text}")

@router.get("/count/total", response_model=SuccessResponse[dict])
async def get_role_count(
    db: Session = Depends(get_db_session),
    status: Optional[str] = Query(None, description="角色状态筛选"),
    current_user: User = Depends(get_current_user)
):
    """
    获取角色总数
    """
    count = await role_service.get_role_count(db, status_filter=status)
    return response_manager.success(data={"total": count}, message="角色总数查询成功") 