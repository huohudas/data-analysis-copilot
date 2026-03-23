from app.agents.sql_agent import run_sql_agent


def main():
    cases = [
        "每个渠道的订单、营收和转化率是多少",
        "ads渠道的营收是多少",
        "2026-03-01 到 2026-03-05 每天的营收趋势如何",
        "营收最高的渠道是什么",
        "seo渠道每天的营收是多少",
    ]

    for q in cases:
        result = run_sql_agent(q)
        print("=" * 100)
        print("QUERY:", q)
        print("SQL_AGENT_SOURCE:", result["sql_agent_source"])
        print("INTENT:", result["intent"])
        print("SQL:")
        print(result["sql"])
        print("ROW_COUNT:", result["row_count"])
        print("COLUMNS:", result["columns"])
        print("RECORDS_PREVIEW:", result["records"][:3])
        print()


if __name__ == "__main__":
    main()
