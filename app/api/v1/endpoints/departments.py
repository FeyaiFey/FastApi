from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.deps import get_current_user
from app.core.response import response_manager
from app.models.user import User
from app.schemas.department import Department, DepartmentTree, DepartmentCreate, DepartmentStatusUpdate
from app.schemas.response import SuccessResponse
from app.services.department import department_service
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger("department.api")

@router.get("/tree", response_model=SuccessResponse[List[DepartmentTree]])
async def get_department_tree(
    db: Session = Depends(get_db_session),
    # current_user: User = Depends(get_current_user)
) -> SuccessResponse[List[DepartmentTree]]:
    """
    获取部门树结构
    - 需要登录权限
    - 返回完整的部门层级结构
    """
    tree = await department_service.get_department_tree(db)
    return response_manager.success(data=tree, message="部门树查询成功")

@router.post("/", response_model=SuccessResponse[Department])
async def create_department(
    *,
    db: Session = Depends(get_db_session),
    department_in: DepartmentCreate,
    current_user: User = Depends(get_current_user)
) -> SuccessResponse[Department]:
    """
    创建部门
    """
    department = await department_service.create_department(
        db, 
        name=department_in.name, 
        parent_id=department_in.parent_id
    )
    return response_manager.created(data=department, message="部门创建成功")

@router.put("/{department_id}/status", response_model=SuccessResponse[Department])
async def update_department_status(
    department_id: UUID,
    status_update: str = Query(..., regex="^[01]$", description="状态：0-禁用，1-启用"),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> SuccessResponse[Department]:
    """
    更新部门状态
    """
    department = await department_service.update_department_status(
        db, 
        id=str(department_id), 
        status=status_update
    )
    status_text = "启用" if status_update == "1" else "禁用"
    return response_manager.success(data=department, message=f"部门状态已更新为{status_text}")

@router.delete("/{department_id}", response_model=SuccessResponse[None])
async def delete_department(
    department_id: UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> SuccessResponse[None]:
    """
    删除部门
    """
    await department_service.delete_department(db, id=department_id)
    return response_manager.success(message="部门删除成功") 