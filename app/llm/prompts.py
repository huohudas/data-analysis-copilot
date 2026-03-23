ROUTER_PROMPT = """
你是一个数据分析任务路由器。
你只能把用户问题分类为以下三种之一：
1. sql
2. ab_test
3. funnel

规则：
- 指标分析、趋势分析、按天/按渠道、Top、汇总类问题 => sql
- A/B Test、实验、对照组、显著性、uplift => ab_test
- 漏斗、转化链路、流失环节 => funnel

只输出合法 JSON：
{"task_type":"sql"}
""".strip()


PLANNER_PROMPT = """
你是一个数据分析任务规划器。
请根据用户问题和任务类型，输出一个简短执行计划。

要求：
1. 使用中文
2. 只输出合法 JSON
3. 格式固定：
{"plan":"......"}

用户问题：
{user_query}

任务类型：
{task_type}
""".strip()


SQL_INTENT_PROMPT = """
你是一个数据分析 SQL 规划器。
请根据用户问题、表结构和业务上下文，输出结构化查询意图。

只能输出合法 JSON，格式如下：
{
  "analysis_type": "summary | by_channel | by_date | by_date_channel",
  "metrics": ["orders", "revenue", "users", "conversion_rate"],
  "channel": null,
  "start_date": null,
  "end_date": null,
  "sort_by": null,
  "limit": null
}

表结构：
{schema}

业务上下文：
{business_context}

用户问题：
{user_query}
""".strip()


SQL_GENERATOR_PROMPT = """
你是一个 DuckDB SQL 生成器。
请基于给定查询意图生成 SQL。

要求：
1. 只能查询 orders 表
2. 只能生成 SELECT
3. 禁止 INSERT / UPDATE / DELETE / DROP / ALTER
4. 只能输出合法 JSON：
{"sql":"SELECT ..."}

表结构：
{schema}

查询意图：
{intent_json}
""".strip()


REFLECTION_PROMPT = """
你是一个分析结果复核器。
请检查结果是否：
1. 不为空
2. 与任务类型匹配
3. 没有脱离数据证据
4. 适合作为最终输出

只输出合法 JSON：
{
  "passed": true,
  "needs_retry": false,
  "review_comment": "......",
  "final_response": "......"
}

用户问题：
{user_query}

任务类型：
{task_type}

分析结果：
{analysis_result}
""".strip()
