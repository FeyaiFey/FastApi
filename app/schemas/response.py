from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel
from fastapi import status



T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = status.HTTP_200_OK
    message: str = "Success"
    data: Optional[T] = None

    class Config:
        arbitrary_types_allowed = True

class ResponseHandler:
    """
    统一响应处理器
    """
    @staticmethod
    def success(*, data: Any = None, message: str = "Success") -> ResponseModel:
        return ResponseModel(
            code=status.HTTP_200_OK,
            message=message,
            data=data
        )

    @staticmethod
    def error(*, code: int = status.HTTP_400_BAD_REQUEST, message: str = "Error", data: Any = None) -> ResponseModel:
        return ResponseModel(
            code=code,
            message=message,
            data=data
        )

