import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import get_logger

logger = get_logger(name="api")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 开始时间
        start_time = time.time()
        
        # 请求信息
        request_id = request.headers.get("X-Request-ID", "")
        client_host = request.client.host if request.client else "unknown"
        
        # 获取请求体
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
            except:
                body = await request.body()
        
        # 记录请求信息
        logger.info(
            f"开始处理请求: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "client_host": client_host,
                "headers": dict(request.headers),
                "process_time_ms": 0,
                "status_code": 0
            }
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            process_time_ms = round(process_time * 1000, 2)  # 转换为毫秒并保留2位小数
            
            # 获取响应体
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # 重新构建响应
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            # 记录响应信息
            logger.info(
                f"请求处理完成: {request.method} {request.url.path} - 耗时: {process_time_ms}ms - 状态码: {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "path": request.url.path,
                    "client_host": client_host,
                    "status_code": response.status_code,
                    "process_time_ms": process_time_ms,
                }
            )
            
            return response
            
        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time
            process_time_ms = round(process_time * 1000, 2)
            
            # 记录异常信息
            logger.exception(
                f"请求处理失败: {request.method} {request.url.path} - 耗时: {process_time_ms}ms - 错误: {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "path": request.url.path,
                    "client_host": client_host,
                    "error": str(e),
                    "process_time_ms": process_time_ms,
                    "status_code": 500
                }
            )
            raise