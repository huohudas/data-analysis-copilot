from app.config import settings
from app.graph.builder import build_graph


def main():
    graph = build_graph()

    print("=== DataMind Copilot V2 ===")
    print(settings.startup_note())
    print("当前 effective mode:", settings.effective_mode)
    print("当前 provider:", settings.model_provider)
    print("你可以输入：")
    print("1. 每个渠道的订单、营收和转化率是多少")
    print("2. 2026-03-01 到 2026-03-05 每天的营收趋势如何")
    print("3. 请分析这个A/B实验结果")
    print("4. 请分析这个漏斗")
    print()

    user_query = input("请输入你的问题：").strip()

    state = graph.invoke(
        {
            "session_id": "demo_user",
            "user_query": user_query,
            "retry_count": 0,
            "errors": [],
        }
    )

    print("\n[Task Type]")
    print(state.get("task_type"))

    print("\n[Plan]")
    print(state.get("plan"))

    print("\n[Business Context]")
    print(state.get("business_context"))

    if state.get("sql_query"):
        print("\n[SQL Source]")
        print(state.get("sql_source"))
        if state.get("sql_fallback_reason"):
            print("\n[SQL Fallback]")
            print(state.get("sql_fallback_reason"))
        print("\n[SQL Query]")
        print(state.get("sql_query"))

    print("\n[Analysis Result]")
    print(state.get("analysis_result"))

    print("\n[Reflection]")
    print(state.get("reflection"))

    print("\n[Final Report]")
    print(state.get("reporter_output"))


if __name__ == "__main__":
    main()
