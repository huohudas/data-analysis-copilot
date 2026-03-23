from typing import Dict, Any


def build_summary(user_query: str, task_type: str) -> str:
    if task_type == "sql":
        return f"- 任务类型：SQL 指标分析\n- 目标问题：{user_query}"
    if task_type == "ab_test":
        return f"- 任务类型：A/B Test 分析\n- 目标问题：{user_query}"
    if task_type == "funnel":
        return f"- 任务类型：Funnel 漏斗分析\n- 目标问题：{user_query}"
    return f"- 目标问题：{user_query}"


def normalize_multiline_text(text: str) -> str:
    if not text:
        return "未提供内容。"

    lines = [line.rstrip() for line in text.splitlines()]
    while lines and not lines[-1]:
        lines.pop()

    return "\n".join(lines).strip() if lines else "未提供内容。"


def build_report(
    user_query: str,
    task_type: str,
    plan: str,
    business_context: str,
    analysis_result: str,
    reflection_comment: str,
) -> str:
    sections = [
        "=== DataMind Copilot Report ===",
        "",
        "[任务概述]",
        normalize_multiline_text(build_summary(user_query, task_type)),
        "",
        "[执行计划]",
        normalize_multiline_text(plan),
        "",
        "[业务上下文]",
        normalize_multiline_text(business_context),
        "",
        "[分析结果]",
        normalize_multiline_text(analysis_result),
        "",
        "[Reflection 复核]",
        normalize_multiline_text(reflection_comment),
    ]
    return "\n".join(sections)


def run_reporter_agent(
    user_query: str,
    task_type: str,
    plan: str,
    business_context: str,
    analysis_result: str,
    reflection_result: Dict[str, Any],
) -> Dict[str, Any]:
    report = build_report(
        user_query=user_query,
        task_type=task_type,
        plan=plan,
        business_context=business_context,
        analysis_result=analysis_result,
        reflection_comment=reflection_result["review_comment"],
    )

    return {
        "user_query": user_query,
        "task_type": task_type,
        "reporter_source": "structured_text_reporter_v2",
        "final_report": report,
        "final_response": reflection_result["final_response"],
    }
