import base64
import os
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.user import User
from app.schemas.user import UserInfo
from app.crud.user import user as crud_user
from app.crud.role import role as crud_role
from app.crud.department import department as crud_department
from app.core.logger import get_logger
from app.core.exceptions import (
    ValidationException,
    BusinessException
)

logger = get_logger(__name__)

class UserService:
    async def get_current_user_info(self, db: Session, user_id: UUID) -> UserInfo:
        """获取当前用户信息"""
        try:
            user = await crud_user.get_by_id(db, user_id)
            department = await crud_department.get_by_id(db, user.DepartmentId)
            role = await crud_role.get_by_id(db, user.RoleId)

            if not department or not role:
                raise BusinessException("获取用户关联信息失败")

            return UserInfo(
                Id=user.Id,
                UserName=user.UserName,
                Email=user.Email,
                DepartmentId=user.DepartmentId,
                RoleId=user.RoleId,
                DepartmentName=department.DepartmentName,
                RoleName=role.RoleName,
                AvatarUrl=user.AvatarUrl
            )
        except Exception as e:
            logger.error(f"获取用户信息失败: {str(e)}")
            raise BusinessException("获取用户信息失败")
    
    async def update_user_avatar(self, db: Session, user_id: int, avatar_data: str) -> None:
        """更新用户头像
        
        Args:
            user_id: 用户ID
            avatar_data: base64编码的图片数据，格式为 "data:image/xxx;base64,xxxxx"
        """
        try:
            # 验证用户是否存在
            user = db.query(User).filter(User.Id == user_id).first()
            if not user:
                raise ValidationException("用户不存在")
                
            # 解析base64数据
            try:
                # 移除 data:image/xxx;base64, 前缀
                if "," in avatar_data:
                    avatar_data = avatar_data.split(",", 1)[1]
                    
                # 解码base64数据
                image_data = base64.b64decode(avatar_data)
                
                # 生成文件名
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"avatar_{user_id}_{timestamp}.png"
                
                # 确保上传目录存在
                upload_dir = os.path.join("static", "avatars")
                os.makedirs(upload_dir, exist_ok=True)
                
                # 保存图片文件
                file_path = os.path.join(upload_dir, filename)
                with open(file_path, "wb") as f:
                    f.write(image_data)
                    
                # 更新用户头像URL
                avatar_url = 'http://127.0.0.1:8000/static/avatars/' + filename
                
                # 更新用户头像URL
                user.AvatarUrl = avatar_url
                db.commit()
                db.refresh(user)
                
                logger.info(f"用户 {user_id} 头像更新成功")
                
            except Exception as e:
                logger.error(f"处理头像数据失败: {str(e)}")
                raise ValidationException("处理头像数据失败")
                
        except ValidationException as e:
            raise e
        except Exception as e:
            logger.error(f"更新用户头像失败: {str(e)}")
            raise ValidationException("更新用户头像失败")


user_service = UserService() 