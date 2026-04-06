"""
MemoChat - Local AI Memory Routing System

A modular local AI memory routing system that can interface with llama.cpp server.
Provides structured memory management with query/write markers.
"""

import logging
from typing import Optional

from .config import (
    ALLOWED_CATEGORIES,
    CONTEXT_LIMIT_TOKENS,
    DB_PATH,
    LLAMA_API_URL,
    LLAMA_API_KEY,
    LLAMA_MODEL,
    LLAMA_TIMEOUT,
    LLAMA_TEMPERATURE,
    LLAMA_MAX_TOKENS,
    LOG_LEVEL,
    SYSTEM_PROMPT_TEMPLATE,
    MEMORY_QUERY_PATTERN,
    MEMORY_WRITE_PATTERN,
    MEMORY_EMPTY_PATTERN,
)
from .db_handler import init_db, query, upsert, delete, get_all_memory, get_memory_by_category
from .llama_client import call_llama_api, call_llama_api_with_retry
from .memory_router import (
    estimate_token_count,
    build_context_prompt,
    parse_memory_markers,
    process_memory_query,
    process_memory_write,
    process_memory_markers,
    route_memory,
    inject_memory_context,
)
from .pipeline import MemoryPipeline, run_interactive_pipeline, run_single_query
from .version import __version__


class MemoChat:
    """统一的 MemoChat 对象，管理所有配置和交互"""
    
    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        db_path: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        log_level: Optional[str] = None,
    ):
        """初始化 MemoChat 对象
        
        Args:
            api_url: Llama API 地址
            api_key: API 密钥
            model: 模型名称
            db_path: 数据库文件路径
            temperature: 温度参数
            max_tokens: 最大 token 数
            timeout: 超时时间（秒）
            log_level: 日志级别
        """
        self.api_url = api_url if api_url else LLAMA_API_URL
        self.api_key = api_key if api_key else LLAMA_API_KEY
        self.model = model if model else LLAMA_MODEL
        self.db_path = db_path if db_path else DB_PATH
        self.temperature = temperature if temperature is not None else LLAMA_TEMPERATURE
        self.max_tokens = max_tokens if max_tokens is not None else LLAMA_MAX_TOKENS
        self.timeout = timeout if timeout is not None else LLAMA_TIMEOUT
        self.log_level = log_level if log_level else LOG_LEVEL
        
        self.conversation_history: list[dict] = []
        
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("MemoChat initialized")
        
        init_db()
    
    def chat(
        self,
        user_input: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """与 AI 助手对话
        
        Args:
            user_input: 用户输入
            system_prompt: 自定义系统提示（可选）
            
        Returns:
            AI 助手的回复
        """
        self.logger.info(f"Processing user input: {user_input[:100]}...")
        
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
        })
        
        response, results = route_memory(
            user_input,
            self.conversation_history[:-1],
            api_url=self.api_url,
            api_key=self.api_key,
            model=self.model,
        )
        
        if response is None:
            self.logger.error("Failed to get response from memory router")
            return "Error: Failed to get response from AI"
        
        for result in results:
            if result["type"] == "write":
                self.conversation_history.append({
                    "role": "system",
                    "content": f"Memory saved: {result['result']}",
                })
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
        })
        
        return response
    
    def reset(self) -> None:
        """重置对话历史"""
        self.conversation_history = []
        self.logger.info("Conversation history reset")
    
    def get_history(self) -> list[dict]:
        """获取对话历史"""
        return self.conversation_history.copy()
    
    def get_memory(self) -> list[dict]:
        """获取所有记忆"""
        return get_all_memory()
    
    def get_memory_by_category(self, category: str) -> list[dict]:
        """按分类获取记忆"""
        return get_memory_by_category(category)


__all__ = [
    "ALLOWED_CATEGORIES",
    "CONTEXT_LIMIT_TOKENS",
    "DB_PATH",
    "LLAMA_API_URL",
    "LLAMA_API_KEY",
    "LLAMA_MODEL",
    "LLAMA_TIMEOUT",
    "LLAMA_TEMPERATURE",
    "LLAMA_MAX_TOKENS",
    "LOG_LEVEL",
    "SYSTEM_PROMPT_TEMPLATE",
    "MEMORY_QUERY_PATTERN",
    "MEMORY_WRITE_PATTERN",
    "MEMORY_EMPTY_PATTERN",
    "init_db",
    "query",
    "upsert",
    "delete",
    "get_all_memory",
    "get_memory_by_category",
    "call_llama_api",
    "call_llama_api_with_retry",
    "estimate_token_count",
    "build_context_prompt",
    "parse_memory_markers",
    "process_memory_query",
    "process_memory_write",
    "process_memory_markers",
    "route_memory",
    "inject_memory_context",
    "MemoryPipeline",
    "run_interactive_pipeline",
    "run_single_query",
    "MemoChat",
    "__version__",
]
