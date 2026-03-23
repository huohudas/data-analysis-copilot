from typing import Dict, Any

from app.tools.analysis_tools import ensure_demo_data
from app.tools.funnel_tools import run_funnel_tool


def run_funnel_agent(user_query: str) -> Dict[str, Any]:
    paths = ensure_demo_data()
    analysis_result = run_funnel_tool(paths["funnel"])

    return {
        "user_query": user_query,
        "funnel_agent_source": "rule_funnel",
        "analysis_result": analysis_result,
        "chart_spec": {"chart_type": "funnel", "x": "step", "y": "users"},
    }
