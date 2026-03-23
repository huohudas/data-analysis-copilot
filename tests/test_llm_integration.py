from app.config import settings
from app.graph.builder import build_graph


def run_case(query: str):
    graph = build_graph()
    state = graph.invoke(
        {
            "session_id": "llm_test_user",
            "user_query": query,
            "retry_count": 0,
            "errors": [],
        }
    )

    print("=" * 100)
    print("QUERY:", query)
    print("REQUESTED_MODE:", settings.app_mode)
    print("EFFECTIVE_MODE:", settings.effective_mode)
    print("PROVIDER:", settings.model_provider)
    print("TASK_TYPE:", state.get("task_type"))
    print("SQL_SOURCE:", state.get("sql_source"))
    print("SQL_FALLBACK_REASON:", state.get("sql_fallback_reason"))
    print("REFLECTION:", state.get("reflection"))
    print("FINAL_REPORT_PREVIEW:")
    print((state.get("reporter_output") or "")[:800])
    print()


def main():
    cases = [
        "每个渠道的订单、营收和转化率是多少",
        "请分析这个A/B实验结果",
        "请分析这个漏斗",
    ]
    for q in cases:
        run_case(q)


if __name__ == "__main__":
    main()
