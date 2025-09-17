#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polytool配置管理模块
===================

提供全局配置管理，支持环境变量、配置文件等多种配置方式
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class Settings:
    """
    应用程序配置类
    
    支持从环境变量、.env文件等加载配置
    """
    
    def __init__(self):
        """初始化配置"""
        # 加载.env文件
        self._load_env_file()
        
        # 应用基础信息
        self.APP_NAME = os.getenv("APP_NAME", "Polytool")
        self.VERSION = os.getenv("VERSION", "0.1.0")
        self.DESCRIPTION = os.getenv("DESCRIPTION", "通用智能体框架")
        
        # 服务器配置
        self.SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
        self.SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
        self.API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
        
        # 日志配置
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")
        self.LOG_FORMAT = os.getenv(
            "LOG_FORMAT", 
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # 数据库配置
        # 向量数据库
        self.VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "faiss")
        self.VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))
        
        # 图数据库
        self.GRAPH_DB_TYPE = os.getenv("GRAPH_DB_TYPE", "networkx")
        self.GRAPH_DB_PATH = os.getenv("GRAPH_DB_PATH", "./data/graph_db")
        
        # 文档存储
        self.DOCUMENT_STORE_TYPE = os.getenv("DOCUMENT_STORE_TYPE", "local")
        self.DOCUMENT_STORE_PATH = os.getenv("DOCUMENT_STORE_PATH", "./data/documents")
        
        # LLM配置
        self.DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        
        # OpenAI配置
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
        self.OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        # Claude配置
        self.CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
        self.CLAUDE_API_BASE = os.getenv("CLAUDE_API_BASE", "https://api.anthropic.com")
        self.CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
        self.CLAUDE_MAX_TOKENS = int(os.getenv("CLAUDE_MAX_TOKENS", "2000"))
        
        # Kimi配置
        self.KIMI_API_KEY = os.getenv("KIMI_API_KEY")
        self.KIMI_API_BASE = os.getenv("KIMI_API_BASE", "https://api.moonshot.cn")
        self.KIMI_MODEL = os.getenv("KIMI_MODEL", "moonshot-v1-8k")
        self.KIMI_MAX_TOKENS = int(os.getenv("KIMI_MAX_TOKENS", "2000"))
        self.KIMI_TEMPERATURE = float(os.getenv("KIMI_TEMPERATURE", "0.7"))
        
        # LLM通用配置
        self.LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "30"))
        self.LLM_RETRY_COUNT = int(os.getenv("LLM_RETRY_COUNT", "3"))
        self.LLM_RETRY_DELAY = float(os.getenv("LLM_RETRY_DELAY", "1.0"))
        
        # 工具配置
        self.TOOLS_CONFIG_PATH = os.getenv("TOOLS_CONFIG_PATH", "./config/tools.yaml")
        self.PLUGINS_PATH = os.getenv("PLUGINS_PATH", "./plugins")
        
        # 安全配置
        self.SECRET_KEY = os.getenv("SECRET_KEY", "polytool-secret-key-change-in-production")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # 性能配置
        self.MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.MAX_CONTENT_SIZE = int(os.getenv("MAX_CONTENT_SIZE", str(10 * 1024 * 1024)))
        
        # 记忆管理配置
        self.MEMORY_MAX_SIZE = int(os.getenv("MEMORY_MAX_SIZE", "1000"))
        self.MEMORY_CHUNK_SIZE = int(os.getenv("MEMORY_CHUNK_SIZE", "1000"))
        self.MEMORY_OVERLAP_SIZE = int(os.getenv("MEMORY_OVERLAP_SIZE", "200"))
        
        # 开发配置
        self.DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
        self.RELOAD = os.getenv("RELOAD", "false").lower() in ("true", "1", "yes")
        
        # 确保必要的目录存在
        self._ensure_directories()
    
    def _load_env_file(self):
        """加载.env文件"""
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key not in os.environ:  # 不覆盖已存在的环境变量
                            os.environ[key] = value
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            Path(self.VECTOR_DB_PATH).parent,
            Path(self.GRAPH_DB_PATH).parent,
            Path(self.DOCUMENT_STORE_PATH),
            Path(self.PLUGINS_PATH),
        ]
        
        # 确保日志目录存在
        if self.LOG_FILE_PATH:
            directories.append(Path(self.LOG_FILE_PATH).parent)
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return {
            "vector_db": {
                "type": self.VECTOR_DB_TYPE,
                "path": self.VECTOR_DB_PATH,
                "embedding_model": self.EMBEDDING_MODEL,
                "dimension": self.EMBEDDING_DIMENSION,
            },
            "graph_db": {
                "type": self.GRAPH_DB_TYPE,
                "path": self.GRAPH_DB_PATH,
            },
            "document_store": {
                "type": self.DOCUMENT_STORE_TYPE,
                "path": self.DOCUMENT_STORE_PATH,
            }
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置"""
        return {
            "default_provider": self.DEFAULT_LLM_PROVIDER,
            "openai": {
                "api_key": self.OPENAI_API_KEY,
                "api_base": self.OPENAI_API_BASE,
                "model": self.OPENAI_MODEL,
            }
        }
    
    def get_server_config(self) -> Dict[str, Any]:
        """获取服务器配置"""
        return {
            "host": self.SERVER_HOST,
            "port": self.SERVER_PORT,
            "api_prefix": self.API_PREFIX,
            "debug": self.DEBUG,
            "reload": self.RELOAD,
        }


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """
    获取配置实例
    
    Returns:
        Settings: 配置实例
    """
    return settings


def update_settings(**kwargs) -> None:
    """
    更新配置
    
    Args:
        **kwargs: 配置参数
    """
    global settings
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """
    获取配置实例
    
    Returns:
        Settings: 配置实例
    """
    return settings


def update_settings(**kwargs) -> None:
    """
    更新配置
    
    Args:
        **kwargs: 配置参数
    """
    global settings
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)