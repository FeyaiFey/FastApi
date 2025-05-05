from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db_session, get_current_user
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

@router.post("/add", response_model=Department)
async def create_department(
    *,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    department_in: DepartmentCreate = Depends()
) -> Department:
    """
    创建部门
    """
    return await department_service.create_department(
        db, 
        name=department_in.name, 
        parent_id=department_in.parent_id
    )

@router.put("/{id}/status", response_model=Department)
async def update_department_status(
    *,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    status_in: DepartmentStatusUpdate = Depends()
) -> Department:
    """
    更新部门状态
    """
    return await department_service.update_department_status(
        db, 
        id=status_in.id, 
        status=status_in.status
    )

@router.delete("/delete/{id}", response_model=Department)
async def delete_department(
    *,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    id: UUID = Depends()
) -> Department:
    """
    删除部门
    """
    return await department_service.delete_department(db, id=id) 