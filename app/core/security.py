import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.redis import redis_client
import uuid
from app.core.logger import get_logger

logger = get_logger(__name__)

# 配置密码哈希上下文
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

async def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

async def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建访问令牌"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
        )
    
    # 生成唯一的会话ID
    session_id = str(uuid.uuid4())
    
    # 创建令牌数据
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "session_id": session_id
    }
    
    # 生成JWT令牌
    encoded_jwt = jwt.encode(
        to_encode,
        os.getenv("SECRET_KEY"),
        algorithm=os.getenv("ALGORITHM")
    )
    
    # 将令牌信息存储到Redis
    redis_key = f"token:{session_id}"
    await redis_client.setex(
        redis_key,
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") * 60,  # 转换为秒
        encoded_jwt
    )
    
    return encoded_jwt

async def verify_token(token: str) -> Optional[dict]:
    """验证令牌"""
    try:
        # 解码JWT令牌
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithm=os.getenv("ALGORITHM")
        )
        
        # 获取会话ID
        session_id = payload.get("session_id")
        if not session_id:
            return None
        
        # 检查Redis中是否存在该令牌
        redis_key = f"token:{session_id}"
        stored_token = await redis_client.get(redis_key)
        
        if not stored_token or stored_token != token:
            return None
        
        return payload
        
    except JWTError:
        return None

async def revoke_token(token: str) -> bool:
    """撤销令牌"""
    try:
        # 解码令牌获取会话ID
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithm=os.getenv("ALGORITHM")
        )
        session_id = payload.get("session_id")
        
        if session_id:
            # 从Redis中删除令牌
            redis_key = f"token:{session_id}"
            await redis_client.delete(redis_key)
            return True
    except JWTError:
        pass
    return False

async def revoke_all_tokens(user_id: Union[str, int]) -> None:
    """
    撤销用户的所有令牌
    - 获取用户的所有令牌
    - 从Redis中删除这些令牌
    - 处理Redis连接错误
    """
    try:
        # 获取用户的所有令牌键
        pattern = f"token:*"
        async for key in redis_client.scan_iter(pattern):
            try:
                token = await redis_client.get(key)
                if token:
                    payload = jwt.decode(
                        token,
                        os.getenv("SECRET_KEY"),
                        algorithm=os.getenv("ALGORITHM")
                    )
                    if str(payload.get("sub")) == str(user_id):
                        await redis_client.delete(key)
            except (JWTError, Exception) as e:
                continue
    except Exception as e:
        logger.error(f"撤销令牌失败: {str(e)}")
        raise ConnectionError("令牌服务暂时不可用") from e 