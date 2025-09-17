#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单Web服务器启动脚本
==================

用于测试ChatBot Web客户端的独立启动脚本
"""

import json
import os
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime

class WebTestHandler(BaseHTTPRequestHandler):
    """简化的Web测试处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/index.html':
            self._send_html_response("""
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <title>Polytool ChatBot 测试服务器</title>
            </head>
            <body>
                <h1>Polytool ChatBot 测试服务器</h1>
                <p><a href="/chat">点击进入聊天界面</a></p>
                <p>测试服务器运行中 - " + datetime.now().isoformat() + "</p>
            </body>
            </html>
            """)
        elif path == '/chat' or path == '/chat-ui':
            self._serve_chat_page()
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
                
                # 模拟ChatBot响应
                message = request_data.get('message', '')
                response_text = f"收到消息: {message}\\n\\n这是一个测试响应，用于验证Web客户端功能。"
                
                response = {
                    "status": "success",
                    "response": response_text,
                    "session_id": request_data.get("session_id", "test_session"),
                    "timestamp": datetime.now().isoformat()
                }
                
                self._send_json_response(response)
                    
            except Exception as e:
                self._send_error(500, f"Internal server error: {str(e)}")
        else:
            self._send_error(404, "Not Found")
    
    def _send_json_response(self, data, status_code=200):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_data.encode('utf-8'))
    
    def _send_html_response(self, html, status_code=200):
        """发送HTML响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def _send_error(self, status_code, message):
        """发送错误响应"""
        self._send_json_response({
            "error": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }, status_code)

    def _serve_chat_page(self):
        """提供聊天页面"""
        try:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            chat_html_path = os.path.join(current_dir, 'web', 'templates', 'chat.html')
            
            if os.path.exists(chat_html_path):
                with open(chat_html_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self._send_html_response(content)
            else:
                self._send_error(404, f"Chat page not found at {chat_html_path}")
        except Exception as e:
            self._send_error(500, f"Error serving chat page: {str(e)}")

    def _serve_static_file(self, path):
        """提供静态文件服务"""
        try:
            # 移除 /static/ 前缀
            file_path = path[8:]  # 去掉 '/static/'
            
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
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
                self.send_header('Cache-Control', 'public, max-age=3600')
                self.end_headers()
                self.wfile.write(content)
            else:
                self._send_error(404, f"File not found: {full_path}")
                
        except Exception as e:
            self._send_error(500, f"Error serving static file: {str(e)}")

    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {self.client_address[0]} - {format % args}")


def main():
    """主函数"""
    host = '127.0.0.1'
    port = 8080
    
    print(f"🚀 启动Web测试服务器...")
    print(f"📍 监听地址: http://{host}:{port}")
    print(f"💬 聊天界面: http://{host}:{port}/chat")
    print(f"⚡ 按 Ctrl+C 停止服务器\\n")
    
    try:
        httpd = HTTPServer((host, port), WebTestHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")


if __name__ == '__main__':
    main()