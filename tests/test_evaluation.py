from app.graph.builder import build_graph
from app.evaluation.sql_eval import evaluate_sql_step
from app.evaluation.analysis_eval import evaluate_analysis_step
from app.evaluation.answer_eval import evaluate_answer_step
from app.evaluation.process_eval import evaluate_process_step


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
                "session_id": "eval_user",
                "user_query": q,
                "retry_count": 0,
                "errors": [],
            }
        )

        sql_eval = evaluate_sql_step(state)
        analysis_eval = evaluate_analysis_step(state)
        answer_eval = evaluate_answer_step(state)
        process_eval = evaluate_process_step(state)

        print("=" * 100)
        print("QUERY:", q)
        print("TASK_TYPE:", state.get("task_type"))
        print("SQL_EVAL:", sql_eval)
        print("ANALYSIS_EVAL:", analysis_eval)
        print("ANSWER_EVAL:", answer_eval)
        print("PROCESS_EVAL:", process_eval)
        print()

if __name__ == "__main__":
    main()
