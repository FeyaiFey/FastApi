from typing import Dict, Set
from fastapi import WebSocket
from app.core.redis import redis_client
import json

class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # 存储所有活动的 WebSocket 连接
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """建立新的 WebSocket 连接"""
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
        
    def disconnect(self, websocket: WebSocket, client_id: str):
        """断开 WebSocket 连接"""
        if client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
                
    async def send_personal_message(self, message: str, client_id: str):
        """发送个人消息"""
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                await connection.send_text(message)
                
    async def broadcast(self, message: str):
        """广播消息给所有连接的客户端"""
        for connections in self.active_connections.values():
            for connection in connections:
                await connection.send_text(message)
                
    async def publish_message(self, channel: str, message: dict):
        """发布消息到 Redis 频道"""
        await redis_client.publish(channel, json.dumps(message))
        
    async def subscribe_to_channel(self, channel: str, websocket: WebSocket):
        """订阅 Redis 频道"""
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel)
        
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                await websocket.send_text(message["data"])

# 创建全局连接管理器实例
manager = ConnectionManager() 