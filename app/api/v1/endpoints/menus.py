from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db_session
from app.core.deps import get_current_user
from app.models.user import User
from app.services.menu import menu_service
from app.schemas.menu import Menu, MenuCreate, MenuUpdate, MenuTree
from app.core.logger import get_logger
from app.exceptions.base import NotFoundError

logger = get_logger("menus.api")
router = APIRouter()

@router.post("/", response_model=Menu, status_code=status.HTTP_201_CREATED)
async def create_menu(
    *,
    db: Session = Depends(get_db_session),
    menu_in: MenuCreate,
    current_user: User = Depends(get_current_user)
):
    """
    创建菜单
    """
    return await menu_service.create_menu(db, menu_in)

@router.get("/", response_model=List[Menu])
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
    return await menu_service.get_menus(db, skip=skip, limit=limit, hidden=hidden, parent_id=parent_id)

@router.get("/tree", response_model=List[MenuTree])
async def read_menu_tree(
    db: Session = Depends(get_db_session),
    show_hidden: bool = Query(False, description="是否显示隐藏菜单"),
    current_user: User = Depends(get_current_user)
):
    """
    获取菜单树结构
    """
    return await menu_service.get_menu_tree(db, show_hidden=show_hidden)

@router.get("/next-id")
async def get_next_menu_id(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    获取下一个可用的MenuId
    """
    next_id = await menu_service.get_next_menu_id(db)
    return {"next_menu_id": next_id}

@router.get("/{menu_id}", response_model=Menu)
async def read_menu(
    menu_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    根据ID获取菜单
    """
    return await menu_service.get_menu_by_id(db, menu_id)

@router.put("/{menu_id}", response_model=Menu)
async def update_menu(
    menu_id: uuid.UUID,
    menu_update: MenuUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    更新菜单
    """
    return await menu_service.update_menu(db, menu_id, menu_update)

@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu(
    menu_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    删除菜单
    """
    await menu_service.delete_menu(db, menu_id)
    return None

@router.patch("/{menu_id}/toggle-visibility", response_model=Menu)
async def toggle_menu_visibility(
    menu_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    切换菜单显示/隐藏状态
    """
    return await menu_service.toggle_menu_visibility(db, menu_id)

@router.get("/count/total")
async def get_menu_count(
    db: Session = Depends(get_db_session),
    hidden: Optional[bool] = Query(None, description="菜单显示状态筛选"),
    current_user: User = Depends(get_current_user)
):
    """
    获取菜单总数
    """
    count = await menu_service.get_menu_count(db, hidden=hidden)
    return {"total": count} 