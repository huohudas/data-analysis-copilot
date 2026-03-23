from typing import TypedDict, Any, Dict, List


class GraphState(TypedDict, total=False):
    session_id: str
    user_query: str

    task_type: str
    selected_tool: str
    plan: str

    rag_hits: List[Dict[str, Any]]
    business_context: str

    sql_query: str
    sql_source: str
    sql_fallback_reason: str
    sql_result_records: List[Dict[str, Any]]

    analysis_result: str
    chart_spec: Dict[str, Any]

    reporter_output: str
    reflection: Dict[str, Any]
    final_response: str

    retry_count: int
    errors: List[str]