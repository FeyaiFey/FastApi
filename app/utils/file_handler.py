import os
import uuid
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from typing import Optional

class FileHandler:
    @staticmethod
    async def save_avatar(file: UploadFile, user_id: int) -> str:
        """
        保存用户头像
        :param file: 上传的文件
        :param user_id: 用户ID
        :return: 文件相对路径
        """
        # 检查文件大小
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB
        while chunk := await file.read(chunk_size):
            file_size += len(chunk)
            if file_size > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件大小超过限制 ({settings.MAX_UPLOAD_SIZE/1024/1024}MB)"
                )
        await file.seek(0)

        # 检查文件类型
        if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="不支持的文件类型"
            )

        # 生成文件名
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{user_id}_{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(settings.AVATAR_DIR, filename)

        # 确保目录存在
        os.makedirs(settings.AVATAR_DIR, exist_ok=True)

        # 保存文件
        try:
            with open(file_path, "wb") as f:
                while chunk := await file.read(chunk_size):
                    f.write(chunk)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"文件保存失败: {str(e)}"
            )

        # 返回相对路径
        return f"/static/uploads/avatars/{filename}"