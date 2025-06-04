from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.department import Department, DepartmentTree, DepartmentCreate, DepartmentStatusUpdate
from app.services.department import department_service
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger("department.api")

@router.get("/tree", response_model=List[DepartmentTree])
async def get_department_tree(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> List[DepartmentTree]:
    """
    获取部门树结构
    """
    return await department_service.get_department_tree(db)

@router.post("/", response_model=Department, status_code=status.HTTP_201_CREATED)
async def create_department(
    *,
    db: Session = Depends(get_db_session),
    department_in: DepartmentCreate,
    current_user: User = Depends(get_current_user)
) -> Department:
    """
    创建部门
    """
    return await department_service.create_department(
        db, 
        name=department_in.name, 
        parent_id=department_in.parent_id
    )

@router.patch("/{department_id}/status", response_model=Department)
async def update_department_status(
    department_id: UUID,
    status_update: str = Query(..., regex="^[01]$", description="状态：0-禁用，1-启用"),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Department:
    """
    更新部门状态
    """
    return await department_service.update_department_status(
        db, 
        id=str(department_id), 
        status=status_update
    )

@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    删除部门
    """
    await department_service.delete_department(db, id=department_id)
    return None 