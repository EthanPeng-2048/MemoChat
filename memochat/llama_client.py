import logging
from typing import Optional

import requests

from .config import (
    LLAMA_API_URL,
    LLAMA_API_KEY,
    LLAMA_MODEL,
    LLAMA_TIMEOUT,
    LLAMA_TEMPERATURE,
    LLAMA_MAX_TOKENS,
)

logger = logging.getLogger(__name__)


def call_llama_api(
    messages: list[dict[str, str]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    model: Optional[str] = None,
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Optional[str]:
    url = api_url if api_url else LLAMA_API_URL
    payload = {
        "messages": messages,
        "temperature": temperature if temperature is not None else LLAMA_TEMPERATURE,
        "max_tokens": max_tokens if max_tokens is not None else LLAMA_MAX_TOKENS,
        "stream": False,
    }
    
    if model or LLAMA_MODEL:
        payload["model"] = model if model else LLAMA_MODEL
        logger.debug(f"Using model: {payload['model']}")
    
    logger.debug(f"Calling Llama API: {url}")
    logger.debug(f"Payload: {payload}")
    
    headers = {}
    key = api_key if api_key else LLAMA_API_KEY
    if key:
        headers["Authorization"] = f"Bearer {key}"
        logger.debug("API key found, adding Authorization header")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=LLAMA_TIMEOUT)
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0].get("message", {}).get("content", "")
            logger.info(f"Received response from Llama API: {content[:100]}...")
            return content
        else:
            logger.error(f"Unexpected API response format: {result}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to call Llama API: {e}")
        return None


def call_llama_api_with_retry(
    messages: list[dict[str, str]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    max_retries: int = 3,
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Optional[str]:
    for attempt in range(max_retries):
        result = call_llama_api(messages, temperature, max_tokens, model=model, api_url=api_url, api_key=api_key)
        if result is not None:
            return result
        if attempt < max_retries - 1:
            logger.warning(f"Retry attempt {attempt + 1}/{max_retries}")
    
    logger.error(f"Failed to call Llama API after {max_retries} attempts")
    return None
