#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polytool - 通用智能体框架
====================================

主启动入口文件，负责初始化系统各层组件并启动API服务
"""

import sys
import os
import argparse
import asyncio
import logging
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from utils.logger import setup_logger
from orchestration.llm_gateway import create_llm_gateway
from orchestration.memory_manager import MemoryManager
from orchestration.tool_gateway import ToolGateway
from api.server import APIServer

# 尝试导入HTTP服务器
try:
    from api.http_server import HTTPServer
    HTTP_SERVER_AVAILABLE = True
except ImportError:
    try:
        from api.simple_http_server import SimpleHTTPServer as HTTPServer
        HTTP_SERVER_AVAILABLE = True
    except ImportError:
        HTTPServer = None
        HTTP_SERVER_AVAILABLE = False


class PolytoolApplication:
    """
    Polytool应用程序主类
    
    负责整个应用程序的初始化、配置和启动
    """
    
    def __init__(self, config_path: Optional[str] = None, mode: str = "http"):
        """
        初始化Polytool应用程序
        
        Args:
            config_path: 配置文件路径，可选
            mode: 运行模式 (http, cli, chat)
        """
        self.config_path = config_path
        self.mode = mode
        self.logger = None
        self.llm_gateway = None
        self.memory_manager = None
        self.tool_gateway = None
        self.api_server = None
        self.http_server = None
        
    async def initialize(self):
        """
        异步初始化应用程序
        """
        try:
            # 1. 初始化日志系统
            self.logger = setup_logger(
                name="polytool",
                level=settings.LOG_LEVEL,
                log_file=settings.LOG_FILE_PATH
            )
            self.logger.info("🚀 Polytool启动中...")
            
            # 2. 初始化管理层组件
            await self._initialize_orchestration_layer()
            
            # 3. 初始化API服务器
            await self._initialize_api_server()
            
            self.logger.info("✅ Polytool初始化完成")
            
        except Exception as e:
            self.logger.error(f"❌ Polytool初始化失败: {e}")
            raise
    
    async def _initialize_orchestration_layer(self):
        """
        初始化管理层组件
        """
        self.logger.info("🔧 初始化管理层组件...")
        
        # LLM网关
        self.llm_gateway = create_llm_gateway(settings)
        await self.llm_gateway.initialize()
        self.logger.info("✓ LLM网关初始化完成")
        
        # 记忆与知识库管理
        self.memory_manager = MemoryManager()
        await self.memory_manager.initialize()
        self.logger.info("✓ 记忆管理器初始化完成")
        
        # 工具网关
        self.tool_gateway = ToolGateway()
        await self.tool_gateway.initialize()
        self.logger.info("✓ 工具网关初始化完成")
    
    async def _initialize_api_server(self):
        """
        初始化API服务器
        """
        self.logger.info("🌐 初始化API服务器...")
        
        if self.mode == "http":
            # HTTP服务器模式
            if HTTP_SERVER_AVAILABLE:
                self.http_server = HTTPServer(
                    llm_gateway=self.llm_gateway,
                    memory_manager=self.memory_manager,
                    tool_gateway=self.tool_gateway
                )
                await self.http_server.initialize()
                self.logger.info("✓ HTTP服务器初始化完成")
            else:
                self.logger.error("❌ HTTP服务器不可用，请安装 fastapi 或使用 CLI 模式")
                raise RuntimeError("HTTP服务器依赖不满足")
        else:
            # CLI/Chat模式
            self.api_server = APIServer(
                llm_gateway=self.llm_gateway,
                memory_manager=self.memory_manager,
                tool_gateway=self.tool_gateway
            )
            await self.api_server.initialize()
            self.logger.info("✓ CLI服务器初始化完成")
    
    async def run(self):
        """
        运行应用程序
        """
        try:
            if self.mode == "http":
                self.logger.info(f"🌟 Polytool HTTP服务启动，监听端口: {settings.SERVER_PORT}")
                self.logger.info(f"📚 API文档地址: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/docs")
                # 启动HTTP服务器
                await self.http_server.run()
            else:
                self.logger.info(f"🌟 Polytool {self.mode.upper()}模式启动")
                # 启动CLI服务器
                await self.api_server.run()
            
        except KeyboardInterrupt:
            self.logger.info("👋 接收到中断信号，正在关闭服务...")
        except Exception as e:
            self.logger.error(f"❌ 应用运行异常: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """
        优雅关闭应用程序
        """
        self.logger.info("🔄 正在优雅关闭应用程序...")
        
        # 关闭各个组件
        if self.http_server:
            await self.http_server.shutdown()
            
        if self.api_server:
            await self.api_server.shutdown()
        
        if self.tool_gateway:
            await self.tool_gateway.shutdown()
            
        if self.memory_manager:
            await self.memory_manager.shutdown()
            
        if self.llm_gateway:
            await self.llm_gateway.shutdown()
        
        self.logger.info("✅ 应用程序已安全关闭")


def create_arg_parser():
    """
    创建命令行参数解析器
    """
    parser = argparse.ArgumentParser(
        description="Polytool - 通用智能体框架",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py                    # 使用默认配置启动
  python main.py --config config.yaml  # 指定配置文件
  python main.py --debug           # 启用调试模式
  python main.py --port 8080       # 指定端口
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="启用调试模式"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        help="API服务器端口"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="API服务器主机地址"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"Polytool {settings.VERSION}"
    )
    
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["http", "cli", "chat"],
        default="http",
        help="运行模式: http(HTTP服务器), cli(命令行界面), chat(聊天模式)"
    )
    
    return parser


async def main():
    """
    主函数
    """
    # 解析命令行参数
    parser = create_arg_parser()
    args = parser.parse_args()
    
    # 根据参数更新配置
    if args.debug:
        settings.LOG_LEVEL = "DEBUG"
    
    if args.port:
        settings.SERVER_PORT = args.port
        
    if args.host:
        settings.SERVER_HOST = args.host
    
    # 创建并运行应用程序
    app = PolytoolApplication(config_path=args.config, mode=args.mode)
    
    try:
        await app.initialize()
        await app.run()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Polytool需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 运行主程序
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 程序异常退出: {e}")
        sys.exit(1)
