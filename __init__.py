#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polytool - 通用智能体框架
========================

一个基于低代码开发、插件化架构和增强RAG技术的通用智能体框架
"""

__version__ = "0.1.0"
__author__ = "Polytool Team"
__email__ = "team@polytool.ai"
__description__ = "通用智能体框架"

from config import settings

# 导出主要组件
from orchestration import LLMGateway, MemoryManager, ToolGateway
from api import APIServer

__all__ = [
    "settings",
    "LLMGateway",
    "MemoryManager",
    "ToolGateway", 
    "APIServer",
]