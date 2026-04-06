"""
MemoChat - Local AI Memory Routing System

A modular local AI memory routing system that can interface with llama.cpp server.
Provides structured memory management with query/write markers.
"""

from .config import (
    ALLOWED_CATEGORIES,
    CONTEXT_LIMIT_TOKENS,
    DB_PATH,
    LLAMA_API_URL,
    LLAMA_API_KEY,
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

__all__ = [
    "ALLOWED_CATEGORIES",
    "CONTEXT_LIMIT_TOKENS",
    "DB_PATH",
    "LLAMA_API_URL",
    "LLAMA_API_KEY",
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
    "__version__",
]
