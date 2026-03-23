from typing import Dict, Any


def evaluate_sql_step(state: Dict[str, Any]) -> Dict[str, Any]:
    task_type = state.get("task_type")
    sql_query = state.get("sql_query", "")
    records = state.get("sql_result_records", [])

    if task_type != "sql":
        return {
            "score": 1.0,
            "passed": True,
            "comment": "非 SQL 任务，跳过 SQL 评估。",
        }

    if not sql_query:
        return {
            "score": 0.0,
            "passed": False,
            "comment": "SQL 任务缺少 sql_query。",
        }

    normalized = sql_query.strip().lower()
    if not normalized.startswith("select"):
        return {
            "score": 0.0,
            "passed": False,
            "comment": "SQL 不是只读 SELECT 查询。",
        }

    if len(records) == 0:
        return {
            "score": 0.4,
            "passed": True,
            "comment": "SQL 已生成但结果为空，需要结合业务确认是否合理。",
        }

    return {
        "score": 1.0,
        "passed": True,
        "comment": "SQL 查询存在且返回结果正常。",
    }
