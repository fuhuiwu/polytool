#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API服务器模块
=============

提供RESTful API接口服务，包含ChatBot智能体接口
"""

import asyncio
import logging
import json
import sys
import os
from typing import Optional, Dict, Any
from datetime import datetime

# 添加项目根目录到sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger
from agent import AgentManager, ChatBotAgent
from config import settings
from orchestration.llm_gateway import create_llm_gateway


class APIServer:
    """
    API服务器类
    
    提供HTTP API接口，包含ChatBot功能
    """
    
    def __init__(self, llm_gateway=None, memory_manager=None, tool_gateway=None):
        """
        初始化API服务器
        
        Args:
            llm_gateway: LLM网关实例
            memory_manager: 记忆管理器实例
            tool_gateway: 工具网关实例
        """
        self.logger = get_logger("polytool.api_server")
        self.llm_gateway = llm_gateway
        self.memory_manager = memory_manager
        self.tool_gateway = tool_gateway
        self.server = None
        
        # 智能体管理器
        self.agent_manager = AgentManager()
        
        # 默认ChatBot实例ID
        self.default_chatbot_id = "default_chatbot"
        
    async def initialize(self):
        """异步初始化API服务器"""
        self.logger.info("正在初始化API服务器...")
        
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
        
        self.logger.info("API服务器初始化完成")
        
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
        
    async def run(self):
        """运行API服务器"""
        self.logger.info("API服务器开始运行...")
        self.logger.info("🤖 ChatBot已就绪，可以开始对话！")
        self.logger.info("📋 可用的API端点:")
        self.logger.info("  • POST /chat - 与ChatBot对话")
        self.logger.info("  • GET /agents - 获取智能体列表")
        self.logger.info("  • GET /agents/{agent_id} - 获取智能体信息")
        
        try:
            # 简单的命令行交互模式用于测试
            await self._start_cli_interface()
        except KeyboardInterrupt:
            self.logger.info("接收到中断信号")
        
    async def _start_cli_interface(self):
        """
        启动命令行交互界面（用于测试）
        """
        print("\n" + "="*50)
        print("🤖 Polytool ChatBot 交互模式")
        print("输入 'exit' 或 'quit' 退出，输入 'help' 查看帮助")
        print("="*50 + "\n")
        
        session_id = "cli_session"
        
        while True:
            try:
                # 获取用户输入
                user_input = input("👤 您: ").strip()
                
                if not user_input:
                    continue
                    
                # 处理特殊命令
                if user_input.lower() in ['exit', 'quit', '退出']:
                    print("👋 ChatBot: 再见！期待下次交流！")
                    break
                elif user_input.lower() in ['help', '帮助']:
                    self._show_help()
                    continue
                elif user_input.lower() in ['clear', '清空']:
                    await self._clear_conversation(session_id)
                    print("🧹 对话历史已清空")
                    continue
                elif user_input.lower() in ['status', '状态']:
                    await self._show_status(session_id)
                    continue
                
                # 与ChatBot对话
                response = await self.chat_with_bot(user_input, session_id)
                
                if response["status"] == "success":
                    print(f"🤖 ChatBot: {response['response']}")
                else:
                    print(f"❌ 错误: {response.get('message', '未知错误')}")
                    
            except KeyboardInterrupt:
                print("\n👋 ChatBot: 再见！")
                break
            except EOFError:
                print("\n👋 ChatBot: 再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
    
    def _show_help(self):
        """显示帮助信息"""
        print("\n📖 可用命令:")
        print("  • help/帮助 - 显示此帮助信息")
        print("  • clear/清空 - 清空当前对话历史")
        print("  • status/状态 - 显示对话状态信息")
        print("  • exit/quit/退出 - 退出程序")
        print("  • 其他输入 - 与ChatBot对话\n")
    
    async def _clear_conversation(self, session_id: str):
        """清空对话历史"""
        chatbot = await self.agent_manager.get_agent(self.default_chatbot_id)
        if chatbot:
            chatbot.conversation_manager.clear_conversation(session_id)
    
    async def _show_status(self, session_id: str):
        """显示状态信息"""
        chatbot = await self.agent_manager.get_agent(self.default_chatbot_id)
        if chatbot:
            info = chatbot.get_conversation_info(session_id)
            print(f"\n📊 对话状态:")
            print(f"  • 会话ID: {info['session_id']}")
            print(f"  • 消息数量: {info['message_count']}")
            print(f"  • 用户消息: {info['conversation_summary']['user_messages']}")
            print(f"  • 助手回复: {info['conversation_summary']['assistant_messages']}")
            if info['last_activity']:
                print(f"  • 最后活动: {info['last_activity']}")
            print()
    
    async def chat_with_bot(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        与ChatBot对话
        
        Args:
            message: 用户消息
            session_id: 会话ID
            
        Returns:
            Dict[str, Any]: ChatBot响应
        """
        input_data = {
            "message": message,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        return await self.agent_manager.process_request(self.default_chatbot_id, input_data)
    
    async def get_agents_info(self) -> Dict[str, Any]:
        """
        获取智能体信息
        
        Returns:
            Dict[str, Any]: 智能体信息
        """
        return {
            "status": "success",
            "data": {
                "manager_status": self.agent_manager.get_status(),
                "active_agents": self.agent_manager.get_active_agents()
            }
        }
    
    async def get_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """
        获取指定智能体信息
        
        Args:
            agent_id: 智能体ID
            
        Returns:
            Dict[str, Any]: 智能体信息
        """
        info = self.agent_manager.get_agent_info(agent_id)
        if info:
            return {"status": "success", "data": info}
        else:
            return {"status": "error", "message": f"智能体不存在: {agent_id}"}
    
    async def create_chatbot(self, agent_id: str, name: str = None, description: str = "") -> Dict[str, Any]:
        """
        创建新的ChatBot实例
        
        Args:
            agent_id: 智能体ID
            name: 智能体名称
            description: 智能体描述
            
        Returns:
            Dict[str, Any]: 创建结果
        """
        try:
            agent = await self.agent_manager.create_agent(
                agent_type="chatbot",
                agent_id=agent_id,
                name=name or f"ChatBot_{agent_id}",
                description=description
            )
            
            return {
                "status": "success",
                "message": f"ChatBot实例创建成功: {agent_id}",
                "data": agent.get_info()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"创建ChatBot实例失败: {str(e)}"
            }
    
    async def remove_chatbot(self, agent_id: str) -> Dict[str, Any]:
        """
        移除ChatBot实例
        
        Args:
            agent_id: 智能体ID
            
        Returns:
            Dict[str, Any]: 移除结果
        """
        if agent_id == self.default_chatbot_id:
            return {
                "status": "error",
                "message": "不能移除默认ChatBot实例"
            }
        
        success = await self.agent_manager.remove_agent(agent_id)
        
        if success:
            return {
                "status": "success", 
                "message": f"ChatBot实例已移除: {agent_id}"
            }
        else:
            return {
                "status": "error",
                "message": f"移除ChatBot实例失败: {agent_id}"
            }
        
    async def shutdown(self):
        """关闭API服务器"""
        self.logger.info("正在关闭API服务器...")
        
        # 关闭所有智能体
        await self.agent_manager.shutdown_all_agents()
        
        self.logger.info("API服务器已关闭")


async def chat_mode():
    """聊天模式 - 交互式ChatBot对话"""
    print("🤖 Polytool ChatBot 聊天模式")
    print("=" * 50)
    print("💡 提示: 输入 'quit' 或 'exit' 退出聊天")
    print("=" * 50)
    
    # 初始化LLM网关
    llm_gateway = create_llm_gateway(settings)
    await llm_gateway.initialize()
    
    # 初始化API服务器
    server = APIServer(llm_gateway=llm_gateway)
    try:
        await server.initialize()
        
        # 使用默认的ChatBot实例
        agent_id = server.default_chatbot_id
        print(f"✅ ChatBot已就绪 (ID: {agent_id})")
        print()
        
        # 开始对话循环
        session_id = "interactive_session"
        message_count = 0
        
        while True:
            try:
                # 获取用户输入
                user_input = input("👤 您: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("\n👋 再见！感谢使用Polytool ChatBot！")
                    break
                
                message_count += 1
                print(f"🔄 处理中...", end="\r")
                
                # 调用ChatBot
                response = await server.chat_with_bot(
                    message=user_input,
                    session_id=session_id
                )
                
                # 显示回复
                if response.get("status") == "success":
                    bot_reply = response.get("response", "")
                    conversation_length = response.get("conversation_length", 0)
                    
                    print(f"\r🤖 ChatBot: {bot_reply}")
                    print(f"   💬 对话长度: {conversation_length} | 消息编号: {message_count}")
                    print()
                else:
                    error_msg = response.get("message", "未知错误")
                    print(f"\r❌ 错误: {error_msg}")
                    print()
                
            except KeyboardInterrupt:
                print("\n\n⏹️  收到中断信号，正在退出...")
                break
            except Exception as e:
                print(f"\n❌ 处理消息时出错: {e}")
                print()
        
    finally:
        # 清理资源
        await server.shutdown()


def main():
    """主入口函数"""
    print("🚀 Polytool API服务器")
    print("选择运行模式:")
    print("1. 聊天模式 (chat)")
    print("2. 服务器模式 (server) - 暂未实现")
    print()
    
    try:
        mode = input("请选择模式 [chat]: ").strip().lower() or "chat"
        
        if mode in ["chat", "c", "1"]:
            asyncio.run(chat_mode())
        elif mode in ["server", "s", "2"]:
            print("⚠️  服务器模式暂未实现")
        else:
            print(f"❌ 未知模式: {mode}")
            
    except KeyboardInterrupt:
        print("\n👋 退出程序")
    except Exception as e:
        print(f"❌ 程序出错: {e}")


if __name__ == "__main__":
    main()