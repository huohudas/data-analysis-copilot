import json
import re
from typing import Dict, Any
import requests

from app.config import settings


def _extract_json(content: str) -> Dict[str, Any]:
    text = content.strip()

    # 去掉 markdown 代码块
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    # 先直接尝试
    try:
        return json.loads(text)
    except Exception:
        pass

    # 再尝试提取第一个 {...}
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        candidate = match.group(0)
        return json.loads(candidate)

    raise ValueError(f"模型返回不是合法 JSON: {text[:500]}")


def call_json_llm(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    if not settings.llm_enabled:
        raise RuntimeError("当前未启用可用的 LLM 模式")

    provider = settings.provider_config()
    headers = {
        "Authorization": f"Bearer {provider['api_key']}",
        "Content-Type": "application/json",
    }

    payload: Dict[str, Any] = {
        "model": provider["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": settings.llm_temperature,
        "max_tokens": 2048,
        "response_format": {"type": "json_object"},
    }

    if settings.model_provider == "deepseek" and provider["model"] == "deepseek-reasoner":
        payload["thinking"] = {"type": "enabled"}

    resp = requests.post(
        provider["base_url"],
        headers=headers,
        json=payload,
        timeout=settings.llm_timeout,
    )
    resp.raise_for_status()
    data = resp.json()

    try:
        content = data["choices"][0]["message"]["content"]
    except Exception as e:
        raise ValueError(f"无法解析模型返回: {e}; raw={json.dumps(data, ensure_ascii=False)[:800]}")

    print("\n[LLM RAW OUTPUT]\n", content, "\n")
    return _extract_json(content)
