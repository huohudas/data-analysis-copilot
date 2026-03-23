from app.tools.sql_tools import parse_user_query, generate_sql


def run_case(query: str):
    intent = parse_user_query(query)
    sql = generate_sql(query)

    print("=" * 80)
    print("QUERY:", query)
    print("INTENT:", intent)
    print("SQL:")
    print(sql)
    print()


def main():
    cases = [
        "每个渠道的订单、营收和转化率是多少",
        "每天的订单和营收趋势如何",
        "ads渠道的营收是多少",
        "2026-03-01 到 2026-03-05 每天的营收趋势如何",
        "按天按渠道看订单和营收",
        "营收最高的渠道是什么",
        "top 1 channel by revenue",
        "2026-03-03 的总订单和转化率是多少",
        "seo渠道每天的营收是多少",
    ]

    for q in cases:
        run_case(q)


if __name__ == "__main__":
    main()
