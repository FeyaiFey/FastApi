from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
import uuid
from datetime import datetime

from app.models.department import Department
from app.schemas.department import DepartmentTree
from app.core.logger import get_logger
from app.exceptions.base import DatabaseError, NotFoundError, ValidationError

logger = get_logger("department.crud")

class CRUDDepartment:
    async def get_by_id(self, db: Session, id: str) -> Optional[Department]:
        """根据ID获取部门"""
        try:
            return db.query(Department).get(id)
        except SQLAlchemyError as e:
            logger.error(f"查询部门失败: {str(e)}")
            raise DatabaseError("查询部门失败")
    
    async def get_by_name(self, db: Session, name: str) -> Optional[Department]:
        """根据名称获取部门"""
        try:
            return db.query(Department).filter(Department.DepartmentName == name).first()
        except SQLAlchemyError as e:
            logger.error(f"查询部门失败: {str(e)}")
            raise DatabaseError("查询部门失败")

    async def get_tree(self, db: Session) -> List[DepartmentTree]:
        """获取部门树结构"""
        try:
            # 获取所有部门
            departments = db.query(Department).all()
            
            # 构建部门字典
            dept_dict = {
                str(dept.Id): DepartmentTree(
                    Id=str(dept.Id),
                    DepartmentName=dept.DepartmentName,
                    Children=[]
                )
                for dept in departments
            }
            
            # 构建树结构
            root_depts = []
            for dept in departments:
                dept_item = dept_dict[str(dept.Id)]
                if dept.ParentId:
                    # 如果有父部门，添加到父部门的子部门列表
                    parent = dept_dict.get(str(dept.ParentId))
                    if parent:
                        parent.Children.append(dept_item)
                else:
                    # 如果没有父部门，作为根部门
                    root_depts.append(dept_item)
            
            return root_depts
        except SQLAlchemyError as e:
            logger.error(f"获取部门树失败: {str(e)}")
            raise DatabaseError("获取部门树失败")

    async def create(self, db: Session, name: str, parent_id: Optional[UUID] = None) -> Department:
        """创建部门"""
        try:
            db_obj = Department(
                Id=str(uuid.uuid1()),
                DepartmentName=name,
                ParentId=parent_id,
                Status="1",  # 默认启用
                CreatedAt=datetime.now(),
                UpdatedAt=datetime.now()
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"部门创建成功: {name}")
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"创建部门失败: {str(e)}")
            db.rollback()
            raise DatabaseError("创建部门失败")

    async def update_status(self, db: Session, id: UUID, status: str) -> Department:
        """更新部门状态"""
        try:
            dept = db.query(Department).get(id)
            if not dept:
                raise NotFoundError(f"部门不存在: {id}")
            
            dept.Status = status
            dept.UpdatedAt = datetime.now()
            db.commit()
            db.refresh(dept)
            logger.info(f"部门状态更新成功: {id} -> {status}")
            return dept
        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"更新部门状态失败: {str(e)}")
            db.rollback()
            raise DatabaseError("更新部门状态失败")

    async def delete(self, db: Session, *, id: UUID) -> Department:
        """删除部门"""
        try:
            dept = db.query(Department).get(id)
            if not dept:
                raise NotFoundError(f"部门不存在: {id}")
            
            # 检查是否有子部门
            children = db.query(Department).filter(Department.ParentId == id).count()
            if children > 0:
                raise ValidationError("部门存在子部门，无法删除")
            
            # 检查是否有用户
            if hasattr(dept, 'users') and dept.users:
                raise ValidationError("部门存在用户，无法删除")
            
            db.delete(dept)
            db.commit()
            logger.info(f"部门删除成功: {id}")
            return dept
        except (NotFoundError, ValidationError):
            raise
        except SQLAlchemyError as e:
            logger.error(f"删除部门失败: {str(e)}")
            db.rollback()
            raise DatabaseError("删除部门失败")

department = CRUDDepartment() 