from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.crud.role import get_role_crud
from app.schemas.role import Role, RoleCreate, RoleUpdate
from app.core.logger import get_logger
from app.exceptions.base import ValidationError, NotFoundError

logger = get_logger("role.service")

class RoleService:
    
    async def create_role(self, db: Session, role_in: RoleCreate) -> Role:
        """创建角色"""
        role_crud = get_role_crud(db)
        
        # 检查角色名称或代码是否已存在
        if await role_crud.check_role_exists(role_in.RoleName, role_in.RoleCode):
            raise ValidationError("角色名称或代码已存在")
        
        role = await role_crud.create(role_in)
        logger.info(f"创建角色成功: {role.RoleName}")
        return role

    async def get_roles(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        status_filter: Optional[str] = None
    ) -> List[Role]:
        """获取角色列表"""
        role_crud = get_role_crud(db)
        return await role_crud.get_multi(skip=skip, limit=limit, status=status_filter)

    async def get_role_by_id(self, db: Session, role_id: UUID) -> Role:
        """根据ID获取角色"""
        role_crud = get_role_crud(db)
        role = await role_crud.get_by_id(role_id)
        
        if not role:
            raise NotFoundError("角色不存在")
        
        return role

    async def get_role_by_name(self, db: Session, role_name: str) -> Optional[Role]:
        """根据角色名称获取角色"""
        role_crud = get_role_crud(db)
        return await role_crud.get_by_name(role_name)

    async def get_role_by_code(self, db: Session, role_code: str) -> Optional[Role]:
        """根据角色代码获取角色"""
        role_crud = get_role_crud(db)
        return await role_crud.get_by_code(role_code)

    async def update_role(self, db: Session, role_id: UUID, role_update: RoleUpdate) -> Role:
        """更新角色"""
        role_crud = get_role_crud(db)
        
        # 检查角色是否存在
        role = await role_crud.get_by_id(role_id)
        if not role:
            raise NotFoundError("角色不存在")
        
        # 检查角色名称或代码是否已被其他角色使用
        update_data = role_update.model_dump(exclude_unset=True)
        if "RoleName" in update_data or "RoleCode" in update_data:
            role_name = update_data.get("RoleName", role.RoleName)
            role_code = update_data.get("RoleCode", role.RoleCode)
            if await role_crud.check_role_exists(role_name, role_code, exclude_id=role_id):
                raise ValidationError("角色名称或代码已被其他角色使用")
        
        updated_role = await role_crud.update(role_id, role_update)
        logger.info(f"更新角色成功: {role_id}")
        return updated_role

    async def delete_role(self, db: Session, role_id: UUID) -> None:
        """删除角色"""
        role_crud = get_role_crud(db)
        
        # 检查角色是否存在
        role = await role_crud.get_by_id(role_id)
        if not role:
            raise NotFoundError("角色不存在")
        
        # TODO: 检查是否有用户使用此角色，如果有则不允许删除
        # 这里可以添加相关逻辑
        # from app.crud.user import user as crud_user
        # users_with_role = await crud_user.get_by_role_id(db, role_id)
        # if users_with_role:
        #     raise ValidationError("该角色下还有用户，无法删除")
        
        success = await role_crud.delete(role_id)
        if not success:
            raise NotFoundError("角色不存在")
        
        logger.info(f"删除角色成功: {role_id}")

    async def get_role_count(self, db: Session, status_filter: Optional[str] = None) -> int:
        """获取角色总数"""
        role_crud = get_role_crud(db)
        return await role_crud.count(status=status_filter)

    async def change_role_status(self, db: Session, role_id: UUID, status: str) -> Role:
        """更改角色状态"""
        if status not in ["0", "1"]:
            raise ValidationError("状态值无效，只能是0（禁用）或1（启用）")
        
        role_update = RoleUpdate(Status=status)
        return await self.update_role(db, role_id, role_update)

    async def get_default_role(self, db: Session) -> Optional[Role]:
        """获取默认角色"""
        role_crud = get_role_crud(db)
        # 假设默认角色的代码为 'user' 或者状态为某个特定值
        # 这里需要根据实际业务逻辑调整
        return await role_crud.get_by_code("user")

role_service = RoleService() 