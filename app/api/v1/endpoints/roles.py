from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db_session
from app.core.deps import get_current_user
from app.models.user import User
from app.services.role import role_service
from app.schemas.roleMenu import RouteItem
from app.schemas.response import ResponseModel, ResponseHandler
from app.core.exceptions import (
    CustomException
)
from app.core.logger import get_logger

logger = get_logger("roles.api")
router = APIRouter()

@router.get("/{role_id}/menus", response_model=ResponseModel[List[RouteItem]])
async def get_role_menus(
    role_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[List[RouteItem]]:
    """
    获取角色的菜单路由
    - 需要登录权限
    - 返回该角色可访问的所有菜单，构建成前端路由格式
    - 数据结构与前端路由配置完全一致
    """
    try:
        routes = await role_service.get_role_menus(db, role_id)
        logger.info(f"获取角色 {role_id} 的菜单路由")
        return ResponseHandler.success(data=routes, message="角色菜单路由查询成功")
    except CustomException as e:
        # 自定义异常会被全局异常处理器捕获并处理
        raise
    except Exception as e:
        logger.error(f"获取角色菜单路由失败: {str(e)}")
        raise CustomException(message="获取角色菜单路由失败")