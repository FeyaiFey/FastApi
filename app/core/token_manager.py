from typing import Optional
from app.core.redis import redis_client
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

class TokenManager:
    def __init__(self):
        self.redis = redis_client
        self.token_prefix = "user_token:"
        self.token_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 转换为秒

    def _get_token_key(self, user_id: str) -> str:
        """获取Redis中的token键"""
        return f"{self.token_prefix}{user_id}"

    async def store_token(self, user_id: str, token: str) -> None:
        """
        存储用户token
        :param user_id: 用户ID
        :param token: JWT token
        """
        try:
            key = self._get_token_key(user_id)
            await self.redis.set(
                key,
                token,
                ex=self.token_expire
            )
            logger.info(f"用户 {user_id} 的token已存储")
        except Exception as e:
            logger.error(f"存储token失败: {str(e)}")
            raise

    async def get_token(self, user_id: str) -> Optional[str]:
        """
        获取用户token
        :param user_id: 用户ID
        :return: token字符串或None
        """
        try:
            key = self._get_token_key(user_id)
            token = await self.redis.get(key)
            return token
        except Exception as e:
            logger.error(f"获取token失败: {str(e)}")
            return None

    async def validate_token(self, user_id: str, token: str) -> bool:
        """
        验证token是否有效
        :param user_id: 用户ID
        :param token: 待验证的token
        :return: 是否有效
        """
        try:
            stored_token = await self.get_token(user_id)
            if not stored_token:
                logger.warning(f"用户 {user_id} 的token不存在")
                return False
            
            is_valid = stored_token == token
            if not is_valid:
                logger.warning(f"用户 {user_id} 的token不匹配")
            
            return is_valid
        except Exception as e:
            logger.error(f"验证token失败: {str(e)}")
            return False

    async def revoke_token(self, user_id: str) -> None:
        """
        撤销用户token
        :param user_id: 用户ID
        """
        try:
            key = self._get_token_key(user_id)
            await self.redis.delete(key)
            logger.info(f"用户 {user_id} 的token已撤销")
        except Exception as e:
            logger.error(f"撤销token失败: {str(e)}")
            raise

    async def refresh_token(self, user_id: str, token: str) -> None:
        """
        刷新token过期时间
        :param user_id: 用户ID
        :param token: 当前token
        """
        try:
            key = self._get_token_key(user_id)
            await self.redis.set(
                key,
                token,
                ex=self.token_expire
            )
            logger.info(f"用户 {user_id} 的token已刷新")
        except Exception as e:
            logger.error(f"刷新token失败: {str(e)}")
            raise

token_manager = TokenManager() 