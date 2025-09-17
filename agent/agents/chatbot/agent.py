#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatBot智能体实现
=================

ChatBot智能体的核心实现
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from agent.base import Agent
from .conversation import ConversationManager, ChatMessage


class ChatBotAgent(Agent):
    """
    聊天机器人智能体
    
    支持多会话对话，具备上下文记忆和个性化响应能力
    """
    
    def __init__(self, agent_id: str = "chatbot", name: str = "ChatBot", description: str = "智能聊天助手"):
        """
        初始化ChatBot智能体
        
        Args:
            agent_id: 智能体ID
            name: 智能体名称
            description: 智能体描述
        """
        super().__init__(agent_id, name, description)
        
        # 对话管理器
        self.conversation_manager = ConversationManager()
        
        # ChatBot配置
        self.system_prompt = """你是Polytool框架的智能助手，名叫ChatBot。你的特点：
1. 友好、专业、有帮助
2. 能够记住对话上下文
3. 擅长回答技术问题和日常交流
4. 会根据用户需求提供合适的建议
5. 保持简洁明了的回复风格

请用中文与用户交流。"""
        
        # 默认回复模板
        self.default_responses = [
            "我理解您的问题，让我想想怎么帮助您。",
            "这是一个有趣的话题，您能详细说明一下吗？", 
            "我正在学习中，可能需要更多信息才能给出更好的回答。",
            "感谢您的耐心，我会尽力为您提供帮助。"
        ]
    
    async def _initialize_agent(self):
        """
        初始化ChatBot智能体
        """
        # 这里可以加载模型、初始化向量数据库等
        self.logger.info("ChatBot智能体初始化完成")
    
    async def _cleanup_agent(self):
        """
        清理ChatBot资源
        """
        # 清理对话历史（可选）
        self.conversation_manager.conversations.clear()
        self.logger.info("ChatBot智能体资源已清理")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理用户输入并生成回复
        
        Args:
            input_data: 包含用户消息的输入数据
            
        Returns:
            Dict[str, Any]: 包含回复的响应数据
        """
        try:
            # 提取输入参数
            user_message = input_data.get("message", "")
            session_id = input_data.get("session_id", "default")
            context = input_data.get("context", {})
            
            if not user_message.strip():
                return {
                    "status": "error",
                    "message": "用户消息不能为空",
                    "session_id": session_id
                }
            
            # 添加用户消息到对话历史
            user_chat_message = ChatMessage(role="user", content=user_message)
            self.conversation_manager.add_message(session_id, user_chat_message)
            
            # 生成回复
            response = await self._generate_response(user_message, session_id, context)
            
            # 添加助手回复到对话历史
            assistant_message = ChatMessage(role="assistant", content=response)
            self.conversation_manager.add_message(session_id, assistant_message)
            
            return {
                "status": "success",
                "response": response,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "conversation_length": len(self.conversation_manager.get_conversation_history(session_id))
            }
            
        except Exception as e:
            self.logger.error(f"处理用户输入时出错: {e}")
            return {
                "status": "error",
                "message": f"处理请求时出现错误: {str(e)}",
                "session_id": input_data.get("session_id", "default")
            }
    
    async def _generate_response(self, user_message: str, session_id: str, context: Dict[str, Any]) -> str:
        """
        生成回复消息
        
        Args:
            user_message: 用户消息
            session_id: 会话ID
            context: 上下文信息
            
        Returns:
            str: 生成的回复
        """
        # 获取对话历史
        history = self.conversation_manager.get_conversation_history(session_id, limit=10)
        
        # 如果有LLM网关，使用LLM生成回复
        if self.llm_gateway:
            try:
                # 使用LLM网关的简化接口生成回复
                response = await self.llm_gateway.generate_simple(
                    system_prompt=self.system_prompt,
                    user_message=self._build_user_message_with_context(history, user_message)
                )
                
                if response and response.strip():
                    return response.strip()
                else:
                    self.logger.warning("LLM返回空响应，使用默认回复")
                    return await self._generate_smart_default_response(user_message, history)
                
            except Exception as e:
                self.logger.warning(f"LLM生成回复失败，使用默认回复: {e}")
                return await self._generate_smart_default_response(user_message, history)
        else:
            # 使用智能默认回复
            return await self._generate_smart_default_response(user_message, history)
    
    def _build_user_message_with_context(self, history: List[ChatMessage], current_message: str) -> str:
        """
        构建带有上下文的用户消息
        
        Args:
            history: 对话历史
            current_message: 当前用户消息
            
        Returns:
            str: 带有上下文的用户消息
        """
        if not history:
            return current_message
        
        # 构建上下文
        context_parts = []
        
        # 只取最近的几轮对话作为上下文
        recent_history = history[-6:]  # 最多3轮对话（6条消息）
        
        if recent_history:
            context_parts.append("对话上下文：")
            for msg in recent_history:
                role_name = "用户" if msg.role == "user" else "助手"
                context_parts.append(f"{role_name}: {msg.content}")
            context_parts.append("")  # 空行分隔
        
        context_parts.append(f"当前用户消息: {current_message}")
        
        return "\n".join(context_parts)
    
    async def _generate_smart_default_response(self, user_message: str, history: List[ChatMessage]) -> str:
        """
        生成智能默认回复
        
        Args:
            user_message: 用户消息
            history: 对话历史
            
        Returns:
            str: 智能默认回复
        """
        message_lower = user_message.lower().strip()
        
        # 问候语检测
        if any(greeting in message_lower for greeting in ["你好", "您好", "hello", "hi", "嗨"]):
            if len(history) <= 2:  # 首次问候
                return f"您好！我是{self.name}，Polytool框架的智能助手。我可以帮助您解答问题、进行对话。有什么我可以帮助您的吗？"
            else:
                return "您好！有什么新的问题我可以帮助您解决吗？"
        
        # 告别语检测
        elif any(farewell in message_lower for farewell in ["再见", "拜拜", "goodbye", "bye"]):
            return "再见！很高兴为您服务，期待下次交流！"
        
        # 感谢语检测
        elif any(thanks in message_lower for thanks in ["谢谢", "感谢", "thank"]):
            return "不客气！很高兴能帮助您。还有其他问题吗？"
        
        # 自我介绍请求
        elif any(intro in message_lower for intro in ["你是谁", "介绍一下", "自我介绍"]):
            return f"我是{self.name}，基于Polytool智能体框架开发的聊天助手。我可以：\n1. 与您进行自然对话\n2. 记住我们的对话历史\n3. 回答各种问题\n4. 提供技术支持\n\n很高兴认识您！"
        
        # 功能询问
        elif any(func in message_lower for func in ["能做什么", "功能", "帮助", "help"]):
            return "我目前可以为您提供以下服务：\n• 💬 自然对话交流\n• 🧠 记忆对话上下文\n• ❓ 回答问题和解疑\n• 💡 提供建议和帮助\n• 🔧 技术相关咨询\n\n请随时告诉我您需要什么帮助！"
        
        # 对话历史询问
        elif "历史" in message_lower or "记录" in message_lower:
            history_count = len(history)
            return f"我们目前已经进行了 {history_count // 2} 轮对话。我会记住我们的对话内容，以便更好地为您服务。"
        
        # 技术相关问题
        elif any(tech in message_lower for tech in ["polytool", "框架", "代码", "编程", "开发"]):
            return "关于Polytool框架或技术问题，我很乐意与您探讨！Polytool是一个通用智能体框架，采用三层架构设计。您想了解哪个方面的内容呢？"
        
        # 默认智能回复
        else:
            import random
            # 根据消息长度和内容选择合适的默认回复
            if len(user_message) > 100:
                return "您提到的内容很详细，我正在理解中。虽然我的能力还在不断学习完善，但我会尽力为您提供有用的回复。能告诉我您最关心的是哪个方面吗？"
            elif "?" in user_message or "？" in user_message:
                return "这是一个很好的问题！虽然我目前的知识库还在建设中，但我可以尝试从不同角度来思考这个问题。您能提供更多背景信息吗？"
            else:
                responses = [
                    "我理解您的意思。您能详细说明一下吗？",
                    "这听起来很有趣！能告诉我更多相关信息吗？",
                    "我正在思考您的话，能否给我一些更多的上下文呢？",
                    "感谢您的分享。我想更好地理解您的需求，可以详细解释一下吗？"
                ]
                return random.choice(responses)
    
    def get_conversation_info(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            Dict[str, Any]: 会话信息
        """
        history = self.conversation_manager.get_conversation_history(session_id)
        return {
            "session_id": session_id,
            "message_count": len(history),
            "last_activity": history[-1].timestamp.isoformat() if history else None,
            "conversation_summary": {
                "user_messages": len([msg for msg in history if msg.role == "user"]),
                "assistant_messages": len([msg for msg in history if msg.role == "assistant"])
            }
        }
    
    def export_conversation(self, session_id: str) -> List[Dict[str, Any]]:
        """
        导出会话历史
        
        Args:
            session_id: 会话ID
            
        Returns:
            List[Dict[str, Any]]: 会话历史数据
        """
        history = self.conversation_manager.get_conversation_history(session_id)
        return [msg.to_dict() for msg in history]