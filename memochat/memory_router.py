import logging
import re
from typing import Optional

from .config import (
    SYSTEM_PROMPT_TEMPLATE,
    MEMORY_QUERY_PATTERN,
    MEMORY_WRITE_PATTERN,
    MEMORY_EMPTY_PATTERN,
    CONTEXT_LIMIT_TOKENS,
)
from .db_handler import query, upsert, delete, get_all_memory
from .llama_client import call_llama_api_with_retry

logger = logging.getLogger(__name__)


def estimate_token_count(text: str) -> int:
    return len(text) // 4


def build_context_prompt(user_input: str, history: list[dict]) -> str:
    context_parts = [SYSTEM_PROMPT_TEMPLATE]
    
    all_memory = get_all_memory()
    if all_memory:
        context_parts.append("\n当前数据库中的记忆:")
        for mem in all_memory:
            context_parts.append(f"- category={mem['category']}, key={mem['key']}, value={mem['value']}")
    
    if history:
        context_parts.append("\n历史对话:")
        for msg in history[-5:]:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            context_parts.append(f"{role.upper()}: {content}")
    
    context_parts.append(f"\n用户输入: {user_input}")
    
    return "\n".join(context_parts)


def parse_memory_markers(response: str) -> list[dict]:
    markers = []
    
    query_pattern = re.compile(MEMORY_QUERY_PATTERN, re.DOTALL)
    for match in query_pattern.finditer(response):
        category = match.group(1).strip()
        key = match.group(2).strip()
        markers.append({
            "type": "query",
            "category": category,
            "key": key,
            "full_match": match.group(0),
        })
    
    write_pattern = re.compile(MEMORY_WRITE_PATTERN, re.DOTALL)
    for match in write_pattern.finditer(response):
        category = match.group(1).strip()
        key = match.group(2).strip()
        value = match.group(3).strip()
        markers.append({
            "type": "write",
            "category": category,
            "key": key,
            "value": value,
            "full_match": match.group(0),
        })
    
    empty_pattern = re.compile(MEMORY_EMPTY_PATTERN, re.DOTALL)
    for match in empty_pattern.finditer(response):
        category = match.group(1).strip()
        key = match.group(2).strip()
        markers.append({
            "type": "empty",
            "category": category,
            "key": key,
            "full_match": match.group(0),
        })
    
    return markers


def process_memory_query(category: str, key: str) -> str:
    value = query(category, key)
    
    if value is not None:
        return f"记忆已找到: category={category}, key={key}, value={value}"
    else:
        return f"#[MEM_EMPTY: category={category}, key={key}]"


def process_memory_write(category: str, key: str, value: str) -> bool:
    return upsert(category, key, value)


def process_memory_markers(markers: list[dict]) -> tuple[str, list[dict]]:
    results = []
    output_parts = []
    
    for marker in markers:
        if marker["type"] == "query":
            result = process_memory_query(marker["category"], marker["key"])
            results.append({
                "type": "query",
                "category": marker["category"],
                "key": marker["key"],
                "result": result,
            })
            output_parts.append(result)
        
        elif marker["type"] == "write":
            success = process_memory_write(
                marker["category"],
                marker["key"],
                marker["value"],
            )
            result = f"记忆已保存: category={marker['category']}, key={marker['key']}"
            results.append({
                "type": "write",
                "category": marker["category"],
                "key": marker["key"],
                "success": success,
                "result": result,
            })
            output_parts.append(result)
        
        elif marker["type"] == "empty":
            results.append({
                "type": "empty",
                "category": marker["category"],
                "key": marker["key"],
                "result": marker["full_match"],
            })
            output_parts.append(marker["full_match"])
    
    return "\n".join(output_parts), results


def route_memory(
    user_input: str,
    history: list[dict],
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> tuple[Optional[str], list[dict], bool]:
    context_prompt = build_context_prompt(user_input, history)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE},
        {"role": "user", "content": context_prompt},
    ]
    
    response = call_llama_api_with_retry(messages, api_url=api_url, api_key=api_key, model=model)
    
    if response is None:
        logger.error("Failed to get response from Llama API")
        return None, [], False
    
    markers = parse_memory_markers(response)
    
    if not markers:
        logger.info("No memory markers found in response")
        return response, [], False
    
    output, results = process_memory_markers(markers)
    
    if any(m["type"] in ("query", "empty") for m in markers):
        logger.info("Memory queries or empty results detected, performing secondary generation")
        
        augmented_prompt = (
            f"{context_prompt}\n\n"
            f"已处理的记忆操作结果:\n{output}"
        )
        
        secondary_messages = [
            {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE},
            {"role": "user", "content": augmented_prompt},
        ]
        
        final_response = call_llama_api_with_retry(secondary_messages, api_url=api_url, api_key=api_key, model=model)
        
        if final_response is None:
            logger.error("Failed to get secondary response from Llama API")
            return response, results, True
        
        return final_response, results, True
    
    return response, results, False


def inject_memory_context(prompt: str, history: list[dict]) -> str:
    total_chars = 0
    max_chars = CONTEXT_LIMIT_TOKENS * 4
    
    context_parts = [SYSTEM_PROMPT_TEMPLATE]
    
    for msg in history[-10:]:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        context_parts.append(f"{role.upper()}: {content}")
        total_chars += len(content)
        
        if total_chars >= max_chars:
            break
    
    context_parts.append(f"\n用户输入: {prompt}")
    
    return "\n".join(context_parts)
