#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatBot智能体
==============

智能聊天助手，支持多会话对话
"""

from .agent import ChatBotAgent
from .conversation import ChatMessage, ConversationManager

# 导出主要类
__all__ = ["ChatBotAgent", "ChatMessage", "ConversationManager"]