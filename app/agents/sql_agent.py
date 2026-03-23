from typing import Dict, Any
import json

from app.config import settings
from app.llm.client import call_json_llm
from app.llm.prompts import SQL_INTENT_PROMPT, SQL_GENERATOR_PROMPT
from app.tools.sql_tools import (
    get_schema,
    generate_sql_rule,
    validate_sql_or_raise,
    run_sql_tool,
)
from app.tools.analysis_tools import ensure_demo_data


def try_llm_sql(user_query: str, business_context: str, schema: str):
    intent = call_json_llm(
        system_prompt="你是一个严谨的数据分析 SQL 规划器，只输出 JSON。",
        user_prompt=SQL_INTENT_PROMPT.format(
            schema=schema,
            business_context=business_context,
            user_query=user_query,
        ),
    )

    sql_resp = call_json_llm(
        system_prompt="你是一个严谨的 DuckDB SQL 生成器，只输出 JSON。",
        user_prompt=SQL_GENERATOR_PROMPT.format(
            schema=schema,
            intent_json=json.dumps(intent, ensure_ascii=False),
        ),
    )

    sql = str(sql_resp.get("sql", "")).strip()
    validate_sql_or_raise(sql)
    return intent, sql


def run_sql_agent(user_query: str, business_context: str = "") -> Dict[str, Any]:
    paths = ensure_demo_data()
    schema = get_schema()

    if settings.llm_enabled:
        try:
            intent, sql = try_llm_sql(user_query, business_context, schema)
            df = run_sql_tool(sql, paths["orders"])
            return {
                "user_query": user_query,
                "sql_agent_source": "llm_sql",
                "schema": schema,
                "intent": intent,
                "sql": sql,
                "row_count": len(df),
                "columns": list(df.columns),
                "records": df.to_dict(orient="records"),
            }
        except Exception as e:
            intent, sql = generate_sql_rule(user_query)
            validate_sql_or_raise(sql)
            df = run_sql_tool(sql, paths["orders"])
            return {
                "user_query": user_query,
                "sql_agent_source": "rule_fallback",
                "schema": schema,
                "intent": intent,
                "sql": sql,
                "row_count": len(df),
                "columns": list(df.columns),
                "records": df.to_dict(orient="records"),
                "fallback_reason": f"LLM SQL 失败，已回退规则 SQL：{e}",
            }

    intent, sql = generate_sql_rule(user_query)
    validate_sql_or_raise(sql)
    df = run_sql_tool(sql, paths["orders"])

    return {
        "user_query": user_query,
        "sql_agent_source": "rule_nl2sql",
        "schema": schema,
        "intent": intent,
        "sql": sql,
        "row_count": len(df),
        "columns": list(df.columns),
        "records": df.to_dict(orient="records"),
    }
