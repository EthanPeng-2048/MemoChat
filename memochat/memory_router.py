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

# 预编译的正则表达式模式，避免重复编译的性能开销
QUERY_PATTERN = re.compile(MEMORY_QUERY_PATTERN, re.DOTALL)
WRITE_PATTERN = re.compile(MEMORY_WRITE_PATTERN, re.DOTALL)
EMPTY_PATTERN = re.compile(MEMORY_EMPTY_PATTERN, re.DOTALL)


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
    
    for match in QUERY_PATTERN.finditer(response):
        category = match.group(1).strip()
        key = match.group(2).strip()
        markers.append({
            "type": "query",
            "category": category,
            "key": key,
            "full_match": match.group(0),
        })
    
    for match in WRITE_PATTERN.finditer(response):
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
    
    for match in EMPTY_PATTERN.finditer(response):
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


def extract_first_marker(response: str) -> Optional[dict]:
    """从 AI 响应中提取第一个工具调用标记
    
    Args:
        response: AI 的响应文本
        
    Returns:
        第一个匹配的工具标记，如果没有则返回 None
    """
    logger.debug(f"正在解析 AI 响应：{response[:200]}")
    
    matches = []
    
    for match in QUERY_PATTERN.finditer(response):
        logger.debug(f"找到 QUERY 标记：{match.group(0)}")
        matches.append({
            "type": "query",
            "category": match.group(1).strip(),
            "key": match.group(2).strip(),
            "full_match": match.group(0),
            "position": match.start(),
        })
    
    for match in WRITE_PATTERN.finditer(response):
        logger.debug(f"找到 WRITE 标记：{match.group(0)}")
        matches.append({
            "type": "write",
            "category": match.group(1).strip(),
            "key": match.group(2).strip(),
            "value": match.group(3).strip(),
            "full_match": match.group(0),
            "position": match.start(),
        })
    
    for match in EMPTY_PATTERN.finditer(response):
        logger.debug(f"找到 EMPTY 标记：{match.group(0)}")
        matches.append({
            "type": "empty",
            "category": match.group(1).strip(),
            "key": match.group(2).strip(),
            "full_match": match.group(0),
            "position": match.start(),
        })
    
    if not matches:
        logger.warning(f"未找到任何工具标记，响应内容：{response[:200]}")
        return None
    
    matches.sort(key=lambda x: x["position"])
    first_match = matches[0]
    logger.debug(f"返回第一个工具标记：type={first_match['type']}, category={first_match['category']}, key={first_match['key']}")
    return first_match


def execute_tool(marker: dict) -> str:
    """执行单个工具调用并返回结果
    
    Args:
        marker: 工具标记字典
        
    Returns:
        工具执行结果的文本描述
    """
    if marker["type"] == "query":
        value = query(marker["category"], marker["key"])
        if value is not None:
            return f"工具执行结果：查询成功 - category={marker['category']}, key={marker['key']}, value={value}"
        else:
            return f"工具执行结果：查询结果为空 - category={marker['category']}, key={marker['key']}"
    
    elif marker["type"] == "write":
        success = upsert(marker["category"], marker["key"], marker["value"])
        if success:
            return f"工具执行结果：写入成功 - category={marker['category']}, key={marker['key']}, value={marker['value']}"
        else:
            return f"工具执行结果：写入失败 - category={marker['category']}, key={marker['key']}"
    
    elif marker["type"] == "empty":
        return f"工具执行结果：空记忆标记 - category={marker['category']}, key={marker['key']}"
    
    return "工具执行结果：未知工具类型"


def route_memory(
    user_input: str,
    history: list[dict],
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> tuple[Optional[str], list[dict]]:
    """处理用户输入，循环调用工具直到 AI 不再调用工具
    
    流程：
    1. 用户输入
    2. AI 返回工具调用（每次只调用一个工具）
    3. 系统执行工具并返回结果（包含用户输入）
    4. AI 根据结果决定是否继续调用工具
    5. 重复步骤 3-4 直到 AI 不再调用工具
    6. AI 返回最终回答
    
    Args:
        user_input: 用户输入
        history: 对话历史
        api_url: Llama API URL
        api_key: API 密钥
        model: 模型名称
        
    Returns:
        tuple: (AI 最终回复，工具执行结果列表)
    """
    context_prompt = build_context_prompt(user_input, history)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE},
        {"role": "user", "content": context_prompt},
    ]
    
    all_results = []
    tool_call_history = []
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        logger.debug(f"第 {iteration} 次 AI 调用")
        
        response = call_llama_api_with_retry(messages, api_url=api_url, api_key=api_key, model=model)
        
        if response is None:
            logger.error("Failed to get response from Llama API")
            return None, all_results
        
        marker = extract_first_marker(response)
        
        if marker is None:
            logger.info("AI 未调用工具，返回最终回答")
            return response, all_results
        
        logger.info(f"检测到工具调用：type={marker['type']}, category={marker['category']}, key={marker['key']}")
        
        tool_result = execute_tool(marker)
        logger.info(f"工具执行结果：{tool_result}")
        
        all_results.append({
            "type": marker["type"],
            "category": marker["category"],
            "key": marker["key"],
            "result": tool_result,
        })
        
        tool_call_history.append({
            "iteration": iteration,
            "type": marker["type"],
            "category": marker["category"],
            "key": marker["key"],
            "result": tool_result,
        })
        
        history_text = "\n\n".join([
            f"第 {call['iteration']} 次工具调用:\n"
            f"  类型：{call['type']}\n"
            f"  分类：{call['category']}\n"
            f"  键：{call['key']}\n"
            f"  结果：{call['result']}"
            for call in tool_call_history
        ])
        
        new_user_content = (
            f"用户输入：{user_input}\n\n"
            f"工具调用历史:\n{history_text}\n\n"
            f"请继续处理或给出最终回答。"
        )
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE},
            {"role": "user", "content": new_user_content},
        ]
    
    logger.warning(f"达到最大迭代次数 {max_iterations}，终止工具调用")
    return "达到最大工具调用次数限制", all_results


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
