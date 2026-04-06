from typing import Final

ALLOWED_CATEGORIES: Final[list[str]] = [
    "user_preference",
    "conversation_history",
    "factual_knowledge",
    "task_context",
    "personal_info"
]

CONTEXT_LIMIT_TOKENS: Final[int] = 4096

DB_PATH: Final[str] = "memochat.db"

LLAMA_API_URL: Final[str] = "http://localhost:8080/v1/chat/completions"

LLAMA_API_KEY: Final[str] = ""

LLAMA_MODEL: Final[str] = ""

LLAMA_TIMEOUT: Final[int] = 120

LLAMA_TEMPERATURE: Final[float] = 0.7

LLAMA_MAX_TOKENS: Final[int] = 1024

LOG_LEVEL: Final[str] = "INFO"

SYSTEM_PROMPT_TEMPLATE: Final[str] = (
    "你是一个助手。你拥有一个结构化记忆表，仅包含字段：category(分类), key(键), value(值)。\n"
    "工具调用规则：\n"
    "1. 每次只能调用一个工具（一个 MEM_QUERY 或 MEM_WRITE），不能同时调用多个。\n"
    "2. 当需要读取记忆时，输出：#[MEM_QUERY: category=分类,key=键]\n"
    "3. 当需要保存新记忆时，输出：#[MEM_WRITE: category=分类,key=键，value=内容]\n"
    "4. 系统会执行你的工具调用并返回结果，你可以继续调用下一个工具或给出最终回答。\n"
    "5. 当你完成所有工具调用后，请直接给出最终回答。\n"
    "注意：工具调用标记必须单独一行，不要与其他文本混合。"
)

MEMORY_QUERY_PATTERN: Final[str] = r"#\[MEM_QUERY:\s*category=([^,]+),\s*key=([^\]]+)\]"
MEMORY_WRITE_PATTERN: Final[str] = r"#\[MEM_WRITE:\s*category=([^,]+),\s*key=([^,]+),\s*value=(.+)\]"
MEMORY_EMPTY_PATTERN: Final[str] = r"#\[MEM_EMPTY:\s*category=([^,]+),\s*key=([^\]]+)\]"
