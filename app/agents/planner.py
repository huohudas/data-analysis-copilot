from typing import Dict, Any

from app.config import settings
from app.llm.client import call_json_llm
from app.llm.prompts import ROUTER_PROMPT, PLANNER_PROMPT
from app.llm.prompt_utils import render_prompt


def rule_route(user_query: str) -> str:
    q = user_query.lower()

    if "ab" in q or "a/b" in q or "实验" in user_query or "显著性" in user_query:
        return "ab_test"

    if "漏斗" in user_query or "funnel" in q or "流失" in user_query:
        return "funnel"

    return "sql"


def rule_plan(user_query: str, task_type: str) -> str:
    if task_type == "ab_test":
        return "识别为 A/B Test 分析任务，后续应读取实验数据，计算转化率、uplift 和显著性结论。"
    if task_type == "funnel":
        return "识别为漏斗分析任务，后续应读取漏斗数据，分析各步骤转化率和流失最严重环节。"
    return "识别为 SQL 数据分析任务，后续应先解析指标、维度和过滤条件，再生成 SQL 查询，并进入 Python 二次分析。"


def llm_route(user_query: str) -> str:
    result = call_json_llm(
        system_prompt=ROUTER_PROMPT,
        user_prompt=user_query,
    )
    task_type = str(result.get("task_type", "sql")).strip()
    if task_type not in {"sql", "ab_test", "funnel"}:
        return "sql"
    return task_type


def llm_plan(user_query: str, task_type: str) -> str:
    prompt = render_prompt(
        PLANNER_PROMPT,
        user_query=user_query,
        task_type=task_type,
    )
    result = call_json_llm(
        system_prompt="你是一个严谨的数据分析规划器，只输出 JSON。",
        user_prompt=prompt,
    )
    return str(result.get("plan", "系统已生成分析计划。")).strip()


def run_planner_agent(user_query: str) -> Dict[str, Any]:
    settings.validate()

    output: Dict[str, Any] = {
        "user_query": user_query,
        "requested_mode": settings.app_mode,
        "effective_mode": settings.effective_mode,
        "model_provider": settings.model_provider,
        "startup_note": settings.startup_note(),
    }

    if settings.effective_mode == "rule":
        task_type = rule_route(user_query)
        plan = rule_plan(user_query, task_type)
        output["planner_source"] = "rule"
        output["task_type"] = task_type
        output["plan"] = plan
        return output

    try:
        task_type = llm_route(user_query)
        plan = llm_plan(user_query, task_type)

        output["planner_source"] = "llm"
        output["task_type"] = task_type
        output["plan"] = plan
        return output

    except Exception as e:
        task_type = rule_route(user_query)
        plan = rule_plan(user_query, task_type)

        output["planner_source"] = "rule_fallback"
        output["task_type"] = task_type
        output["plan"] = plan
        output["fallback_reason"] = f"LLM Planner 失败，已回退规则模式：{e}"
        return output
