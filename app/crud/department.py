from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
import uuid
from datetime import datetime

from app.models.department import Department
from app.schemas.department import DepartmentTree
from app.core.logger import get_logger
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    CustomException
)

logger = get_logger("department.crud")

class CRUDDepartment:
    async def get_by_id(self, db: Session, id: str) -> Optional[Department]:
        """根据ID获取部门"""
        try:
            department = db.query(Department).get(id)
            if not department:
                raise NotFoundException(f"部门不存在: {id}")
            return department
        except CustomException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"查询部门失败: {str(e)}")
            raise BadRequestException("查询部门失败，请稍后重试")
    
    async def get_by_name(self, db: Session, name: str) -> Optional[Department]:
        """根据名称获取部门"""
        try:
            department = db.query(Department).filter(Department.DepartmentName == name).first()
            if not department:
                raise NotFoundException(f"未找到名称为 {name} 的部门")
            return department
        except CustomException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"查询部门失败: {str(e)}")
            raise BadRequestException("查询部门失败，请稍后重试")

    async def get_tree(self, db: Session) -> List[DepartmentTree]:
        """获取部门树结构"""
        try:
            # 获取所有部门
            departments = db.query(Department).all()
            
            if not departments:
                # 没有部门数据时返回空列表，不抛出异常
                return []
            
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
                        # 父部门不存在时，作为根部门
                        logger.warning(f"部门 {dept.DepartmentName} 的父部门 {dept.ParentId} 不存在")
                        root_depts.append(dept_item)
                else:
                    # 如果没有父部门，作为根部门
                    root_depts.append(dept_item)
            
            return root_depts
        except CustomException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"获取部门树失败: {str(e)}")
            raise BadRequestException("获取部门树失败，请稍后重试")

department = CRUDDepartment() 