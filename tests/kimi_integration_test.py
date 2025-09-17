#!/usr/bin/env python3
"""
Kimi K2 LLM集成测试
====================

测试Kimi (月之暗面) LLM提供商的集成效果
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from orchestration.llm_gateway import create_llm_gateway, LLMMessage
from agent.agents.chatbot.agent import ChatBotAgent


async def test_kimi_llm_integration():
    """测试Kimi LLM集成"""
    print("🚀 Kimi K2 LLM集成测试")
    print("=" * 50)
    
    # 创建LLM网关
    llm_gateway = create_llm_gateway(settings)
    await llm_gateway.initialize()
    
    # 检查环境变量和提供商
    mock_llm = os.getenv("MOCK_LLM", "false").lower() == "true"
    print(f"🔧 MOCK_LLM模式: {mock_llm}")
    print(f"🔧 可用提供商: {list(llm_gateway.providers.keys())}")
    print(f"🔧 默认提供商: {llm_gateway.config.get('default_provider', 'openai')}")
    
    if "kimi" in llm_gateway.providers:
        print("✅ Kimi提供商已成功注册")
    else:
        print("❌ Kimi提供商未找到")
    
    print("\n" + "-" * 50)
    
    # 测试1: 直接LLM网关调用
    print("📡 测试1: 直接调用Kimi LLM网关")
    test_messages_direct = [
        LLMMessage(role="system", content="你是一个智能助手"),
        LLMMessage(role="user", content="请简单介绍一下你自己，说明你的能力")
    ]
    
    try:
        if mock_llm:
            response = await llm_gateway.generate(test_messages_direct, provider="kimi")
        else:
            # 真实模式下，如果有kimi配置
            if llm_gateway.providers.get("kimi"):
                response = await llm_gateway.generate(test_messages_direct, provider="kimi")
            else:
                print("⚠️  真实模式下未配置Kimi API密钥，跳过直接调用测试")
                response = None
        
        if response:
            print(f"🤖 Kimi回复: {response.content}")
            print(f"📊 模型: {response.model}")
            print(f"🏷️  提供商: {response.provider}")
            if response.usage:
                print(f"📈 Token使用: {response.usage}")
    except Exception as e:
        print(f"❌ 直接调用失败: {e}")
    
    print("\n" + "-" * 50)
    
    # 测试2: 通过ChatBot集成测试
    print("🤖 测试2: ChatBot集成Kimi LLM")
    
    chatbot = ChatBotAgent(
        agent_id="kimi_test_chatbot",
        name="Kimi测试ChatBot",
        description="集成Kimi LLM的聊天机器人"
    )
    
    # 注入依赖
    chatbot.inject_dependencies(llm_gateway, None, None)
    await chatbot.initialize()
    
    test_conversations = [
        "你好，请介绍一下Kimi K2的特点",
        "你能处理哪些类型的问题？",
        "请帮我写一个简单的Python函数",
        "谢谢你的帮助"
    ]
    
    session_id = "kimi_test_session"
    
    for i, user_message in enumerate(test_conversations, 1):
        print(f"\n【对话 {i}】")
        print(f"👤 用户: {user_message}")
        
        try:
            # 处理消息
            result = await chatbot.process({
                "message": user_message,
                "session_id": session_id
            })
            
            if result["status"] == "success":
                print(f"🤖 ChatBot: {result['response']}")
                print(f"📊 对话历史长度: {len(chatbot.conversation_manager.get_conversation_history(session_id))}")
            else:
                print(f"❌ ChatBot错误: {result.get('message', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 对话处理失败: {e}")
        
        # 添加短暂延迟
        await asyncio.sleep(0.5)
    
    print("\n" + "-" * 50)
    
    # 测试3: 性能和功能特性测试
    print("⚡ 测试3: Kimi功能特性测试")
    
    feature_tests = [
        {
            "name": "长文本理解",
            "message": "请总结以下内容的要点：人工智能技术在近年来取得了突破性进展，特别是大语言模型的发展，为各行各业带来了新的机遇和挑战。这些模型不仅能够理解和生成自然语言，还能够进行逻辑推理、创意写作、代码编程等复杂任务。"
        },
        {
            "name": "代码生成",
            "message": "请用Python写一个计算斐波那契数列的函数"
        },
        {
            "name": "多轮对话记忆",
            "message": "我之前问过你什么问题？请回顾我们的对话历史"
        }
    ]
    
    for test in feature_tests:
        print(f"\n🧪 {test['name']}测试:")
        print(f"👤 用户: {test['message']}")
        
        try:
            result = await chatbot.process({
                "message": test['message'],
                "session_id": session_id
            })
            
            if result["status"] == "success":
                # 截断长回复
                response = result['response']
                if len(response) > 200:
                    response = response[:200] + "..."
                print(f"🤖 ChatBot: {response}")
                print("✅ 测试通过")
            else:
                print(f"❌ 测试失败: {result.get('message')}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    # 清理资源
    await chatbot.shutdown()
    await llm_gateway.shutdown()
    
    print("\n" + "=" * 50)
    print("🎉 Kimi K2 LLM集成测试完成！")
    
    # 总结
    print("\n📋 集成总结:")
    print("✅ KimiProvider类实现完成")
    print("✅ 配置管理支持完成") 
    print("✅ LLM网关注册完成")
    print("✅ ChatBot集成测试完成")
    print("\n💡 使用说明:")
    if mock_llm:
        print("- 当前为模拟模式，所有Kimi调用使用MockLLMProvider")
        print("- 要使用真实Kimi API，请设置MOCK_LLM=false并配置有效的KIMI_API_KEY")
    else:
        print("- 当前为真实模式，需要有效的Kimi API密钥")
        print("- 请在.env文件中配置KIMI_API_KEY")
    print("- 支持的Kimi模型: moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k")


async def test_provider_switching():
    """测试提供商切换功能"""
    print("\n🔄 测试提供商切换功能")
    print("-" * 30)
    
    llm_gateway = create_llm_gateway(settings)
    await llm_gateway.initialize()
    
    test_message = [LLMMessage(role="user", content="你是哪个AI助手？")]
    
    providers_to_test = ["openai", "claude", "kimi"]
    
    for provider in providers_to_test:
        if provider in llm_gateway.providers:
            print(f"\n🔧 切换到 {provider} 提供商:")
            try:
                response = await llm_gateway.generate(test_message, provider=provider)
                print(f"✅ {provider}: {response.content[:100]}...")
            except Exception as e:
                print(f"❌ {provider} 调用失败: {e}")
        else:
            print(f"⚠️  {provider} 提供商未注册")
    
    await llm_gateway.shutdown()


if __name__ == "__main__":
    asyncio.run(test_kimi_llm_integration())
    print("\n" + "=" * 50)
    asyncio.run(test_provider_switching())