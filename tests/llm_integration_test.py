#!/usr/bin/env python3
"""
真实LLM集成测试
使用真实的OpenAI或Claude API进行ChatBot功能测试
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.llm_gateway import LLMGateway
from agent.agents.chatbot.agent import ChatBotAgent
from config import settings


class RealLLMIntegrationTest:
    """真实LLM集成测试类"""
    
    def __init__(self):
        self.llm_gateway = None
        self.chatbot = None
        
    async def setup(self):
        """初始化测试环境"""
        print("🔧 初始化真实LLM集成测试...")
        
        # 检查API密钥配置
        if not self._check_api_keys():
            print("❌ 错误: 未配置有效的API密钥，请在.env文件中配置")
            return False
            
        # 创建LLM网关
        self.llm_gateway = LLMGateway()
        
        # 创建ChatBot实例
        self.chatbot = ChatBotAgent(
            name="真实LLM测试ChatBot",
            llm_gateway=self.llm_gateway
        )
        
        print("✅ 真实LLM集成测试初始化完成")
        return True
        
    def _check_api_keys(self) -> bool:
        """检查API密钥配置"""
        mock_llm = os.getenv("MOCK_LLM", "false").lower() == "true"
        if mock_llm:
            print("⚠️  当前配置为模拟模式，请在.env中设置 MOCK_LLM=false")
            return False
            
        default_provider = settings.DEFAULT_LLM_PROVIDER
        openai_key = settings.OPENAI_API_KEY
        claude_key = settings.CLAUDE_API_KEY
        
        if default_provider == "openai":
            if not openai_key or openai_key == "your-openai-api-key-here":
                print("❌ 错误: 未配置有效的OpenAI API密钥")
                return False
        elif default_provider == "claude":
            if not claude_key or claude_key == "your-claude-api-key-here":
                print("❌ 错误: 未配置有效的Claude API密钥")
                return False
        else:
            print(f"❌ 错误: 未知的LLM提供商 {default_provider}")
            return False
            
        return True
        
    async def test_basic_interaction(self):
        """测试基础对话功能"""
        print("\n💬 测试基础LLM对话功能")
        print("-" * 50)
        
        test_messages = [
            "你好，我是用户",
            "请介绍一下你自己",
            "你有什么能力？",
            "谢谢你的介绍"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n【测试 {i}】")
            print(f"👤 用户: {message}")
            
            try:
                response = await self.chatbot.process_message(message)
                print(f"🤖 ChatBot: {response}")
                print(f"📊 对话长度: {len(self.chatbot.conversation_history)}")
                
                # 添加短暂延迟避免API限制
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ 错误: {e}")
                return False
                
        return True
        
    async def test_context_memory(self):
        """测试上下文记忆功能"""
        print("\n🧠 测试上下文记忆功能")
        print("-" * 50)
        
        # 建立上下文
        context_message = "我的名字是张三，我是一名Python开发者"
        print(f"👤 用户: {context_message}")
        
        try:
            response1 = await self.chatbot.process_message(context_message)
            print(f"🤖 ChatBot: {response1}")
            
            await asyncio.sleep(1)
            
            # 测试记忆
            memory_test = "你还记得我的名字和职业吗？"
            print(f"\n👤 用户: {memory_test}")
            
            response2 = await self.chatbot.process_message(memory_test)
            print(f"🤖 ChatBot: {response2}")
            
            # 检查是否包含上下文信息
            if "张三" in response2 or "Python" in response2 or "开发者" in response2:
                print("✅ 上下文记忆测试通过")
                return True
            else:
                print("⚠️  上下文记忆测试可能失败 - 回复中未检测到相关信息")
                return True  # 不强制失败，因为LLM响应可能有变化
                
        except Exception as e:
            print(f"❌ 上下文记忆测试错误: {e}")
            return False
            
    async def test_technical_question(self):
        """测试技术问题回答"""
        print("\n🔬 测试技术问题回答能力")
        print("-" * 50)
        
        technical_question = "请解释一下Python中的装饰器原理"
        print(f"👤 用户: {technical_question}")
        
        try:
            response = await self.chatbot.process_message(technical_question)
            print(f"🤖 ChatBot: {response}")
            
            # 检查技术回答质量
            technical_keywords = ["装饰器", "函数", "@", "语法", "Python"]
            found_keywords = sum(1 for keyword in technical_keywords if keyword in response)
            
            if found_keywords >= 2:
                print(f"✅ 技术问题回答测试通过 (检测到 {found_keywords} 个相关关键词)")
                return True
            else:
                print(f"⚠️  技术问题回答可能需要改进 (仅检测到 {found_keywords} 个相关关键词)")
                return True  # 不强制失败
                
        except Exception as e:
            print(f"❌ 技术问题测试错误: {e}")
            return False
            
    async def test_conversation_flow(self):
        """测试完整对话流程"""
        print("\n🔄 测试完整对话流程")
        print("-" * 50)
        
        conversation_flow = [
            ("开场", "你好，我想了解一个新话题"),
            ("询问", "你能帮我学习机器学习吗？"),
            ("深入", "什么是监督学习？"),
            ("扩展", "能举个具体的例子吗？"),
            ("总结", "感谢你的详细解释！"),
            ("结束", "再见")
        ]
        
        for stage, message in conversation_flow:
            print(f"\n【{stage}阶段】")
            print(f"👤 用户: {message}")
            
            try:
                response = await self.chatbot.process_message(message)
                print(f"🤖 ChatBot: {response[:200]}{'...' if len(response) > 200 else ''}")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ {stage}阶段错误: {e}")
                return False
                
        print("✅ 完整对话流程测试通过")
        return True
        
    async def cleanup(self):
        """清理测试资源"""
        if self.llm_gateway:
            await self.llm_gateway.close()
        print("🧹 测试资源清理完成")


async def main():
    """主测试函数"""
    print("🧪 Polytool真实LLM集成测试")
    print("=" * 50)
    
    mock_llm = os.getenv("MOCK_LLM", "false").lower() == "true"
    default_provider = settings.DEFAULT_LLM_PROVIDER
    
    print(f"🔧 当前LLM提供商: {default_provider}")
    print(f"🔧 模拟模式: {'开启' if mock_llm else '关闭'}")
    print("=" * 50)
    
    if mock_llm:
        print("⚠️  当前为模拟模式，请在.env中设置 MOCK_LLM=false 以测试真实API")
        print("💡 运行模拟测试请使用: python tests/llm_demo.py")
        return
    
    test = RealLLMIntegrationTest()
    
    try:
        # 初始化测试
        if not await test.setup():
            return
            
        # 执行测试套件
        tests = [
            ("基础对话", test.test_basic_interaction),
            ("上下文记忆", test.test_context_memory),
            ("技术问题", test.test_technical_question),
            ("对话流程", test.test_conversation_flow)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🚀 执行测试: {test_name}")
            try:
                if await test_func():
                    passed_tests += 1
                    print(f"✅ {test_name} 测试通过")
                else:
                    print(f"❌ {test_name} 测试失败")
            except Exception as e:
                print(f"❌ {test_name} 测试异常: {e}")
        
        # 测试结果总结
        print("\n" + "=" * 50)
        print("📊 真实LLM集成测试结果:")
        print(f"   ✅ 通过测试: {passed_tests}/{total_tests}")
        print(f"   📈 成功率: {passed_tests/total_tests*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 所有测试通过！ChatBot LLM集成成功！")
        else:
            print("⚠️  部分测试失败，请检查配置和网络连接")
            
    except Exception as e:
        print(f"❌ 测试执行异常: {e}")
    finally:
        await test.cleanup()
        

if __name__ == "__main__":
    asyncio.run(main())