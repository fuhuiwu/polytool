#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM网关模块
===========

负责统一管理各种大语言模型的接入和调用
"""

import asyncio
import logging
import json
import aiohttp
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from utils.logger import get_logger


@dataclass
class LLMMessage:
    """LLM消息数据结构"""
    role: str  # system, user, assistant
    content: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {"role": self.role, "content": self.content}


@dataclass
class LLMResponse:
    """LLM响应数据结构"""
    content: str
    model: str
    provider: str
    usage: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    

class LLMProvider:
    """LLM提供商基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(f"polytool.llm.{self.get_provider_name()}")
    
    def get_provider_name(self) -> str:
        """获取提供商名称"""
        raise NotImplementedError
    
    async def generate(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """生成回复"""
        raise NotImplementedError
    
    async def validate_config(self) -> bool:
        """验证配置"""
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI提供商"""
    
    def get_provider_name(self) -> str:
        return "openai"
    
    async def validate_config(self) -> bool:
        """验证OpenAI配置"""
        required_keys = ["api_key", "api_base", "model"]
        return all(key in self.config for key in required_keys)
    
    async def generate(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """调用OpenAI API生成回复"""
        if not await self.validate_config():
            raise ValueError("OpenAI配置不完整")
        
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.get("model", "gpt-3.5-turbo"),
            "messages": [msg.to_dict() for msg in messages],
            "max_tokens": self.config.get("max_tokens", 2000),
            "temperature": self.config.get("temperature", 0.7),
            **kwargs
        }
        
        url = f"{self.config['api_base']}/chat/completions"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url, 
                    headers=headers, 
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.get("timeout", 30))
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return LLMResponse(
                            content=data["choices"][0]["message"]["content"],
                            model=data["model"],
                            provider="openai",
                            usage=data.get("usage", {}),
                            metadata={"response_id": data.get("id")}
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(f"OpenAI API错误 {response.status}: {error_text}")
                        
            except asyncio.TimeoutError:
                raise Exception("OpenAI API请求超时")
            except Exception as e:
                self.logger.error(f"OpenAI API调用失败: {e}")
                raise


class ClaudeProvider(LLMProvider):
    """Claude提供商"""
    
    def get_provider_name(self) -> str:
        return "claude"
    
    async def validate_config(self) -> bool:
        """验证Claude配置"""
        required_keys = ["api_key", "api_base", "model"]
        return all(key in self.config for key in required_keys)
    
    async def generate(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """调用Claude API生成回复"""
        if not await self.validate_config():
            raise ValueError("Claude配置不完整")
        
        headers = {
            "x-api-key": self.config['api_key'],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Claude API格式转换
        system_message = None
        conversation_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                conversation_messages.append(msg.to_dict())
        
        payload = {
            "model": self.config.get("model", "claude-3-haiku-20240307"),
            "max_tokens": self.config.get("max_tokens", 2000),
            "messages": conversation_messages,
            **kwargs
        }
        
        if system_message:
            payload["system"] = system_message
        
        url = f"{self.config['api_base']}/v1/messages"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url, 
                    headers=headers, 
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.get("timeout", 30))
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        content = ""
                        if data.get("content") and len(data["content"]) > 0:
                            content = data["content"][0].get("text", "")
                        
                        return LLMResponse(
                            content=content,
                            model=data.get("model", "claude"),
                            provider="claude",
                            usage=data.get("usage", {}),
                            metadata={"response_id": data.get("id")}
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(f"Claude API错误 {response.status}: {error_text}")
                        
            except asyncio.TimeoutError:
                raise Exception("Claude API请求超时")
            except Exception as e:
                self.logger.error(f"Claude API调用失败: {e}")
                raise


class KimiProvider(LLMProvider):
    """Kimi (月之暗面) 提供商"""
    
    def get_provider_name(self) -> str:
        return "kimi"
    
    async def validate_config(self) -> bool:
        """验证Kimi配置"""
        required_keys = ["api_key", "api_base", "model"]
        return all(key in self.config for key in required_keys)
    
    async def generate(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """调用Kimi API生成回复"""
        if not await self.validate_config():
            raise ValueError("Kimi配置不完整")
        
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        
        # 转换消息格式（Kimi使用OpenAI兼容格式）
        api_messages = [msg.to_dict() for msg in messages]
        
        payload = {
            "model": self.config.get("model", "moonshot-v1-8k"),
            "messages": api_messages,
            "max_tokens": self.config.get("max_tokens", 2000),
            "temperature": self.config.get("temperature", 0.7),
            "stream": False,
            **kwargs
        }
        
        url = f"{self.config['api_base']}/v1/chat/completions"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url, 
                    headers=headers, 
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.get("timeout", 30))
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return LLMResponse(
                            content=data["choices"][0]["message"]["content"],
                            model=data["model"],
                            provider="kimi",
                            usage=data.get("usage", {}),
                            metadata={"response_id": data.get("id")}
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(f"Kimi API错误 {response.status}: {error_text}")
                        
            except asyncio.TimeoutError:
                raise Exception("Kimi API请求超时")
            except Exception as e:
                self.logger.error(f"Kimi API调用失败: {e}")
                raise


class MockLLMProvider(LLMProvider):
    """模拟LLM提供商，用于开发和测试"""
    
    def get_provider_name(self) -> str:
        return "mock"
    
    async def validate_config(self) -> bool:
        """验证模拟配置"""
        return True  # 模拟提供商不需要验证
    
    async def generate(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """生成模拟回复"""
        # 模拟API调用延迟
        await asyncio.sleep(0.1)
        
        # 获取最后一条用户消息
        user_messages = [msg for msg in messages if msg.role == "user"]
        if not user_messages:
            return LLMResponse(
                content="我没有收到您的消息，请重新发送。",
                model="mock-gpt-3.5",
                provider="mock"
            )
        
        last_user_message = user_messages[-1].content.lower()
        
        # 根据用户消息生成相应的模拟回复
        if any(greeting in last_user_message for greeting in ["你好", "hello", "hi", "嗨"]):
            response_content = "你好！我是Polytool的智能助手。我可以回答您的问题，进行对话交流。有什么我可以帮助您的吗？"
        elif any(question in last_user_message for question in ["是谁", "你是", "介绍", "自己"]):
            response_content = "我是Polytool框架的智能ChatBot，基于先进的AI技术构建。我可以进行自然对话、回答问题、提供帮助和建议。"
        elif any(capability in last_user_message for capability in ["能做", "功能", "能力", "帮助"]):
            response_content = "我目前可以提供以下服务：\n• 💬 自然对话交流\n• 🧠 记忆对话上下文\n• ❓ 回答各种问题\n• 💡 提供建议和帮助\n• 🔧 技术相关咨询"
        elif any(tech in last_user_message for tech in ["python", "编程", "代码", "开发", "技术"]):
            response_content = "关于技术问题，我很乐意为您解答！Python是一门功能强大的编程语言，广泛用于Web开发、数据科学、人工智能等领域。您想了解哪个方面呢？"
        elif any(thanks in last_user_message for thanks in ["谢谢", "感谢", "thank"]):
            response_content = "不客气！很高兴能帮助您。如果还有其他问题，请随时告诉我。"
        elif any(goodbye in last_user_message for goodbye in ["再见", "拜拜", "bye", "goodbye"]):
            response_content = "再见！很高兴为您服务，期待下次交流！"
        else:
            response_content = f"我理解您提到了：{user_messages[-1].content}。这是一个有趣的话题！作为AI助手，我会尽力为您提供帮助和信息。您希望我具体回答什么问题呢？"
        
        return LLMResponse(
            content=response_content,
            model="mock-gpt-3.5-turbo", 
            provider="mock",
            usage={"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150},
            metadata={"mock": True, "response_time": 0.1}
        )


class LLMGateway:
    """
    LLM网关类
    
    提供统一的LLM访问接口，支持多种LLM提供商
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化LLM网关"""
        self.logger = get_logger("polytool.llm_gateway")
        self.providers: Dict[str, LLMProvider] = {}
        self.config = config or {}
        self.default_provider = None
        
    async def initialize(self):
        """异步初始化LLM网关"""
        self.logger.info("正在初始化LLM网关...")
        
        # 注册可用的提供商
        self._register_providers()
        
        # 初始化默认提供商
        default_provider_name = self.config.get("default_provider", "openai")
        if default_provider_name in self.providers:
            self.default_provider = self.providers[default_provider_name]
            self.logger.info(f"默认LLM提供商: {default_provider_name}")
        else:
            self.logger.warning(f"默认LLM提供商 '{default_provider_name}' 未找到")
        
        self.logger.info("LLM网关初始化完成")
        
    def _register_providers(self):
        """注册LLM提供商"""
        # 检查是否为模拟模式
        mock_llm = self.config.get("mock_llm", False)
        
        if mock_llm:
            # 模拟模式：只注册模拟提供商
            mock_provider = MockLLMProvider({})
            self.providers["openai"] = mock_provider  # 模拟openai
            self.providers["claude"] = mock_provider   # 模拟claude  
            self.providers["kimi"] = mock_provider     # 模拟kimi
            self.providers["mock"] = mock_provider     # 显式模拟提供商
            self.logger.info("模拟LLM提供商已注册")
        else:
            # 真实模式：注册真实提供商
            # 注册OpenAI
            if self.config.get("openai"):
                try:
                    openai_provider = OpenAIProvider(self.config["openai"])
                    self.providers["openai"] = openai_provider
                    self.logger.info("OpenAI提供商已注册")
                except Exception as e:
                    self.logger.error(f"注册OpenAI提供商失败: {e}")
            
            # 注册Claude
            if self.config.get("claude"):
                try:
                    claude_provider = ClaudeProvider(self.config["claude"])
                    self.providers["claude"] = claude_provider
                    self.logger.info("Claude提供商已注册")
                except Exception as e:
                    self.logger.error(f"注册Claude提供商失败: {e}")
            
            # 注册Kimi
            if self.config.get("kimi"):
                try:
                    kimi_provider = KimiProvider(self.config["kimi"])
                    self.providers["kimi"] = kimi_provider
                    self.logger.info("Kimi提供商已注册")
                except Exception as e:
                    self.logger.error(f"注册Kimi提供商失败: {e}")
    
    async def generate(
        self, 
        messages: List[LLMMessage], 
        provider: Optional[str] = None,
        retry_count: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        生成LLM回复
        
        Args:
            messages: 消息列表
            provider: 指定的提供商名称，默认使用默认提供商
            retry_count: 重试次数
            **kwargs: 其他参数
        
        Returns:
            LLMResponse: LLM响应
        """
        # 选择提供商
        if provider and provider in self.providers:
            llm_provider = self.providers[provider]
        elif self.default_provider:
            llm_provider = self.default_provider
        else:
            raise ValueError("没有可用的LLM提供商")
        
        # 设置重试参数
        if retry_count is None:
            retry_count = self.config.get("retry_count", 3)
        
        retry_delay = self.config.get("retry_delay", 1.0)
        
        # 尝试生成回复
        last_error = None
        for attempt in range(retry_count):
            try:
                if attempt > 0:
                    self.logger.info(f"重试LLM调用，第 {attempt + 1}/{retry_count} 次")
                    await asyncio.sleep(retry_delay * attempt)
                
                response = await llm_provider.generate(messages, **kwargs)
                self.logger.debug(f"LLM生成成功: {response.provider}/{response.model}")
                return response
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"LLM调用失败 (尝试 {attempt + 1}/{retry_count}): {e}")
                
                if attempt == retry_count - 1:
                    break
        
        # 所有重试都失败了
        self.logger.error(f"LLM调用彻底失败: {last_error}")
        raise Exception(f"LLM调用失败，已重试{retry_count}次: {last_error}")
    
    async def generate_simple(
        self, 
        system_prompt: str,
        user_message: str,
        provider: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        简化的生成接口
        
        Args:
            system_prompt: 系统提示词
            user_message: 用户消息
            provider: 提供商名称
            **kwargs: 其他参数
            
        Returns:
            str: 生成的回复内容
        """
        messages = []
        
        if system_prompt:
            messages.append(LLMMessage(role="system", content=system_prompt))
        
        messages.append(LLMMessage(role="user", content=user_message))
        
        response = await self.generate(messages, provider, **kwargs)
        return response.content
    
    def get_available_providers(self) -> List[str]:
        """获取可用的提供商列表"""
        return list(self.providers.keys())
    
    def get_provider_info(self, provider_name: str) -> Dict[str, Any]:
        """获取提供商信息"""
        if provider_name not in self.providers:
            return {}
        
        provider = self.providers[provider_name]
        return {
            "name": provider.get_provider_name(),
            "config": {k: "***" if "key" in k.lower() else v 
                      for k, v in provider.config.items()}
        }
        
    async def shutdown(self):
        """关闭LLM网关"""
        self.logger.info("正在关闭LLM网关...")
        self.providers.clear()
        self.default_provider = None
        self.logger.info("LLM网关已关闭")


def create_llm_gateway(settings) -> LLMGateway:
    """
    从配置创建LLM网关
    
    Args:
        settings: 配置对象
        
    Returns:
        LLMGateway: 配置好的LLM网关实例
    """
    import os
    
    config = {
        "default_provider": settings.DEFAULT_LLM_PROVIDER,
        "retry_count": settings.LLM_RETRY_COUNT,
        "retry_delay": settings.LLM_RETRY_DELAY,
    }
    
    # 检查是否为模拟模式
    mock_llm = os.getenv("MOCK_LLM", "false").lower() == "true"
    config["mock_llm"] = mock_llm
    
    if not mock_llm:
        # 真实模式：配置真实提供商
        # OpenAI配置
        if settings.OPENAI_API_KEY:
            config["openai"] = {
                "api_key": settings.OPENAI_API_KEY,
                "api_base": settings.OPENAI_API_BASE,
                "model": settings.OPENAI_MODEL,
                "max_tokens": settings.OPENAI_MAX_TOKENS,
                "temperature": settings.OPENAI_TEMPERATURE,
                "timeout": settings.LLM_TIMEOUT,
            }
        
        # Claude配置
        if settings.CLAUDE_API_KEY:
            config["claude"] = {
                "api_key": settings.CLAUDE_API_KEY,
                "api_base": settings.CLAUDE_API_BASE,
                "model": settings.CLAUDE_MODEL,
                "max_tokens": settings.CLAUDE_MAX_TOKENS,
                "timeout": settings.LLM_TIMEOUT,
            }
        
        # Kimi配置
        if settings.KIMI_API_KEY:
            config["kimi"] = {
                "api_key": settings.KIMI_API_KEY,
                "api_base": settings.KIMI_API_BASE,
                "model": settings.KIMI_MODEL,
                "max_tokens": settings.KIMI_MAX_TOKENS,
                "temperature": settings.KIMI_TEMPERATURE,
                "timeout": settings.LLM_TIMEOUT,
            }
    
    return LLMGateway(config)