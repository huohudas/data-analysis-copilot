from typing import Dict, Any
import pandas as pd

from app.tools.analysis_tools import analyze_sql_result, suggest_chart_spec


def run_analysis_agent(sql_agent_result: Dict[str, Any]) -> Dict[str, Any]:
    records = sql_agent_result.get("records", [])
    df = pd.DataFrame(records)

    analysis_result = analyze_sql_result(df)
    chart_spec = suggest_chart_spec(df)

    return {
        "user_query": sql_agent_result.get("user_query"),
        "analysis_agent_source": "pandas_numpy_analysis",
        "input_columns": list(df.columns),
        "row_count": len(df),
        "chart_spec": chart_spec,
        "analysis_result": analysis_result,
    }
