#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatBot对话管理模块
==================

包含聊天消息和对话管理的核心功能
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional


class ChatMessage:
    """
    聊天消息类
    """
    
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        """
        初始化聊天消息
        
        Args:
            role: 消息角色 ('user' 或 'assistant')
            content: 消息内容
            timestamp: 时间戳
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """从字典创建消息"""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class ConversationManager:
    """
    对话管理器
    """
    
    def __init__(self, max_history: int = 100):
        """
        初始化对话管理器
        
        Args:
            max_history: 最大历史消息数
        """
        self.max_history = max_history
        self.conversations: Dict[str, List[ChatMessage]] = {}
    
    def add_message(self, session_id: str, message: ChatMessage):
        """
        添加消息到会话
        
        Args:
            session_id: 会话ID
            message: 聊天消息
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append(message)
        
        # 保持历史记录在限制范围内
        if len(self.conversations[session_id]) > self.max_history:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history:]
    
    def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        获取会话历史
        
        Args:
            session_id: 会话ID
            limit: 限制返回的消息数量
            
        Returns:
            List[ChatMessage]: 消息历史
        """
        if session_id not in self.conversations:
            return []
        
        messages = self.conversations[session_id]
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def clear_conversation(self, session_id: str):
        """
        清空会话历史
        
        Args:
            session_id: 会话ID
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
    
    def get_active_sessions(self) -> List[str]:
        """
        获取活跃会话列表
        
        Returns:
            List[str]: 会话ID列表
        """
        return list(self.conversations.keys())