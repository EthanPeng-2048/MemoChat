import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()

ALLOWED_CATEGORIES: Final[list[str]] = [
    "user_preference",
    "conversation_history",
    "factual_knowledge",
    "task_context",
    "personal_info"
]

CONTEXT_LIMIT_TOKENS: Final[int] = 4096

DB_PATH: Final[str] = os.getenv("DB_PATH", "memochat.db")

LLAMA_API_URL: Final[str] = os.getenv("LLAMA_API_URL", "http://localhost:8080/v1/chat/completions")

LLAMA_API_KEY: Final[str] = os.getenv("LLAMA_API_KEY", "")

LLAMA_TIMEOUT: Final[int] = int(os.getenv("LLAMA_TIMEOUT", "120"))

LLAMA_TEMPERATURE: Final[float] = float(os.getenv("LLAMA_TEMPERATURE", "0.7"))

LLAMA_MAX_TOKENS: Final[int] = int(os.getenv("LLAMA_MAX_TOKENS", "1024"))

LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO")

SYSTEM_PROMPT_TEMPLATE: Final[str] = (
    "你是一个助手。你拥有一个结构化记忆表，仅包含字段：category(分类), key(键), value(值)。"
    "当需要读取记忆时，必须严格输出：#[MEM_QUERY: category=分类, key=键]。"
    "当需要保存新记忆时，输出：#[MEM_WRITE: category=分类, key=键, value=内容]。"
    "不要解释指令，直接输出或结合回答。"
)

MEMORY_QUERY_PATTERN: Final[str] = r"#\[MEM_QUERY:\s*category=([^,]+),\s*key=([^\]]+)\]"
MEMORY_WRITE_PATTERN: Final[str] = r"#\[MEM_WRITE:\s*category=([^,]+),\s*key=([^,]+),\s*value=(.+)\]"
MEMORY_EMPTY_PATTERN: Final[str] = r"#\[MEM_EMPTY:\s*category=([^,]+),\s*key=([^\]]+)\]"
