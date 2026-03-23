from app.agents.planner import run_planner_agent


def main():
    cases = [
        "每个渠道的订单、营收和转化率是多少",
        "请分析这个A/B实验结果",
        "请分析这个漏斗",
        "2026-03-01 到 2026-03-05 每天的营收趋势如何",
    ]

    for q in cases:
        result = run_planner_agent(q)
        print("=" * 100)
        print("QUERY:", q)
        print("REQUESTED_MODE:", result.get("requested_mode"))
        print("EFFECTIVE_MODE:", result.get("effective_mode"))
        print("PROVIDER:", result.get("model_provider"))
        print("PLANNER_SOURCE:", result.get("planner_source"))
        print("STARTUP_NOTE:", result.get("startup_note"))
        print("TASK_TYPE:", result.get("task_type"))
        print("PLAN:", result.get("plan"))
        if result.get("fallback_reason"):
            print("FALLBACK_REASON:", result.get("fallback_reason"))
        print()

if __name__ == "__main__":
    main()
