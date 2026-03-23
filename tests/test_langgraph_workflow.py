from app.graph.builder import build_graph


def run_case(query: str):
    graph = build_graph()
    state = graph.invoke(
        {
            "session_id": "demo_user",
            "user_query": query,
            "retry_count": 0,
            "errors": [],
        }
    )

    print("=" * 100)
    print("QUERY:", query)
    print("TASK_TYPE:", state.get("task_type"))
    print("PLAN:", state.get("plan"))
    print("HAS_BUSINESS_CONTEXT:", bool(state.get("business_context")))
    print("HAS_SQL:", bool(state.get("sql_query")))
    print("HAS_ANALYSIS:", bool(state.get("analysis_result")))
    print("REFLECTION:", state.get("reflection"))
    print("FINAL_RESPONSE:", state.get("final_response"))
    print("FINAL_REPORT:")
    print(state.get("reporter_output"))
    print()


def main():
    cases = [
        "每个渠道的订单、营收和转化率是多少",
        "2026-03-01 到 2026-03-05 每天的营收趋势如何",
        "请分析这个A/B实验结果",
        "请分析这个漏斗",
    ]

    for q in cases:
        run_case(q)


if __name__ == "__main__":
    main()
