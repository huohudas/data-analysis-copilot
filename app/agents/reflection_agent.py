from typing import Dict, Any

from app.config import settings
from app.llm.client import call_json_llm
from app.llm.prompts import REFLECTION_PROMPT
from app.llm.prompt_utils import render_prompt


def rule_reflection(user_query: str, task_type: str, analysis_result: str) -> Dict[str, Any]:
    if not analysis_result or len(analysis_result.strip()) == 0:
        return {
            "passed": False,
            "needs_retry": True,
            "review_comment": "分析结果为空，说明前序节点未产出有效内容。",
            "final_response": "分析失败：系统没有生成有效结果。",
        }

    if task_type == "sql":
        if "分析结果" not in analysis_result:
            return {
                "passed": False,
                "needs_retry": True,
                "review_comment": "SQL 任务结果缺少明确分析说明。",
                "final_response": "分析失败：SQL 分析结果不完整。",
            }

    if task_type == "ab_test":
        if ("p-value" not in analysis_result) and ("显著" not in analysis_result):
            return {
                "passed": False,
                "needs_retry": True,
                "review_comment": "A/B Test 结果缺少显著性判断。",
                "final_response": "分析失败：A/B Test 结果缺少显著性信息。",
            }

    if task_type == "funnel":
        if ("流失" not in analysis_result) and ("转化率" not in analysis_result):
            return {
                "passed": False,
                "needs_retry": True,
                "review_comment": "漏斗分析结果缺少转化或流失信息。",
                "final_response": "分析失败：漏斗分析结果不完整。",
            }

    return {
        "passed": True,
        "needs_retry": False,
        "review_comment": "Reflection 检查通过：结果完整，任务类型匹配，可进入最终汇报阶段。",
        "final_response": analysis_result,
    }


def run_reflection_agent(
    user_query: str,
    task_type: str,
    analysis_result: str,
) -> Dict[str, Any]:
    if settings.llm_enabled:
        try:
            prompt = render_prompt(
                REFLECTION_PROMPT,
                user_query=user_query,
                task_type=task_type,
                analysis_result=analysis_result,
            )
            result = call_json_llm(
                system_prompt="你是一个严谨的分析结果复核器，只输出 JSON。",
                user_prompt=prompt,
            )
            return {
                "user_query": user_query,
                "task_type": task_type,
                "reflection_source": "llm_reflection",
                "passed": bool(result.get("passed", True)),
                "needs_retry": bool(result.get("needs_retry", False)),
                "review_comment": str(result.get("review_comment", "LLM Reflection 已完成复核。")),
                "final_response": str(result.get("final_response", analysis_result)),
            }
        except Exception as e:
            rule = rule_reflection(user_query, task_type, analysis_result)
            return {
                "user_query": user_query,
                "task_type": task_type,
                "reflection_source": "rule_fallback",
                "passed": rule["passed"],
                "needs_retry": rule["needs_retry"],
                "review_comment": f"{rule['review_comment']}（LLM Reflection 失败，已回退规则复核：{e}）",
                "final_response": rule["final_response"],
            }

    result = rule_reflection(user_query, task_type, analysis_result)
    return {
        "user_query": user_query,
        "task_type": task_type,
        "reflection_source": "rule_reflection",
        "passed": result["passed"],
        "needs_retry": result["needs_retry"],
        "review_comment": result["review_comment"],
        "final_response": result["final_response"],
    }
