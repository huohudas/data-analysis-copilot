from app.llm.prompts import (
    PLANNER_PROMPT,
    SQL_INTENT_PROMPT,
    SQL_GENERATOR_PROMPT,
    REFLECTION_PROMPT,
)
from app.llm.prompt_utils import render_prompt


def main():
    planner = render_prompt(
        PLANNER_PROMPT,
        user_query="每个渠道的订单、营收和转化率是多少",
        task_type="sql",
    )
    sql_intent = render_prompt(
        SQL_INTENT_PROMPT,
        schema="orders(date, channel, orders, revenue, users)",
        business_context="conversion_rate = orders / users",
        user_query="每个渠道的订单、营收和转化率是多少",
    )
    sql_generator = render_prompt(
        SQL_GENERATOR_PROMPT,
        schema="orders(date, channel, orders, revenue, users)",
        intent_json='{"analysis_type":"by_channel","metrics":["orders","revenue","conversion_rate"]}',
    )
    reflection = render_prompt(
        REFLECTION_PROMPT,
        user_query="每个渠道的订单、营收和转化率是多少",
        task_type="sql",
        analysis_result="分析结果：渠道维度汇总如下。\n- ads ...\n- seo ...",
    )

    print("=" * 100)
    print("PLANNER PROMPT:")
    print(planner)
    print()

    print("=" * 100)
    print("SQL INTENT PROMPT:")
    print(sql_intent)
    print()

    print("=" * 100)
    print("SQL GENERATOR PROMPT:")
    print(sql_generator)
    print()

    print("=" * 100)
    print("REFLECTION PROMPT:")
    print(reflection)
    print()

    print("Prompt rendering passed.")
if __name__ == "__main__":
    main()
