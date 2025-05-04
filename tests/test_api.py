import pytest
import requests
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class TestAPI:
    """API测试类"""
    
    def _send_request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """
        发送请求并返回响应信息
        
        Args:
            method: 请求方法
            path: 请求路径
            **kwargs: 请求参数
            
        Returns:
            包含响应信息的字典
        """
        start_time = time.time()
        url = f"{BASE_URL}{path}"
        response = requests.request(method, url, **kwargs)
        end_time = time.time()
        
        return {
            "status_code": response.status_code,
            "response_time": round((end_time - start_time) * 1000, 2),  # 转换为毫秒
            "content_type": response.headers.get("content-type"),
            "response": response.json() if "application/json" in response.headers.get("content-type", "") else None
        }
    
    def test_root_endpoint(self):
        """测试根路由"""
        result = self._send_request("GET", "/")
        
        print(f"\n测试根路由 /:")
        print(f"状态码: {result['status_code']}")
        print(f"响应时间: {result['response_time']}ms")
        print(f"响应内容: {result['response']}")
        
        assert result["status_code"] == 200
        assert result["response"]["message"] == "Hello World"
        
    def test_hello_endpoint(self):
        """测试hello路由"""
        name = "test"
        result = self._send_request("GET", f"/hello/{name}")
        
        print(f"\n测试hello路由 /hello/{name}:")
        print(f"状态码: {result['status_code']}")
        print(f"响应时间: {result['response_time']}ms")
        print(f"响应内容: {result['response']}")
        
        assert result["status_code"] == 200
        assert result["response"]["message"] == f"Hello {name}"
        
    def test_docs_endpoint(self):
        """测试文档路由"""
        result = self._send_request("GET", "/docs")
        
        print(f"\n测试docs路由 /docs:")
        print(f"状态码: {result['status_code']}")
        print(f"响应时间: {result['response_time']}ms")
        print(f"响应类型: {result['content_type']}")
        
        assert result["status_code"] == 200
        assert "text/html" in result["content_type"]

if __name__ == "__main__":
    # 运行所有测试
    pytest.main(["-v", __file__]) 