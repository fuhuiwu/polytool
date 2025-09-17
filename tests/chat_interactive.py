#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatBot交互测试脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.server import APIServer


async def test_chat():
    """测试ChatBot对话功能"""
    print("🤖 ChatBot交互测试")
    print("=" * 30)
    
    server = APIServer()
    
    try:
        await server.initialize()
        print(f"✅ 服务器已初始化")
        
        # 测试对话
        test_messages = [
            "你好！",
            "你是谁？",
            "你能做什么？",
            "我想了解Polytool框架",
            "谢谢你的帮助",
            "再见"
        ]
        
        session_id = "test_session"
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n👤 用户 [{i}]: {message}")
            
            response = await server.chat_with_bot(
                message=message,
                session_id=session_id
            )
            
            if response.get("status") == "success":
                bot_reply = response.get("response", "")
                conversation_length = response.get("conversation_length", 0)
                print(f"🤖 ChatBot [{i}]: {bot_reply}")
                print(f"   💬 对话长度: {conversation_length}")
            else:
                error_msg = response.get("message", "未知错误")
                print(f"❌ 错误: {error_msg}")
        
        print(f"\n✅ 对话测试完成！")
        
    finally:
        await server.shutdown()


def main():
    """主函数"""
    try:
        asyncio.run(test_chat())
    except KeyboardInterrupt:
        print("\n⏹️ 测试中断")
    except Exception as e:
        print(f"❌ 测试出错: {e}")


if __name__ == "__main__":
    main()