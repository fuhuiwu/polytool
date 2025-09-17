#!/usr/bin/env python3
"""
Kimi K2 功能演示
================

展示Kimi集成到Polytool框架的各种功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径  
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from orchestration.llm_gateway import create_llm_gateway, LLMMessage


async def demonstrate_kimi_features():
    """演示Kimi的各项功能"""
    print("🚀 Kimi K2 LLM 功能演示")
    print("=" * 60)
    print("🌙 集成月之暗面 Kimi 大语言模型")
    print("📋 支持的模型:")
    print("   • moonshot-v1-8k (8K上下文)")
    print("   • moonshot-v1-32k (32K上下文)") 
    print("   • moonshot-v1-128k (128K上下文)")
    print("=" * 60)
    
    # 创建LLM网关
    llm_gateway = create_llm_gateway(settings)
    await llm_gateway.initialize()
    
    # 检查Kimi提供商状态
    mock_mode = os.getenv("MOCK_LLM", "false").lower() == "true"
    
    if mock_mode:
        print("🔧 当前运行在模拟模式")
        print("💡 要使用真实Kimi API，请:")
        print("   1. 设置 MOCK_LLM=false")
        print("   2. 配置有效的 KIMI_API_KEY")
        print("   3. 重新运行演示")
    else:
        if "kimi" in llm_gateway.providers:
            print("✅ Kimi提供商已激活，使用真实API")
        else:
            print("⚠️  Kimi提供商未配置，请检查KIMI_API_KEY")
    
    print("\n" + "-" * 60)
    
    # 功能演示场景
    demo_scenarios = [
        {
            "title": "🤖 基础对话能力", 
            "messages": [
                LLMMessage(role="system", content="你是Kimi，月之暗面开发的AI助手"),
                LLMMessage(role="user", content="请介绍一下你自己，包括你的能力和特色")
            ]
        },
        {
            "title": "💻 代码生成能力",
            "messages": [
                LLMMessage(role="user", content="请用Python写一个二分查找算法，要求包含详细注释")
            ]
        },
        {
            "title": "📚 文本分析能力", 
            "messages": [
                LLMMessage(role="user", content="""
请分析以下文本的主要观点：

人工智能技术的发展正在重塑各个行业。从医疗诊断到金融风险控制，
从智能制造到教育个性化，AI的应用场景越来越广泛。然而，技术进步
也带来了数据隐私、算法偏见、就业结构变化等挑战。我们需要在推动
技术创新的同时，建立相应的伦理框架和监管机制。
                """)
            ]
        },
        {
            "title": "🔍 逻辑推理能力",
            "messages": [
                LLMMessage(role="user", content="""
逻辑题：有A、B、C三个人，其中：
- A说：我不是罪犯
- B说：C是罪犯  
- C说：B在撒谎

已知只有一个人是罪犯，且罪犯会说谎，无辜的人说真话。
请分析谁是罪犯？
                """)
            ]
        }
    ]
    
    # 执行演示
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n📋 场景 {i}: {scenario['title']}")
        print("-" * 40)
        
        # 显示用户输入
        user_msg = [msg for msg in scenario['messages'] if msg.role == 'user'][-1]
        print(f"👤 用户输入:")
        print(f"   {user_msg.content.strip()}")
        
        try:
            # 调用Kimi LLM
            response = await llm_gateway.generate(
                scenario['messages'], 
                provider="kimi" if "kimi" in llm_gateway.providers else None
            )
            
            print(f"\n🤖 Kimi回复:")
            # 格式化长文本输出
            content = response.content
            if len(content) > 500:
                # 截断长回复并显示前部分
                lines = content.split('\n')
                displayed_lines = []
                char_count = 0
                
                for line in lines:
                    if char_count + len(line) > 400:
                        if char_count > 200:  # 确保有足够内容显示
                            displayed_lines.append("   ...")
                            displayed_lines.append(f"   [回复过长，已截断。完整长度: {len(content)} 字符]")
                            break
                    displayed_lines.append(f"   {line}")
                    char_count += len(line)
                
                print('\n'.join(displayed_lines))
            else:
                # 短回复直接显示
                for line in content.split('\n'):
                    print(f"   {line}")
            
            print(f"\n📊 响应信息:")
            print(f"   模型: {response.model}")
            print(f"   提供商: {response.provider}")
            if response.usage:
                print(f"   Token使用: {response.usage}")
            
        except Exception as e:
            print(f"❌ 调用失败: {e}")
        
        # 添加分隔符
        if i < len(demo_scenarios):
            print("\n" + "·" * 40)
            await asyncio.sleep(0.5)  # 避免过快调用
    
    print("\n" + "=" * 60)
    
    # 性能特性说明
    print("🌟 Kimi 特色功能:")
    print("✨ 超长上下文: 支持最高128K token的上下文长度")
    print("🧠 强大推理: 擅长逻辑分析和复杂问题解决")
    print("💻 代码能力: 支持多种编程语言的生成和解析")
    print("📖 文档理解: 能够处理和分析长篇文档")
    print("🌐 中文优化: 针对中文场景进行了特别优化")
    
    print("\n🔧 集成配置:")
    print("📁 配置文件: .env 或 .env.example")
    print("🔑 API密钥: KIMI_API_KEY (需要从月之暗面官网获取)")
    print("🌐 API地址: https://api.moonshot.cn")
    print("⚙️  模型选择: moonshot-v1-8k / 32k / 128k")
    
    # 清理资源
    await llm_gateway.shutdown()
    
    print("\n" + "=" * 60)
    print("🎉 Kimi K2 功能演示完成！")


if __name__ == "__main__":
    asyncio.run(demonstrate_kimi_features())