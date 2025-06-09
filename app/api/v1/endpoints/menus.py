from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db_session
from app.core.deps import get_current_user
from app.core.response import response_manager
from app.models.user import User
from app.services.menu import menu_service
from app.schemas.menu import Menu, MenuCreate, MenuUpdate, MenuTree
from app.schemas.response import SuccessResponse, PaginationResponse
from app.core.logger import get_logger
from app.exceptions.base import NotFoundError

logger = get_logger("menus.api")
router = APIRouter()

@router.post("/", response_model=SuccessResponse[Menu])
async def create_menu(
    *,
    db: Session = Depends(get_db_session),
    menu_in: MenuCreate,
    current_user: User = Depends(get_current_user)
):
    """
    创建菜单
    """
    menu = await menu_service.create_menu(db, menu_in)
    return response_manager.created(data=menu, message="菜单创建成功")

@router.get("/", response_model=PaginationResponse[Menu])
async def read_menus(
    db: Session = Depends(get_db_session),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    hidden: Optional[bool] = Query(None, description="菜单显示状态筛选"),
    parent_id: Optional[int] = Query(None, description="父菜单ID筛选"),
    current_user: User = Depends(get_current_user)
):
    """
    获取菜单列表
    """
    # 获取菜单列表
    menus = await menu_service.get_menus(db, skip=skip, limit=limit, hidden=hidden, parent_id=parent_id)
    
    # 获取总数
    total = await menu_service.get_menu_count(db, hidden=hidden)
    
    # 计算页码
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return response_manager.paginated(
        items=menus,
        total=total,
        page=page,
        page_size=limit,
        message="菜单列表查询成功"
    )

@router.get("/tree", response_model=SuccessResponse[List[MenuTree]])
async def read_menu_tree(
    db: Session = Depends(get_db_session),
    show_hidden: bool = Query(False, description="是否显示隐藏菜单"),
    current_user: User = Depends(get_current_user)
):
    """
    获取菜单树结构
    """
    menu_tree = await menu_service.get_menu_tree(db, show_hidden=show_hidden)
    return response_manager.success(data=menu_tree, message="菜单树查询成功")

@router.get("/next-id", response_model=SuccessResponse[dict])
async def get_next_menu_id(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    获取下一个可用的MenuId
    """
    next_id = await menu_service.get_next_menu_id(db)
    return response_manager.success(
        data={"next_menu_id": next_id}, 
        message="下一个菜单ID获取成功"
    )

@router.get("/{menu_id}", response_model=SuccessResponse[Menu])
async def read_menu(
    menu_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    根据ID获取菜单
    """
    menu = await menu_service.get_menu_by_id(db, menu_id)
    return response_manager.success(data=menu, message="菜单详情查询成功")

@router.put("/{menu_id}", response_model=SuccessResponse[Menu])
async def update_menu(
    menu_id: uuid.UUID,
    menu_update: MenuUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    更新菜单
    """
    menu = await menu_service.update_menu(db, menu_id, menu_update)
    return response_manager.success(data=menu, message="菜单更新成功")

@router.delete("/{menu_id}", response_model=SuccessResponse[None])
async def delete_menu(
    menu_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    删除菜单
    """
    await menu_service.delete_menu(db, menu_id)
    return response_manager.success(message="菜单删除成功")

@router.put("/{menu_id}/toggle-visibility", response_model=SuccessResponse[Menu])
async def toggle_menu_visibility(
    menu_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    切换菜单显示/隐藏状态
    """
    menu = await menu_service.toggle_menu_visibility(db, menu_id)
    visibility_status = "隐藏" if menu.Hidden else "显示"
    return response_manager.success(
        data=menu, 
        message=f"菜单已切换为{visibility_status}状态"
    )

@router.get("/count/total", response_model=SuccessResponse[dict])
async def get_menu_count(
    db: Session = Depends(get_db_session),
    hidden: Optional[bool] = Query(None, description="菜单显示状态筛选"),
    current_user: User = Depends(get_current_user)
):
    """
    获取菜单总数
    """
    count = await menu_service.get_menu_count(db, hidden=hidden)
    return response_manager.success(
        data={"total": count}, 
        message="菜单总数查询成功"
    ) 