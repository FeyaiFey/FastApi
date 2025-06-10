from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.schemas.department import DepartmentTree
from app.services.department import department_service
from app.core.logger import get_logger
from app.core.exceptions import (
    CustomException
)
from app.schemas.response import ResponseModel, ResponseHandler

router = APIRouter()
logger = get_logger("department.api")

@router.get("/tree", response_model=ResponseModel[List[DepartmentTree]])
async def get_department_tree(
    db: Session = Depends(get_db_session)
) -> ResponseModel[List[DepartmentTree]]:
    """
    获取部门树结构
    - 需要登录权限
    - 返回完整的部门层级结构
    """
    try:
        tree = await department_service.get_department_tree(db)
        return ResponseHandler.success(data=tree, message="部门树查询成功")
    except CustomException as e:
        # 自定义异常会被全局异常处理器捕获并处理
        raise
    except Exception as e:
        logger.error(f"获取部门树失败: {str(e)}")
        raise CustomException(message="获取部门树失败")