#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI HTTP服务器实现
=====================

提供真正的HTTP API服务
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from utils.logger import get_logger
from agent import AgentManager, ChatBotAgent
from config import settings


# 请求/响应模型
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    context: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    status: str
    response: str
    session_id: str
    timestamp: str
    conversation_length: int = 0


class AgentInfo(BaseModel):
    agent_id: str
    name: str
    description: str
    status: str
    created_at: str


class HTTPServer:
    """HTTP服务器类"""
    
    def __init__(self, llm_gateway=None, memory_manager=None, tool_gateway=None):
        """初始化HTTP服务器"""
        self.logger = get_logger("polytool.http_server")
        self.llm_gateway = llm_gateway
        self.memory_manager = memory_manager
        self.tool_gateway = tool_gateway
        
        # FastAPI应用
        self.app = FastAPI(
            title="Polytool API",
            description="通用智能体框架API服务",
            version="0.1.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # CORS配置
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 智能体管理器
        self.agent_manager = AgentManager()
        self.default_chatbot_id = "default_chatbot"
        
        # 设置路由
        self._setup_routes()
        
    async def initialize(self):
        """初始化HTTP服务器"""
        self.logger.info("正在初始化HTTP服务器...")
        
        # 注入依赖到智能体管理器
        self.agent_manager.inject_dependencies(
            self.llm_gateway, 
            self.memory_manager, 
            self.tool_gateway
        )
        
        # 注册ChatBot智能体类型
        self.agent_manager.register_agent(ChatBotAgent, "chatbot")
        
        # 创建默认的ChatBot实例
        await self._create_default_chatbot()
        
        self.logger.info("HTTP服务器初始化完成")
        
    async def _create_default_chatbot(self):
        """创建默认的ChatBot实例"""
        try:
            await self.agent_manager.create_agent(
                agent_type="chatbot",
                agent_id=self.default_chatbot_id,
                name="默认ChatBot",
                description="Polytool框架的默认聊天助手"
            )
            self.logger.info("默认ChatBot实例创建成功")
        except Exception as e:
            self.logger.error(f"创建默认ChatBot实例失败: {e}")
            raise
    
    def _setup_routes(self):
        """设置API路由"""
        
        @self.app.get("/")
        async def root():
            return {
                "message": "Welcome to Polytool API",
                "version": "0.1.0",
                "docs": "/docs",
                "status": "running"
            }
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "agents_count": len(self.agent_manager.agents),
                "services": {
                    "llm_gateway": self.llm_gateway is not None,
                    "memory_manager": self.memory_manager is not None,
                    "tool_gateway": self.tool_gateway is not None
                }
            }
        
        @self.app.post("/chat", response_model=ChatResponse)
        async def chat_with_bot(request: ChatRequest):
            """与ChatBot对话"""
            try:
                # 获取ChatBot实例
                chatbot = self.agent_manager.get_agent(self.default_chatbot_id)
                if not chatbot:
                    raise HTTPException(status_code=500, detail="ChatBot未初始化")
                
                # 处理对话
                result = await chatbot.process({
                    "message": request.message,
                    "session_id": request.session_id,
                    "context": request.context
                })
                
                if result["status"] == "success":
                    from datetime import datetime
                    return ChatResponse(
                        status="success",
                        response=result["response"],
                        session_id=request.session_id,
                        timestamp=datetime.now().isoformat(),
                        conversation_length=result.get("conversation_length", 0)
                    )
                else:
                    raise HTTPException(
                        status_code=500, 
                        detail=result.get("message", "ChatBot处理失败")
                    )
                    
            except Exception as e:
                self.logger.error(f"对话处理异常: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/agents", response_model=List[AgentInfo])
        async def get_agents():
            """获取所有智能体列表"""
            agents_info = []
            for agent_id, agent in self.agent_manager.agents.items():
                agents_info.append(AgentInfo(
                    agent_id=agent_id,
                    name=agent.name,
                    description=agent.description,
                    status="active" if agent.is_initialized else "inactive",
                    created_at=agent.created_at.isoformat() if hasattr(agent, 'created_at') else ""
                ))
            return agents_info
        
        @self.app.get("/agents/{agent_id}", response_model=AgentInfo)
        async def get_agent(agent_id: str):
            """获取指定智能体信息"""
            agent = self.agent_manager.get_agent(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail="智能体不存在")
            
            return AgentInfo(
                agent_id=agent_id,
                name=agent.name,
                description=agent.description,
                status="active" if agent.is_initialized else "inactive",
                created_at=agent.created_at.isoformat() if hasattr(agent, 'created_at') else ""
            )
        
        @self.app.delete("/agents/{agent_id}/sessions/{session_id}")
        async def clear_conversation(agent_id: str, session_id: str):
            """清空指定智能体的对话历史"""
            agent = self.agent_manager.get_agent(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail="智能体不存在")
            
            if hasattr(agent, 'conversation_manager'):
                agent.conversation_manager.clear_conversation(session_id)
                return {"status": "success", "message": "对话历史已清空"}
            else:
                raise HTTPException(status_code=400, detail="该智能体不支持对话管理")
    
    async def run(self, host: str = None, port: int = None):
        """运行HTTP服务器"""
        host = host or settings.SERVER_HOST
        port = port or settings.SERVER_PORT
        
        self.logger.info(f"🚀 启动HTTP服务器...")
        self.logger.info(f"📍 监听地址: http://{host}:{port}")
        self.logger.info(f"📚 API文档: http://{host}:{port}/docs")
        self.logger.info(f"📖 ReDoc文档: http://{host}:{port}/redoc")
        
        # 启动uvicorn服务器
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        
        try:
            await server.serve()
        except Exception as e:
            self.logger.error(f"HTTP服务器启动失败: {e}")
            raise
    
    async def shutdown(self):
        """关闭HTTP服务器"""
        self.logger.info("正在关闭HTTP服务器...")