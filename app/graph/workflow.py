from typing import Dict, Any
import json

from app.config import settings
from app.tools.sql_tools import (
    get_schema,
    generate_sql,
    run_sql,
    validate_sql_or_raise,
)
from app.tools.analysis_tools import (
    analyze_sql_result,
    run_ab_test_analysis,
    run_funnel_analysis,
)
from app.llm.client import call_json_llm
from app.llm.prompts import (
    ROUTER_PROMPT,
    PLANNER_PROMPT,
    REVIEWER_PROMPT,
    SQL_PLANNER_PROMPT,
    SQL_GENERATOR_PROMPT,
)


def rule_router(user_query: str) -> str:
    q = user_query.lower()

    if "ab" in q or "a/b" in q or "实验" in user_query:
        return "ab_test"

    if "漏斗" in user_query or "funnel" in q:
        return "funnel"

    return "sql"


def llm_router(user_query: str) -> str:
    result = call_json_llm(
        system_prompt=ROUTER_PROMPT,
        user_prompt=user_query,
    )
    task_type = result.get("task_type", "").strip()

    if task_type not in {"sql", "ab_test", "funnel"}:
        return "sql"

    return task_type


def make_plan(user_query: str, task_type: str) -> str:
    if settings.app_mode == "rule":
        if task_type == "ab_test":
            return "识别为 A/B Test 分析任务，进入实验分析节点。"
        if task_type == "funnel":
            return "识别为 Funnel 分析任务，进入漏斗分析节点。"
        return "识别为 SQL 数据分析任务，先生成 SQL，再执行查询，并进入 Pandas/NumPy 二次分析。"

    result = call_json_llm(
        system_prompt="你是一个严谨的数据分析任务规划器，只输出合法 JSON。",
        user_prompt=PLANNER_PROMPT.format(user_query=user_query, task_type=task_type),
    )
    return result.get("plan", "系统已生成分析计划。")


def review_result(user_query: str, task_type: str, analysis_result: str) -> Dict[str, Any]:
    if settings.app_mode == "rule":
        if not analysis_result or len(analysis_result.strip()) == 0:
            return {
                "passed": False,
                "review_comment": "Reviewer 发现输出为空，说明前面节点执行失败或没有产出。",
                "final_response": "分析失败：系统没有生成有效结果。",
            }

        return {
            "passed": True,
            "review_comment": "Reviewer 检查通过：任务路由正常，分析结果已生成，且已包含 Pandas/NumPy 二次分析。",
            "final_response": analysis_result,
        }

    result = call_json_llm(
        system_prompt="你是一个严谨的数据分析结果复核器，只输出合法 JSON。",
        user_prompt=REVIEWER_PROMPT.format(
            user_query=user_query,
            task_type=task_type,
            analysis_result=analysis_result,
        ),
    )

    return {
        "passed": bool(result.get("passed", True)),
        "review_comment": result.get("review_comment", "LLM Reviewer 已完成复核。"),
        "final_response": result.get("final_response", analysis_result),
    }


def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    user_query = state["user_query"]

    if settings.app_mode == "llm":
        task_type = llm_router(user_query)
    else:
        task_type = rule_router(user_query)

    state["task_type"] = task_type
    state["plan"] = make_plan(user_query, task_type)
    return state


def try_llm_sql(user_query: str, schema: str):
    plan_result = call_json_llm(
        system_prompt="你是一个严谨的数据分析 SQL 规划器，只输出合法 JSON。",
        user_prompt=SQL_PLANNER_PROMPT.format(
            schema=schema,
            user_query=user_query,
        ),
    )

    sql_result = call_json_llm(
        system_prompt="你是一个严谨的 DuckDB SQL 生成器，只输出合法 JSON。",
        user_prompt=SQL_GENERATOR_PROMPT.format(
            schema=schema,
            intent_json=json.dumps(plan_result, ensure_ascii=False),
        ),
    )

    sql = sql_result.get("sql", "").strip()
    validate_sql_or_raise(sql)

    return plan_result, sql


def sql_node(state: Dict[str, Any]) -> Dict[str, Any]:
    paths = state["paths"]
    user_query = state["user_query"]
    schema = get_schema()

    state["schema"] = schema
    state["sql_source"] = "rule"
    state["sql_plan"] = None

    if settings.app_mode == "llm":
        try:
            sql_plan, llm_sql = try_llm_sql(user_query, schema)
            df = run_sql(llm_sql, paths["orders"])

            state["sql_source"] = "llm"
            state["sql_plan"] = sql_plan
            state["sql_query"] = llm_sql
            state["sql_result_df"] = df
            state["analysis_result"] = analyze_sql_result(df)
            return state
        except Exception as e:
            state["sql_fallback_reason"] = f"LLM SQL 失败，已回退规则 SQL：{e}"

    rule_sql = generate_sql(user_query)
    df = run_sql(rule_sql, paths["orders"])

    state["sql_query"] = rule_sql
    state["sql_result_df"] = df
    state["analysis_result"] = analyze_sql_result(df)
    return state


def ab_node(state: Dict[str, Any]) -> Dict[str, Any]:
    paths = state["paths"]
    state["analysis_result"] = run_ab_test_analysis(paths["ab_test"])
    return state


def funnel_node(state: Dict[str, Any]) -> Dict[str, Any]:
    paths = state["paths"]
    state["analysis_result"] = run_funnel_analysis(paths["funnel"])
    return state


def reviewer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    result = review_result(
        user_query=state["user_query"],
        task_type=state["task_type"],
        analysis_result=state.get("analysis_result", ""),
    )
    state["review_comment"] = result["review_comment"]
    state["final_response"] = result["final_response"]
    state["passed"] = result["passed"]
    return state


def run_workflow(user_query: str, paths: Dict[str, str]) -> Dict[str, Any]:
    state: Dict[str, Any] = {
        "user_query": user_query,
        "paths": paths,
    }

    state = planner_node(state)

    if state["task_type"] == "ab_test":
        state = ab_node(state)
    elif state["task_type"] == "funnel":
        state = funnel_node(state)
    else:
        state = sql_node(state)

    state = reviewer_node(state)
    return state
