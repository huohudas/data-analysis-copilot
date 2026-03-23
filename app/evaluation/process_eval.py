from typing import Dict, Any


def evaluate_process_step(state: Dict[str, Any]) -> Dict[str, Any]:
    task_type = state.get("task_type")
    plan = state.get("plan", "")
    reflection = state.get("reflection", {})
    business_context = state.get("business_context", "")

    score = 0.0
    checks = 4
    comments = []

    if task_type in {"sql", "ab_test", "funnel"}:
        score += 1
        comments.append("任务路由有效。")
    else:
        comments.append("任务路由无效。")

    if plan:
        score += 1
        comments.append("存在执行计划。")
    else:
        comments.append("缺少执行计划。")

    if reflection:
        score += 1
        comments.append("存在 reflection 结果。")
    else:
        comments.append("缺少 reflection 结果。")

    if business_context:
        score += 1
        comments.append("存在业务上下文。")
    else:
        comments.append("缺少业务上下文。")

    final_score = round(score / checks, 2)

    return {
        "score": final_score,
        "passed": final_score >= 0.75,
        "comment": " ".join(comments),
    }
