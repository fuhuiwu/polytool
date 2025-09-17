#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单HTTP服务器实现
==================

使用标准库实现的HTTP服务器，无需额外依赖
"""

import json
import asyncio
import os
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from threading import Thread
import socket
from typing import Dict, Any
from datetime import datetime

from utils.logger import get_logger
from agent import AgentManager, ChatBotAgent
from config import settings


class SimpleHTTPHandler(BaseHTTPRequestHandler):
    """简单HTTP请求处理器"""
    
    server_instance = None  # 类变量，存储服务器实例引用
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 聊天页面路由
        if path == '/chat-ui' or path == '/':
            self._serve_chat_page()
        elif path == '/health':
            self._send_json_response({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "server": "simple_http",
                "agents_count": len(self.server_instance.agent_manager.active_agents) if self.server_instance else 0
            })
        elif path == '/docs':
            self._send_html_response("""
            <!DOCTYPE html>
            <html>
            <head><title>Polytool API文档</title></head>
            <body>
                <h1>Polytool API 简单文档</h1>
                <h2>可用端点:</h2>
                <ul>
                    <li><strong>GET /</strong> - 聊天Web界面</li>
                    <li><strong>GET /chat-ui</strong> - 聊天Web界面</li>
                    <li><strong>GET /health</strong> - 健康检查</li>
                    <li><strong>POST /chat</strong> - 与ChatBot对话</li>
                    <li><strong>GET /static/*</strong> - 静态文件服务</li>
                </ul>
                <h3>POST /chat 示例:</h3>
                <pre>
{
    "message": "你好",
    "session_id": "test_session"
}
                </pre>
                <p>注意：这是简化版HTTP服务器。要获得完整功能，请安装 fastapi 和 uvicorn。</p>
                <p><a href="/chat-ui">点击进入聊天界面</a></p>
            </body>
            </html>
            """)
        elif path.startswith('/static/'):
            self._serve_static_file(path)
        else:
            self._send_error(404, "Not Found")
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/chat':
            try:
                # 读取请求体
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # 解析JSON
                try:
                    request_data = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError:
                    self._send_error(400, "Invalid JSON")
                    return
                
                # 验证必需字段
                if 'message' not in request_data:
                    self._send_error(400, "Missing 'message' field")
                    return
                
                # 处理聊天请求（同步方式）
                if self.server_instance:
                    response = self.server_instance._process_chat_sync(request_data)
                    self._send_json_response(response)
                else:
                    self._send_error(500, "Server not initialized")
                    
            except Exception as e:
                self._send_error(500, f"Internal server error: {str(e)}")
        else:
            self._send_error(404, "Not Found")
    
    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_data.encode('utf-8'))
    
    def _send_html_response(self, html: str, status_code: int = 200):
        """发送HTML响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def _send_error(self, status_code: int, message: str):
        """发送错误响应"""
        self._send_json_response({
            "error": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }, status_code)
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        if self.server_instance and self.server_instance.logger:
            self.server_instance.logger.info(f"{self.client_address[0]} - {format % args}")

    def _serve_chat_page(self):
        """提供聊天页面"""
        try:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            chat_html_path = os.path.join(current_dir, 'web', 'templates', 'chat.html')
            
            if os.path.exists(chat_html_path):
                with open(chat_html_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self._send_html_response(content)
            else:
                self._send_error(404, "Chat page not found")
        except Exception as e:
            self._send_error(500, f"Error serving chat page: {str(e)}")

    def _serve_static_file(self, path):
        """提供静态文件服务"""
        try:
            # 移除 /static/ 前缀
            file_path = path[8:]  # 去掉 '/static/'
            
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            full_path = os.path.join(current_dir, 'web', 'static', file_path)
            
            # 安全检查：确保路径在static目录内
            static_dir = os.path.join(current_dir, 'web', 'static')
            if not os.path.abspath(full_path).startswith(os.path.abspath(static_dir)):
                self._send_error(403, "Forbidden")
                return
            
            if os.path.exists(full_path) and os.path.isfile(full_path):
                # 获取MIME类型
                mime_type, _ = mimetypes.guess_type(full_path)
                if mime_type is None:
                    mime_type = 'application/octet-stream'
                
                # 读取文件内容
                with open(full_path, 'rb') as f:
                    content = f.read()
                
                # 发送响应
                self.send_response(200)
                self.send_header('Content-Type', mime_type)
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Cache-Control', 'public, max-age=3600')  # 缓存1小时
                self.end_headers()
                self.wfile.write(content)
            else:
                self._send_error(404, "File not found")
                
        except Exception as e:
            self._send_error(500, f"Error serving static file: {str(e)}")


class SimpleHTTPServer:
    """简单HTTP服务器类"""
    
    def __init__(self, llm_gateway=None, memory_manager=None, tool_gateway=None):
        """初始化简单HTTP服务器"""
        self.logger = get_logger("polytool.simple_http_server")
        self.llm_gateway = llm_gateway
        self.memory_manager = memory_manager
        self.tool_gateway = tool_gateway
        
        # 智能体管理器
        self.agent_manager = AgentManager()
        self.default_chatbot_id = "default_chatbot"
        
        self.httpd = None
        self.server_thread = None
        self._shutdown_event = False  # 添加关闭标志
        
        # 将服务器实例传递给处理器类
        SimpleHTTPHandler.server_instance = self
        
    async def initialize(self):
        """初始化简单HTTP服务器"""
        self.logger.info("正在初始化简单HTTP服务器...")
        
        # 注入依赖到智能体管理器
        self.agent_manager.inject_dependencies(
            self.llm_gateway, 
            self.memory_manager, 
            self.tool_gateway
        )
        
        # 注册ChatBot智能体类型
        self.agent_manager.register_agent(ChatBotAgent, "chatbot")
        
        # 创建默认的ChatBot实例
        await self._create_default_chatbot()
        
        self.logger.info("简单HTTP服务器初始化完成")
        
    async def _create_default_chatbot(self):
        """创建默认的ChatBot实例"""
        try:
            await self.agent_manager.create_agent(
                agent_type="chatbot",
                agent_id=self.default_chatbot_id,
                name="默认ChatBot",
                description="Polytool框架的默认聊天助手"
            )
            self.logger.info("默认ChatBot实例创建成功")
        except Exception as e:
            self.logger.error(f"创建默认ChatBot实例失败: {e}")
            raise
    
    def _process_chat_sync(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """同步处理聊天请求（用于HTTP处理器）"""
        try:
            # 获取ChatBot实例
            chatbot = self.agent_manager.active_agents.get(self.default_chatbot_id)
            if not chatbot:
                return {
                    "status": "error",
                    "message": "ChatBot未初始化",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 创建事件循环来处理异步调用
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # 异步处理对话
            result = loop.run_until_complete(chatbot.process({
                "message": request_data["message"],
                "session_id": request_data.get("session_id", "default"),
                "context": request_data.get("context", {})
            }))
            
            if result["status"] == "success":
                return {
                    "status": "success",
                    "response": result["response"],
                    "session_id": request_data.get("session_id", "default"),
                    "timestamp": datetime.now().isoformat(),
                    "conversation_length": result.get("conversation_length", 0)
                }
            else:
                return {
                    "status": "error",
                    "message": result.get("message", "ChatBot处理失败"),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"聊天请求处理异常: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run(self, host: str = None, port: int = None):
        """运行简单HTTP服务器"""
        host = host or settings.SERVER_HOST
        port = port or settings.SERVER_PORT
        
        # 检查端口是否可用
        if self._is_port_in_use(host, port):
            self.logger.warning(f"端口 {port} 已被占用，尝试寻找其他可用端口...")
            port = self._find_free_port(host, port)
        
        self.logger.info(f"🚀 启动简单HTTP服务器...")
        self.logger.info(f"📍 监听地址: http://{host}:{port}")
        self.logger.info(f"📚 API文档: http://{host}:{port}/docs")
        self.logger.info(f"🔍 健康检查: http://{host}:{port}/health")
        
        # 创建HTTP服务器
        try:
            self.httpd = HTTPServer((host, port), SimpleHTTPHandler)
            
            # 在单独线程中运行服务器
            self.server_thread = Thread(target=self.httpd.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.logger.info("✅ HTTP服务器已启动，按 Ctrl+C 停止")
            
            # 保持主线程运行
            try:
                while not self._shutdown_event:
                    await asyncio.sleep(0.1)  # 减少睡眠时间以更快响应关闭信号
            except KeyboardInterrupt:
                self.logger.info("接收到中断信号")
                
        except Exception as e:
            self.logger.error(f"HTTP服务器启动失败: {e}")
            raise
    
    def _is_port_in_use(self, host: str, port: int) -> bool:
        """检查端口是否被占用"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return False
            except socket.error:
                return True
    
    def _find_free_port(self, host: str, start_port: int) -> int:
        """寻找可用端口"""
        for port in range(start_port + 1, start_port + 100):
            if not self._is_port_in_use(host, port):
                return port
        raise RuntimeError("无法找到可用端口")
    
    async def shutdown(self):
        """关闭简单HTTP服务器"""
        self.logger.info("正在关闭简单HTTP服务器...")
        
        # 设置关闭标志，让run循环退出
        self._shutdown_event = True
        
        try:
            if self.httpd:
                # 首先停止服务器接受新连接
                self.httpd.shutdown()
                self.httpd.server_close()
                self.logger.debug("HTTP服务器已停止接受新连接")
            
            if self.server_thread and self.server_thread.is_alive():
                # 等待线程结束，但不要无限等待
                self.server_thread.join(timeout=2)  # 减少超时时间
                if self.server_thread.is_alive():
                    self.logger.warning("服务器线程未能在2秒内正常结束")
                else:
                    self.logger.debug("服务器线程已正常结束")
        
        except Exception as e:
            self.logger.error(f"关闭HTTP服务器时出错: {e}")
        
        self.logger.info("简单HTTP服务器已关闭")