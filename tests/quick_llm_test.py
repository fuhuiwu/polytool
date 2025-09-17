#!/usr/bin/env python3
"""
快速测试模拟LLM集成
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from orchestration.llm_gateway import create_llm_gateway, LLMMessage


async def test_mock_llm():
    print("🧪 测试模拟LLM集成")
    print("=" * 40)
    
    # 创建LLM网关
    llm_gateway = create_llm_gateway(settings)
    await llm_gateway.initialize()
    
    # 检查环境变量
    mock_llm = os.getenv("MOCK_LLM", "false").lower() == "true"
    print(f"🔧 MOCK_LLM: {mock_llm}")
    print(f"🔧 提供商数量: {len(llm_gateway.providers)}")
    print(f"🔧 可用提供商: {list(llm_gateway.providers.keys())}")
    
    if not llm_gateway.providers:
        print("❌ 错误: 没有注册任何提供商")
        return
    
    # 测试对话
    test_messages = [
        LLMMessage(role="user", content="你好"),
        LLMMessage(role="user", content="你是谁？"),
        LLMMessage(role="user", content="再见")
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n【测试 {i}】")
        print(f"👤 用户: {msg.content}")
        
        try:
            response = await llm_gateway.generate([msg])
            print(f"🤖 AI: {response.content}")
            print(f"📊 模型: {response.model} (提供商: {response.provider})")
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    await llm_gateway.shutdown()
    print("\n✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(test_mock_llm())