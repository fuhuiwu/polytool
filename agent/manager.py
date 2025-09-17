#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体管理器
============

负责智能体的注册、实例化和生命周期管理
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Type
from agent.base import Agent
from utils.logger import get_logger


class AgentManager:
    """
    智能体管理器
    
    负责管理所有智能体的生命周期
    """
    
    def __init__(self):
        """初始化智能体管理器"""
        self.logger = get_logger("polytool.agent_manager")
        
        # 注册的智能体类
        self.registered_agents: Dict[str, Type[Agent]] = {}
        
        # 活跃的智能体实例
        self.active_agents: Dict[str, Agent] = {}
        
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
        
        # 同时注入到所有已创建的智能体实例
        for agent in self.active_agents.values():
            agent.inject_dependencies(llm_gateway, memory_manager, tool_gateway)
    
    def register_agent(self, agent_class: Type[Agent], agent_type: str = None):
        """
        注册智能体类
        
        Args:
            agent_class: 智能体类
            agent_type: 智能体类型标识符（可选，默认使用类名）
        """
        if agent_type is None:
            agent_type = agent_class.__name__.lower()
        
        self.registered_agents[agent_type] = agent_class
        self.logger.info(f"已注册智能体类: {agent_type} ({agent_class.__name__})")
    
    async def create_agent(
        self, 
        agent_type: str, 
        agent_id: str, 
        name: str = None, 
        description: str = "", 
        config: Dict[str, Any] = None
    ) -> Agent:
        """
        创建智能体实例
        
        Args:
            agent_type: 智能体类型
            agent_id: 智能体唯一标识符
            name: 智能体名称
            description: 智能体描述
            config: 智能体配置
            
        Returns:
            Agent: 创建的智能体实例
        """
        if agent_type not in self.registered_agents:
            raise ValueError(f"未注册的智能体类型: {agent_type}")
        
        if agent_id in self.active_agents:
            raise ValueError(f"智能体ID已存在: {agent_id}")
        
        # 获取智能体类
        agent_class = self.registered_agents[agent_type]
        
        # 创建智能体实例
        if name is None:
            name = f"{agent_type.title()}_{agent_id}"
        
        try:
            # 根据智能体类的构造函数参数创建实例
            if config:
                agent = agent_class(agent_id=agent_id, name=name, description=description, **config)
            else:
                agent = agent_class(agent_id=agent_id, name=name, description=description)
            
            # 注入依赖
            agent.inject_dependencies(self.llm_gateway, self.memory_manager, self.tool_gateway)
            
            # 初始化智能体
            await agent.initialize()
            
            # 保存到活跃智能体列表
            self.active_agents[agent_id] = agent
            
            self.logger.info(f"已创建智能体: {agent_id} ({agent_type})")
            return agent
            
        except Exception as e:
            self.logger.error(f"创建智能体失败: {agent_id} - {e}")
            raise
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        获取智能体实例
        
        Args:
            agent_id: 智能体ID
            
        Returns:
            Agent: 智能体实例，如果不存在则返回None
        """
        return self.active_agents.get(agent_id)
    
    async def remove_agent(self, agent_id: str) -> bool:
        """
        移除智能体实例
        
        Args:
            agent_id: 智能体ID
            
        Returns:
            bool: 是否成功移除
        """
        if agent_id not in self.active_agents:
            return False
        
        try:
            agent = self.active_agents[agent_id]
            
            # 关闭智能体
            await agent.shutdown()
            
            # 从活跃列表中移除
            del self.active_agents[agent_id]
            
            self.logger.info(f"已移除智能体: {agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"移除智能体失败: {agent_id} - {e}")
            return False
    
    async def process_request(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理智能体请求
        
        Args:
            agent_id: 智能体ID
            input_data: 输入数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        agent = await self.get_agent(agent_id)
        if agent is None:
            return {
                "status": "error",
                "message": f"智能体不存在: {agent_id}",
                "agent_id": agent_id
            }
        
        try:
            result = await agent.process(input_data)
            result["agent_id"] = agent_id
            return result
        except Exception as e:
            self.logger.error(f"智能体处理请求失败: {agent_id} - {e}")
            return {
                "status": "error",
                "message": f"处理请求时出现错误: {str(e)}",
                "agent_id": agent_id
            }
    
    def get_registered_agents(self) -> List[str]:
        """
        获取已注册的智能体类型列表
        
        Returns:
            List[str]: 智能体类型列表
        """
        return list(self.registered_agents.keys())
    
    def get_active_agents(self) -> List[Dict[str, Any]]:
        """
        获取活跃智能体信息列表
        
        Returns:
            List[Dict[str, Any]]: 智能体信息列表
        """
        return [agent.get_info() for agent in self.active_agents.values()]
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定智能体信息
        
        Args:
            agent_id: 智能体ID
            
        Returns:
            Dict[str, Any]: 智能体信息，如果不存在则返回None
        """
        agent = self.active_agents.get(agent_id)
        return agent.get_info() if agent else None
    
    async def shutdown_all_agents(self):
        """
        关闭所有智能体
        """
        self.logger.info("正在关闭所有智能体...")
        
        # 并行关闭所有智能体
        shutdown_tasks = []
        for agent_id, agent in self.active_agents.items():
            task = asyncio.create_task(self._safe_shutdown_agent(agent_id, agent))
            shutdown_tasks.append(task)
        
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        # 清空活跃智能体列表
        self.active_agents.clear()
        
        self.logger.info("所有智能体已关闭")
    
    async def _safe_shutdown_agent(self, agent_id: str, agent: Agent):
        """
        安全关闭单个智能体
        
        Args:
            agent_id: 智能体ID
            agent: 智能体实例
        """
        try:
            await agent.shutdown()
            self.logger.info(f"智能体 {agent_id} 已安全关闭")
        except Exception as e:
            self.logger.error(f"关闭智能体 {agent_id} 时出错: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取管理器状态
        
        Returns:
            Dict[str, Any]: 管理器状态信息
        """
        return {
            "registered_agent_types": len(self.registered_agents),
            "active_agents": len(self.active_agents),
            "registered_types": list(self.registered_agents.keys()),
            "active_agent_ids": list(self.active_agents.keys())
        }