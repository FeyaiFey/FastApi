from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db_session, get_current_user
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserLoginResponse, UserBase
from app.services.auth import auth_service
from app.crud.user import user as crud_user
from app.core.security import revoke_all_tokens
from app.core.logger import get_logger

router = APIRouter() 
logger = get_logger(__name__)

@router.post("/register", response_model=UserBase)
async def register(*,db: Session = Depends(get_db_session),user_in: UserRegister = Depends()) -> UserBase:
    """
    用户注册
    """
    try:
        # 检查邮箱是否已存在
        user = await crud_user.get_by_email(db, email=user_in.Email)
        if user:
            logger.warning(f"注册失败: 邮箱已存在 - {user_in.Email}")
            raise HTTPException(
                status_code=400,
                detail="该邮箱已被注册"
            )
        
        # 创建用户
        user = await crud_user.create(db, obj_in=user_in)
        logger.info(f"用户注册成功: {user.UserName}")
        return user
    except Exception as e:
        logger.error(f"用户注册失败: {str(e)}")
        raise

@router.post("/login", response_model=UserLoginResponse)
async def login(
    db: Session = Depends(get_db_session),
    login_data: UserLogin = Depends()
) -> UserLoginResponse:
    """
    用户登录
    - 验证用户凭据
    - 生成访问令牌
    - 撤销之前的令牌
    """
    try:
        # 使用auth_service处理登录逻辑
        login_response = await auth_service.login(db, login_data)
        
        # 撤销之前的令牌
        user = await auth_service.authenticate(db, login_data)
        await revoke_all_tokens(user.Id)
        
        return login_response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"登录过程发生错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="登录失败，请稍后重试"
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    用户登出
    - 撤销当前用户的所有令牌
    """
    try:
        revoke_all_tokens(current_user.Id)
        logger.info(f"用户 {current_user.Email} 登出成功")
        return {"message": "登出成功"}
    except Exception as e:
        logger.error(f"登出过程发生错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="登出失败，请稍后重试"
        ) 