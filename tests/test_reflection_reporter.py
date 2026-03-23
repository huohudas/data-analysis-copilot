from app.agents.planner import run_planner_agent
from app.agents.rag_agent import run_rag_agent
from app.agents.sql_agent import run_sql_agent
from app.agents.analysis_agent import run_analysis_agent
from app.agents.reflection_agent import run_reflection_agent
from app.agents.reporter import run_reporter_agent


def run_sql_chain(query: str):
    planner_result = run_planner_agent(query)
    rag_result = run_rag_agent(query)
    sql_result = run_sql_agent(query)
    analysis_result = run_analysis_agent(sql_result)
    reflection_result = run_reflection_agent(
        user_query=query,
        task_type=planner_result["task_type"],
        analysis_result=analysis_result["analysis_result"],
    )
    reporter_result = run_reporter_agent(
        user_query=query,
        task_type=planner_result["task_type"],
        plan=planner_result["plan"],
        business_context=rag_result["business_context"],
        analysis_result=analysis_result["analysis_result"],
        reflection_result=reflection_result,
    )

    print("=" * 100)
    print("QUERY:", query)
    print("TASK_TYPE:", planner_result["task_type"])
    print("REFLECTION_PASSED:", reflection_result["passed"])
    print("REFLECTION_COMMENT:", reflection_result["review_comment"])
    print("FINAL_REPORT:")
    print(reporter_result["final_report"])
    print()


def run_rag_check(query: str):
    rag_result = run_rag_agent(query)
    print("=" * 100)
    print("RAG QUERY:", query)
    print("HIT_COUNT:", rag_result["hit_count"])
    print("HITS:", [x["title"] for x in rag_result["hits"]])
    print("BUSINESS_CONTEXT:")
    print(rag_result["business_context"])
    print()


def main():
    run_sql_chain("每个渠道的订单、营收和转化率是多少")
    run_sql_chain("2026-03-01 到 2026-03-05 每天的营收趋势如何")

    run_rag_check("请分析这个漏斗，找出流失最大的环节")


if __name__ == "__main__":
    main()
