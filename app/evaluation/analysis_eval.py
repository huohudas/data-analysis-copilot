from typing import Dict, Any


def evaluate_analysis_step(state: Dict[str, Any]) -> Dict[str, Any]:
    task_type = state.get("task_type", "")
    analysis_result = state.get("analysis_result", "")

    if not analysis_result or len(analysis_result.strip()) == 0:
        return {
            "score": 0.0,
            "passed": False,
            "comment": "analysis_result 为空。",
        }

    rules = {
        "sql": ["分析结果", "结论"],
        "ab_test": ["p-value", "结论"],
        "funnel": ["流失", "转化率"],
    }

    required = rules.get(task_type, [])
    hit_count = sum(1 for kw in required if kw in analysis_result)

    if not required:
        return {
            "score": 0.8,
            "passed": True,
            "comment": "未知任务类型，做基础通过处理。",
        }

    score = hit_count / len(required)
    passed = score >= 0.5

    return {
        "score": round(score, 2),
        "passed": passed,
        "comment": f"分析结果命中 {hit_count}/{len(required)} 个关键特征。",
    }
