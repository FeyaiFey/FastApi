from typing import List
from sqlalchemy.orm import Session
from app.crud.department import department_crud
from app.schemas.department import DepartmentTree
from app.core.logger import get_logger
from app.core.exceptions import (
    BusinessException
)

logger = get_logger("department.service")

class DepartmentService:
    async def get_department_tree(self, db: Session) -> List[DepartmentTree]:
        """获取部门树结构"""
        try:
            return await department_crud.get_tree(db)
        except Exception as e:
            logger.error(f"获取部门树失败: {str(e)}")
            raise BusinessException("获取部门树失败")


department_service = DepartmentService() 