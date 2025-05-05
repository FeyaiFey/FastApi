from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.crud.department import department as crud_department
from app.schemas.department import DepartmentTree, Department
from app.core.logger import get_logger


logger = get_logger("department.service")

class DepartmentService:
    async def get_department_tree(self, db: Session) -> List[DepartmentTree]:
        """获取部门树结构"""
        try:
            return await crud_department.get_tree(db)
        except Exception as e:
            logger.error(f"获取部门树失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="获取部门树失败"
            )

    async def create_department(
        self, 
        db: Session, 
        *, 
        name: str, 
        parent_id: Optional[str] = None
    ) -> Department:
        """创建部门"""
        try:
            # 如果指定了父部门，检查父部门是否存在
            if parent_id:
                parent = await crud_department.get_by_id(db, parent_id)
                if not parent:
                    raise HTTPException(
                        status_code=400,
                        detail="父部门不存在"
                    )
            # 检查部门是否已存在
            existing_dept = await crud_department.get_by_name(db, name)
            if existing_dept:
                raise HTTPException(
                    status_code=400,
                    detail="部门已存在"
                )
            
            dept = await crud_department.create(db, name=name, parent_id=parent_id)
            return dept
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"创建部门失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="创建部门失败"
            )

    async def update_department_status(
        self, 
        db: Session, 
        *, 
        id: str, 
        status: str
    ) -> Department:
        """更新部门状态"""
        try:
            if status not in ["0", "1"]:
                raise HTTPException(
                    status_code=400,
                    detail="状态值无效，只能是0或1"
                )
            
            dept = await crud_department.update_status(db, id=id, status=status)
            return dept
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"更新部门状态失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="更新部门状态失败"
            )

    async def delete_department(self, db: Session, *, id: UUID) -> Department:
        """删除部门"""
        try:
            result = await crud_department.delete(db, id=id)
            return result
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"删除部门失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="删除部门失败"
            )

department_service = DepartmentService() 