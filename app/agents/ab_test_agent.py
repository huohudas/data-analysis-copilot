from typing import Dict, Any

from app.tools.analysis_tools import ensure_demo_data
from app.tools.ab_test_tools import run_ab_test_tool


def run_ab_test_agent(user_query: str) -> Dict[str, Any]:
    paths = ensure_demo_data()
    analysis_result = run_ab_test_tool(paths["ab_test"])

    return {
        "user_query": user_query,
        "ab_test_agent_source": "rule_ab_test",
        "analysis_result": analysis_result,
        "chart_spec": {"chart_type": "bar", "x": "group"},
    }
