#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatBot测试脚本
===============

测试Polytool ChatBot的各种功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import AgentManager, ChatBotAgent
from utils.logger import setup_logger


async def test_chatbot():
    """测试ChatBot功能"""
    
    # 设置日志
    logger = setup_logger("chatbot_test", "INFO")
    logger.info("🧪 开始ChatBot功能测试")
    
    # 创建智能体管理器
    agent_manager = AgentManager()
    
    # 注册ChatBot智能体类型
    agent_manager.register_agent(ChatBotAgent, "chatbot")
    
    # 创建ChatBot实例
    chatbot_id = "test_chatbot"
    chatbot = await agent_manager.create_agent(
        agent_type="chatbot",
        agent_id=chatbot_id,
        name="测试ChatBot",
        description="用于测试的ChatBot实例"
    )
    
    print("🤖 ChatBot测试开始")
    print("="*50)
    
    # 测试对话场景
    test_conversations = [
        "你好！",
        "你是谁？",
        "你能做什么？",
        "我想了解一下Polytool框架",
        "我们聊了多少轮了？",
        "谢谢你的帮助",
        "再见"
    ]
    
    session_id = "test_session"
    
    for i, message in enumerate(test_conversations, 1):
        print(f"\n👤 用户 [{i}]: {message}")
        
        # 构建输入数据
        input_data = {
            "message": message,
            "session_id": session_id
        }
        
        # 处理请求
        response = await agent_manager.process_request(chatbot_id, input_data)
        
        if response["status"] == "success":
            print(f"🤖 ChatBot [{i}]: {response['response']}")
            print(f"   💬 对话长度: {response['conversation_length']}")
        else:
            print(f"❌ 错误: {response.get('message', '未知错误')}")
        
        # 短暂暂停，模拟真实对话
        await asyncio.sleep(0.5)
    
    print("\n" + "="*50)
    
    # 显示对话统计信息
    conversation_info = chatbot.get_conversation_info(session_id)
    print("📊 对话统计:")
    print(f"  • 总消息数: {conversation_info['message_count']}")
    print(f"  • 用户消息: {conversation_info['conversation_summary']['user_messages']}")
    print(f"  • 助手回复: {conversation_info['conversation_summary']['assistant_messages']}")
    
    # 导出对话历史
    history = chatbot.export_conversation(session_id)
    print(f"  • 对话历史已导出: {len(history)} 条记录")
    
    # 测试智能体信息
    agent_info = chatbot.get_info()
    print(f"\n🔍 智能体信息:")
    print(f"  • ID: {agent_info['agent_id']}")
    print(f"  • 名称: {agent_info['name']}")
    print(f"  • 描述: {agent_info['description']}")
    print(f"  • 已初始化: {agent_info['is_initialized']}")
    
    # 测试管理器状态
    manager_status = agent_manager.get_status()
    print(f"\n🎛️ 管理器状态:")
    print(f"  • 注册的智能体类型: {manager_status['registered_agent_types']}")
    print(f"  • 活跃智能体数量: {manager_status['active_agents']}")
    print(f"  • 智能体类型: {manager_status['registered_types']}")
    print(f"  • 活跃智能体ID: {manager_status['active_agent_ids']}")
    
    # 清理资源
    await agent_manager.shutdown_all_agents()
    
    logger.info("✅ ChatBot功能测试完成")
    print("\n🎉 测试完成！")


if __name__ == "__main__":
    try:
        asyncio.run(test_chatbot())
    except KeyboardInterrupt:
        print("\n👋 测试被中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()