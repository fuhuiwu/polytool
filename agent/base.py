#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体基类
==========

定义Polytool框架中所有智能体的基础接口和行为
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from utils.logger import get_logger


class Agent(ABC):
    """
    智能体基类
    
    所有智能体都应该继承此类并实现其抽象方法
    """
    
    def __init__(self, agent_id: str, name: str, description: str = ""):
        """
        初始化智能体
        
        Args:
            agent_id: 智能体唯一标识符
            name: 智能体名称
            description: 智能体描述
        """
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.logger = get_logger(f"polytool.agent.{agent_id}")
        self.is_initialized = False
        self.context = {}
        
        # 注入的依赖组件
        self.llm_gateway = None
        self.memory_manager = None
        self.tool_gateway = None
    
    def inject_dependencies(self, llm_gateway=None, memory_manager=None, tool_gateway=None):
        """
        注入依赖组件
        
        Args:
            llm_gateway: LLM网关实例
            memory_manager: 记忆管理器实例
            tool_gateway: 工具网关实例
        """
        self.llm_gateway = llm_gateway
        self.memory_manager = memory_manager
        self.tool_gateway = tool_gateway
    
    async def initialize(self):
        """
        异步初始化智能体
        """
        try:
            self.logger.info(f"正在初始化智能体: {self.name} ({self.agent_id})")
            await self._initialize_agent()
            self.is_initialized = True
            self.logger.info(f"智能体 {self.name} 初始化完成")
        except Exception as e:
            self.logger.error(f"智能体 {self.name} 初始化失败: {e}")
            raise
    
    async def shutdown(self):
        """
        关闭智能体，清理资源
        """
        try:
            self.logger.info(f"正在关闭智能体: {self.name}")
            await self._cleanup_agent()
            self.is_initialized = False
            self.logger.info(f"智能体 {self.name} 已关闭")
        except Exception as e:
            self.logger.error(f"智能体 {self.name} 关闭时出错: {e}")
            raise
    
    @abstractmethod
    async def _initialize_agent(self):
        """
        子类实现的具体初始化逻辑
        """
        pass
    
    @abstractmethod
    async def _cleanup_agent(self):
        """
        子类实现的具体清理逻辑
        """
        pass
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理输入数据并生成响应
        
        Args:
            input_data: 输入数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        pass
    
    def set_context(self, key: str, value: Any):
        """
        设置上下文信息
        
        Args:
            key: 上下文键
            value: 上下文值
        """
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """
        获取上下文信息
        
        Args:
            key: 上下文键
            default: 默认值
            
        Returns:
            Any: 上下文值
        """
        return self.context.get(key, default)
    
    def clear_context(self):
        """
        清空上下文信息
        """
        self.context.clear()
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取智能体信息
        
        Returns:
            Dict[str, Any]: 智能体信息
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "is_initialized": self.is_initialized,
            "context_keys": list(self.context.keys())
        }
    
    def __repr__(self) -> str:
        return f"Agent(id='{self.agent_id}', name='{self.name}')"