from app.graph.builder import build_graph


def main():
    graph = build_graph()

    cases = [
        "每个渠道的订单、营收和转化率是多少",
        "请分析这个A/B实验结果",
        "请分析这个漏斗，找出流失最大的环节",
    ]

    for q in cases:
        state = graph.invoke(
            {
                "session_id": "demo_user",
                "user_query": q,
                "retry_count": 0,
                "errors": [],
            }
        )

        print("=" * 100)
        print("QUERY:", q)
        print()
        print("[BUSINESS_CONTEXT]")
        print(state.get("business_context"))
        print()
        print("[FINAL_REPORT]")
        print(state.get("reporter_output"))
        print()


if __name__ == "__main__":
    main()
