import traceback
from pprint import pprint

from app.config import settings
from app.llm.client import call_json_llm
from app.llm.prompts import (
    ROUTER_PROMPT,
    PLANNER_PROMPT,
    SQL_INTENT_PROMPT,
    SQL_GENERATOR_PROMPT,
    REFLECTION_PROMPT,
)
from app.tools.sql_tools import get_schema
from app.graph.builder import build_graph


def print_header(title: str):
    print("\n" + "=" * 120)
    print(title)
    print("=" * 120)


def test_router(query: str):
    print_header("1) TEST ROUTER")
    try:
        result = call_json_llm(
            system_prompt=ROUTER_PROMPT,
            user_prompt=query,
        )
        print("[ROUTER RESULT]")
        pprint(result)
    except Exception as e:
        print("[ROUTER ERROR]")
        print(repr(e))
        traceback.print_exc()


def test_planner(query: str, task_type: str):
    print_header("2) TEST PLANNER")
    try:
        prompt = PLANNER_PROMPT.format(
            user_query=query,
            task_type=task_type,
        )
        print("[PLANNER PROMPT PREVIEW]")
        print(prompt[:1200])

        result = call_json_llm(
            system_prompt="你是一个严谨的数据分析规划器，只输出 JSON。",
            user_prompt=prompt,
        )
        print("[PLANNER RESULT]")
        pprint(result)
    except Exception as e:
        print("[PLANNER ERROR]")
        print(repr(e))
        traceback.print_exc()


def test_sql_intent(query: str, business_context: str):
    print_header("3) TEST SQL INTENT")
    try:
        schema = get_schema()
        prompt = SQL_INTENT_PROMPT.format(
            schema=schema,
            business_context=business_context,
            user_query=query,
        )
        print("[SQL INTENT PROMPT PREVIEW]")
        print(prompt[:1500])

        result = call_json_llm(
            system_prompt="你是一个严谨的数据分析 SQL 规划器，只输出 JSON。",
            user_prompt=prompt,
        )
        print("[SQL INTENT RESULT]")
        pprint(result)
        return result
    except Exception as e:
        print("[SQL INTENT ERROR]")
        print(repr(e))
        traceback.print_exc()
        return None


def test_sql_generator(intent_obj):
    print_header("4) TEST SQL GENERATOR")
    if intent_obj is None:
        print("[SKIPPED] intent_obj is None")
        return

    try:
        import json
        schema = get_schema()
        prompt = SQL_GENERATOR_PROMPT.format(
            schema=schema,
            intent_json=json.dumps(intent_obj, ensure_ascii=False),
        )
        print("[SQL GENERATOR PROMPT PREVIEW]")
        print(prompt[:1500])

        result = call_json_llm(
            system_prompt="你是一个严谨的 DuckDB SQL 生成器，只输出 JSON。",
            user_prompt=prompt,
        )
        print("[SQL GENERATOR RESULT]")
        pprint(result)
    except Exception as e:
        print("[SQL GENERATOR ERROR]")
        print(repr(e))
        traceback.print_exc()


def test_reflection(query: str, task_type: str, analysis_result: str):
    print_header("5) TEST REFLECTION")
    try:
        prompt = REFLECTION_PROMPT.format(
            user_query=query,
            task_type=task_type,
            analysis_result=analysis_result,
        )
        print("[REFLECTION PROMPT PREVIEW]")
        print(prompt[:1500])

        result = call_json_llm(
            system_prompt="你是一个严谨的分析结果复核器，只输出 JSON。",
            user_prompt=prompt,
        )
        print("[REFLECTION RESULT]")
        pprint(result)
    except Exception as e:
        print("[REFLECTION ERROR]")
        print(repr(e))
        traceback.print_exc()


def test_full_graph(query: str):
    print_header("6) TEST FULL GRAPH")
    try:
        graph = build_graph()
        state = graph.invoke(
            {
                "session_id": "diag_user",
                "user_query": query,
                "retry_count": 0,
                "errors": [],
            }
        )

        print("[FINAL STATE KEYS]")
        pprint(sorted(state.keys()))

        print("\n[TASK_TYPE]")
        print(state.get("task_type"))

        print("\n[PLAN]")
        print(state.get("plan"))

        print("\n[SQL_SOURCE]")
        print(state.get("sql_source"))

        print("\n[SQL_FALLBACK_REASON]")
        print(state.get("sql_fallback_reason"))

        print("\n[REFLECTION]")
        pprint(state.get("reflection"))

        print("\n[FINAL_RESPONSE PREVIEW]")
        print((state.get("final_response") or "")[:1000])

        print("\n[FINAL_REPORT PREVIEW]")
        print((state.get("reporter_output") or "")[:1500])

    except Exception as e:
        print("[FULL GRAPH ERROR]")
        print(repr(e))
        traceback.print_exc()


def main():
    query = "每个渠道的订单、营收和转化率是多少"
    task_type = "sql"
    business_context = (
        "指标定义：orders 是订单数，revenue 是营收，conversion_rate=orders/users。"
        "表 orders 包含 date, channel, orders, revenue, users 字段。"
    )
    analysis_result = (
        "分析结果：渠道维度汇总如下。\n"
        "- ads，订单 740.0，营收 22200.0，转化率 0.1165，营收占比 57.81%，订单占比 57.81%\n"
        "- seo，订单 540.0，营收 16200.0，转化率 0.1057，营收占比 42.19%，订单占比 42.19%\n\n"
        "Pandas/NumPy 二次分析：\n"
        "- 营收最高渠道：ads（22200.0）\n"
        "- 转化率最高渠道：ads（0.1165）\n"
        "- 转化率最低渠道：seo（0.1057）\n"
        "- 订单统计：均值 640.00，中位数 640.00，最大值 740.00，最小值 540.00，标准差 100.00"
    )

    print_header("ENV INFO")
    print("REQUESTED_MODE =", settings.app_mode)
    print("EFFECTIVE_MODE =", settings.effective_mode)
    print("MODEL_PROVIDER =", settings.model_provider)
    print("GLM_MODEL =", settings.glm_model)
    print("GLM_API_KEY_EXISTS =", bool(settings.glm_api_key))
    print("STARTUP_NOTE =", settings.startup_note())

    test_router(query)
    test_planner(query, task_type)
    intent_obj = test_sql_intent(query, business_context)
    test_sql_generator(intent_obj)
    test_reflection(query, task_type, analysis_result)
    test_full_graph(query)


if __name__ == "__main__":
    main()
