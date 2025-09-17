#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM集成测试脚本
===============

测试ChatBot与LLM的集成功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from orchestration.llm_gateway import create_llm_gateway, LLMMessage
from agent.agents.chatbot import ChatBotAgent
from agent import AgentManager
from utils.logger import setup_logger


async def test_llm_gateway():
    """测试LLM网关基础功能"""
    print("🔧 测试LLM网关基础功能")
    print("=" * 40)
    
    # 创建LLM网关
    llm_gateway = create_llm_gateway(settings)
    
    try:
        await llm_gateway.initialize()
        
        # 获取可用的提供商
        providers = llm_gateway.get_available_providers()
        print(f"可用的LLM提供商: {providers}")
        
        if not providers:
            print("⚠️  没有配置可用的LLM提供商")
            print("请在.env文件中配置OPENAI_API_KEY或CLAUDE_API_KEY")
            return False
        
        # 测试简单对话
        system_prompt = "你是一个友好的AI助手，请用中文简洁地回答用户问题。"
        user_message = "你好，请介绍一下你自己。"
        
        print(f"\n💬 测试对话:")
        print(f"系统提示: {system_prompt}")
        print(f"用户消息: {user_message}")
        
        try:
            response = await llm_gateway.generate_simple(
                system_prompt=system_prompt,
                user_message=user_message
            )
            print(f"✅ LLM回复: {response}")
            return True
            
        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ LLM网关初始化失败: {e}")
        return False
    
    finally:
        await llm_gateway.shutdown()


async def test_chatbot_with_llm():
    """测试ChatBot与LLM的集成"""
    print("\n🤖 测试ChatBot与LLM集成")
    print("=" * 40)
    
    # 创建LLM网关
    llm_gateway = create_llm_gateway(settings)
    
    try:
        await llm_gateway.initialize()
        
        # 检查是否有可用的LLM提供商
        providers = llm_gateway.get_available_providers()
        if not providers:
            print("⚠️  跳过LLM集成测试（没有配置LLM提供商）")
            return True
        
        # 创建智能体管理器
        agent_manager = AgentManager()
        
        # 注入LLM网关
        agent_manager.inject_dependencies(
            llm_gateway=llm_gateway,
            memory_manager=None,
            tool_gateway=None
        )
        
        # 注册ChatBot类型
        agent_manager.register_agent(ChatBotAgent, "chatbot")
        
        # 创建ChatBot实例
        agent = await agent_manager.create_agent(
            agent_type="chatbot",
            agent_id="llm_test_chatbot",
            name="LLM测试ChatBot",
            description="用于测试LLM集成的ChatBot实例"
        )
        
        print(f"✅ ChatBot实例已创建: {agent.name}")
        
        # 测试对话
        test_messages = [
            "你好！",
            "请用一句话介绍一下Python编程语言。",
            "谢谢你的回答。",
            "你还记得我刚才问了什么问题吗？",
            "再见！"
        ]
        
        session_id = "llm_test_session"
        
        print(f"\n💬 开始LLM对话测试:")
        print("-" * 30)
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n👤 用户 [{i}]: {message}")
            
            # 调用ChatBot处理消息
            input_data = {
                "message": message,
                "session_id": session_id
            }
            
            response = await agent_manager.process_request("llm_test_chatbot", input_data)
            
            if response.get("status") == "success":
                bot_reply = response.get("response", "")
                conversation_length = response.get("conversation_length", 0)
                
                print(f"🤖 ChatBot [{i}]: {bot_reply}")
                print(f"   💬 对话长度: {conversation_length}")
                
                # 检查是否是LLM生成的回复
                if len(bot_reply) > 100 or "Python" in bot_reply:
                    print("   🎯 检测到LLM生成的智能回复")
                
            else:
                error_msg = response.get("message", "未知错误")
                print(f"❌ 错误: {error_msg}")
        
        print(f"\n✅ LLM集成测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ LLM集成测试失败: {e}")
        return False
    
    finally:
        # 清理资源
        await agent_manager.shutdown_all_agents()
        await llm_gateway.shutdown()


async def main():
    """主测试函数"""
    print("🧪 LLM集成功能测试")
    print("=" * 50)
    
    # 设置日志
    logger = setup_logger("llm_test", level="INFO")
    
    success_count = 0
    total_tests = 2
    
    # 测试1: LLM网关基础功能
    if await test_llm_gateway():
        success_count += 1
    
    # 测试2: ChatBot与LLM集成
    if await test_chatbot_with_llm():
        success_count += 1
    
    # 总结
    print("\n" + "=" * 50)
    print(f"📊 测试结果:")
    print(f"   ✅ 成功: {success_count}/{total_tests}")
    print(f"   ❌ 失败: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 所有LLM集成测试都通过了！")
    else:
        print(f"\n⚠️  有 {total_tests - success_count} 个测试失败")
        print("\n💡 提示:")
        print("   - 确保在.env文件中配置了正确的API密钥")
        print("   - 检查网络连接是否正常")
        print("   - 验证API密钥是否有效")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ 测试中断")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")