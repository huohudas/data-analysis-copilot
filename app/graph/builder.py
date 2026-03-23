from typing import Literal

from langgraph.graph import StateGraph, START, END

from app.state import GraphState
from app.agents.planner import run_planner_agent
from app.agents.rag_agent import run_rag_agent
from app.agents.sql_agent import run_sql_agent
from app.agents.analysis_agent import run_analysis_agent
from app.agents.ab_test_agent import run_ab_test_agent
from app.agents.funnel_agent import run_funnel_agent
from app.agents.reflection_agent import run_reflection_agent
from app.agents.reporter import run_reporter_agent
from app.memory.short_term import append_working_memory
from app.memory.long_term import update_preferences_from_query


def planner_node(state: GraphState) -> dict:
    result = run_planner_agent(state["user_query"])
    return {
        "task_type": result["task_type"],
        "plan": result["plan"],
    }


def rag_node(state: GraphState) -> dict:
    result = run_rag_agent(state["user_query"])
    return {
        "rag_hits": result["hits"],
        "business_context": result["business_context"],
    }


def route_after_planner(state: GraphState) -> Literal["sql_branch", "ab_branch", "funnel_branch"]:
    task_type = state.get("task_type", "sql")
    if task_type == "ab_test":
        return "ab_branch"
    if task_type == "funnel":
        return "funnel_branch"
    return "sql_branch"


def sql_node(state: GraphState) -> dict:
    sql_result = run_sql_agent(
        state["user_query"],
        business_context=state.get("business_context", ""),
    )
    payload = {
        "sql_query": sql_result["sql"],
        "sql_result_records": sql_result["records"],
        "sql_source": sql_result["sql_agent_source"],
    }
    if sql_result.get("fallback_reason"):
        payload["sql_fallback_reason"] = sql_result["fallback_reason"]
    return payload


def analysis_node(state: GraphState) -> dict:
    sql_agent_result = {
        "user_query": state["user_query"],
        "records": state["sql_result_records"],
    }
    result = run_analysis_agent(sql_agent_result)
    return {
        "analysis_result": result["analysis_result"],
        "chart_spec": result["chart_spec"],
    }


def ab_test_node(state: GraphState) -> dict:
    result = run_ab_test_agent(state["user_query"])
    return {
        "analysis_result": result["analysis_result"],
        "chart_spec": result["chart_spec"],
    }


def funnel_node(state: GraphState) -> dict:
    result = run_funnel_agent(state["user_query"])
    return {
        "analysis_result": result["analysis_result"],
        "chart_spec": result["chart_spec"],
    }


def reflection_node(state: GraphState) -> dict:
    result = run_reflection_agent(
        user_query=state["user_query"],
        task_type=state["task_type"],
        analysis_result=state["analysis_result"],
    )
    return {
        "reflection": {
            "source": result["reflection_source"],
            "passed": result["passed"],
            "needs_retry": result["needs_retry"],
            "review_comment": result["review_comment"],
        },
        "final_response": result["final_response"],
    }


def reporter_node(state: GraphState) -> dict:
    reflection = state.get("reflection", {})
    result = run_reporter_agent(
        user_query=state["user_query"],
        task_type=state["task_type"],
        plan=state.get("plan", ""),
        business_context=state.get("business_context", "未提供业务上下文。"),
        analysis_result=state.get("analysis_result", ""),
        reflection_result={
            "review_comment": reflection.get("review_comment", "无"),
            "final_response": state.get("final_response", ""),
        },
    )

    update_preferences_from_query(state["user_query"])
    append_working_memory(
        session_id=state.get("session_id", "demo_user"),
        record={
            "user_query": state["user_query"],
            "task_type": state["task_type"],
            "final_response": result["final_response"],
        },
    )

    return {
        "reporter_output": result["final_report"],
        "final_response": result["final_response"],
    }


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("planner", planner_node)
    builder.add_node("rag", rag_node)
    builder.add_node("sql", sql_node)
    builder.add_node("analysis", analysis_node)
    builder.add_node("ab_test", ab_test_node)
    builder.add_node("funnel", funnel_node)
    builder.add_node("reflection", reflection_node)
    builder.add_node("reporter", reporter_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "rag")

    builder.add_conditional_edges(
        "rag",
        route_after_planner,
        {
            "sql_branch": "sql",
            "ab_branch": "ab_test",
            "funnel_branch": "funnel",
        },
    )

    builder.add_edge("sql", "analysis")
    builder.add_edge("analysis", "reflection")
    builder.add_edge("ab_test", "reflection")
    builder.add_edge("funnel", "reflection")
    builder.add_edge("reflection", "reporter")
    builder.add_edge("reporter", END)

    return builder.compile()
