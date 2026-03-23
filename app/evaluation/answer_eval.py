from typing import Dict, Any


def evaluate_answer_step(state: Dict[str, Any]) -> Dict[str, Any]:
    final_response = state.get("final_response", "")
    reporter_output = state.get("reporter_output", "")

    if not final_response or not reporter_output:
        return {
            "score": 0.0,
            "passed": False,
            "comment": "final_response 或 reporter_output 缺失。",
        }

    if len(reporter_output) < 80:
        return {
            "score": 0.4,
            "passed": False,
            "comment": "最终报告过短，信息密度不足。",
        }

    return {
        "score": 1.0,
        "passed": True,
        "comment": "最终回答与报告均存在，长度和结构基本正常。",
    }
