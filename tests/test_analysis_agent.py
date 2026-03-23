from app.agents.sql_agent import run_sql_agent
from app.agents.analysis_agent import run_analysis_agent
from app.agents.rag_agent import run_rag_agent


def main():
    cases = [
        "每个渠道的订单、营收和转化率是多少",
        "2026-03-01 到 2026-03-05 每天的营收趋势如何",
        "营收最高的渠道是什么",
        "seo渠道每天的营收是多少",
    ]

    for q in cases:
        sql_result = run_sql_agent(q)
        analysis_result = run_analysis_agent(sql_result)

        print("=" * 100)
        print("QUERY:", q)
        print("SQL:", sql_result["sql"])
        print("CHART_SPEC:", analysis_result["chart_spec"])
        print("ANALYSIS_RESULT:")
        print(analysis_result["analysis_result"])
        print()

    rag_cases = [
        "请分析这个A/B实验结果，并给出显著性结论",
        "转化率是怎么定义的",
        "请分析这个漏斗，找出流失最大的环节",
    ]

    for q in rag_cases:
        rag_result = run_rag_agent(q)
        print("=" * 100)
        print("RAG QUERY:", q)
        print("HIT_COUNT:", rag_result["hit_count"])
        print("HITS:", [x["title"] for x in rag_result["hits"]])
        print("BUSINESS_CONTEXT:")
        print(rag_result["business_context"])
        print()


if __name__ == "__main__":
    main()
