from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.department import department as crud_department
from app.schemas.department import DepartmentTree, Department
from app.core.logger import get_logger
from app.exceptions.base import ValidationError

logger = get_logger("department.service")

class DepartmentService:
    async def get_department_tree(self, db: Session) -> List[DepartmentTree]:
        """获取部门树结构"""
        return await crud_department.get_tree(db)

    async def create_department(
        self, 
        db: Session, 
        *, 
        name: str, 
        parent_id: Optional[str] = None
    ) -> Department:
        """创建部门"""
        # 如果指定了父部门，检查父部门是否存在
        if parent_id:
            parent = await crud_department.get_by_id(db, parent_id)
            if not parent:
                raise ValidationError("父部门不存在")
        
        # 检查部门是否已存在
        existing_dept = await crud_department.get_by_name(db, name)
        if existing_dept:
            raise ValidationError("部门已存在")
        
        dept = await crud_department.create(db, name=name, parent_id=parent_id)
        return dept

    async def update_department_status(
        self, 
        db: Session, 
        *, 
        id: str, 
        status: str
    ) -> Department:
        """更新部门状态"""
        if status not in ["0", "1"]:
            raise ValidationError("状态值无效，只能是0或1")
        
        dept = await crud_department.update_status(db, id=id, status=status)
        return dept

    async def delete_department(self, db: Session, *, id: UUID) -> Department:
        """删除部门"""
        result = await crud_department.delete(db, id=id)
        return result

department_service = DepartmentService() 