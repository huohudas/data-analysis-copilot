import re
import duckdb
import pandas as pd


def get_schema() -> str:
    return """
表名: orders

字段:
- date: 日期，YYYY-MM-DD
- channel: 渠道，例如 ads / seo
- orders: 订单数
- revenue: 营收
- users: 用户数

指标:
- orders
- revenue
- users
- conversion_rate = orders / users
""".strip()


def normalize_query(user_query: str) -> str:
    return user_query.strip().lower()


def extract_dates(user_query: str):
    dates = re.findall(r"\d{4}-\d{2}-\d{2}", user_query)
    if len(dates) >= 2:
        return dates[0], dates[1]
    if len(dates) == 1:
        return dates[0], dates[0]
    return None, None


def extract_channel(user_query: str):
    q = normalize_query(user_query)

    if "ads" in q or "广告" in user_query:
        return "ads"
    if "seo" in q or "自然搜索" in user_query:
        return "seo"

    return None


def extract_limit(user_query: str):
    q = normalize_query(user_query)

    m = re.search(r"top\s*(\d+)", q)
    if m:
        return int(m.group(1))

    m2 = re.search(r"前\s*(\d+)", user_query)
    if m2:
        return int(m2.group(1))

    if "最高" in user_query or "top" in q:
        return 1

    return None


def detect_metrics(user_query: str):
    q = normalize_query(user_query)
    metrics = []

    if "订单" in user_query or "orders" in q:
        metrics.append("orders")
    if "营收" in user_query or "收入" in user_query or "revenue" in q:
        metrics.append("revenue")
    if "用户" in user_query or "users" in q:
        metrics.append("users")
    if "转化率" in user_query or "conversion" in q:
        metrics.append("conversion_rate")

    if not metrics:
        metrics = ["orders", "revenue", "users", "conversion_rate"]

    result = []
    for m in metrics:
        if m not in result:
            result.append(m)
    return result


def detect_analysis_type(user_query: str, explicit_channel=None):
    q = normalize_query(user_query)

    has_channel_word = ("渠道" in user_query) or ("channel" in q)
    has_date = any(k in user_query for k in ["每天", "每日", "按天", "日期", "趋势"]) or ("daily" in q) or ("date" in q)

    if explicit_channel and has_date:
        return "by_date"
    if explicit_channel and not has_date:
        return "summary"
    if has_channel_word and has_date:
        return "by_date_channel"
    if has_channel_word:
        return "by_channel"
    if has_date:
        return "by_date"
    return "summary"


def detect_sort_field(user_query: str, metrics):
    q = normalize_query(user_query)

    if ("营收" in user_query or "revenue" in q) and ("最高" in user_query or "top" in q or "排序" in user_query):
        return "total_revenue"
    if ("订单" in user_query or "orders" in q) and ("最高" in user_query or "top" in q or "排序" in user_query):
        return "total_orders"
    if ("用户" in user_query or "users" in q) and ("最高" in user_query or "top" in q or "排序" in user_query):
        return "total_users"
    if ("转化率" in user_query or "conversion" in q) and ("最高" in user_query or "top" in q or "排序" in user_query):
        return "conversion_rate"

    if "最高" in user_query or "top" in q:
        if "revenue" in metrics:
            return "total_revenue"
        if "orders" in metrics:
            return "total_orders"
        if "conversion_rate" in metrics:
            return "conversion_rate"

    return None


def parse_user_query_to_intent(user_query: str):
    channel = extract_channel(user_query)
    metrics = detect_metrics(user_query)
    analysis_type = detect_analysis_type(user_query, channel)
    start_date, end_date = extract_dates(user_query)
    limit = extract_limit(user_query)
    sort_by = detect_sort_field(user_query, metrics)

    return {
        "analysis_type": analysis_type,
        "metrics": metrics,
        "channel": channel,
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit,
        "sort_by": sort_by,
    }


def build_metric_sql_parts(metrics):
    parts = []

    if "orders" in metrics:
        parts.append("SUM(orders) AS total_orders")
    if "revenue" in metrics:
        parts.append("SUM(revenue) AS total_revenue")
    if "users" in metrics:
        parts.append("SUM(users) AS total_users")
    if "conversion_rate" in metrics:
        parts.append("ROUND(SUM(orders) * 1.0 / NULLIF(SUM(users), 0), 4) AS conversion_rate")

    return parts


def build_group_fields(analysis_type):
    if analysis_type == "by_channel":
        return ["channel"]
    if analysis_type == "by_date":
        return ["date"]
    if analysis_type == "by_date_channel":
        return ["date", "channel"]
    return []


def default_sort_field(metrics):
    if "revenue" in metrics:
        return "total_revenue"
    if "orders" in metrics:
        return "total_orders"
    if "users" in metrics:
        return "total_users"
    if "conversion_rate" in metrics:
        return "conversion_rate"
    return None


def build_where_clause(intent):
    conditions = []

    if intent.get("channel"):
        conditions.append(f"channel = '{intent['channel']}'")

    if intent.get("start_date") and intent.get("end_date"):
        if intent["start_date"] == intent["end_date"]:
            conditions.append(f"date = '{intent['start_date']}'")
        else:
            conditions.append(f"date BETWEEN '{intent['start_date']}' AND '{intent['end_date']}'")

    if not conditions:
        return ""

    return "WHERE " + " AND ".join(conditions)


def build_order_clause(intent, analysis_type):
    sort_by = intent.get("sort_by")
    if sort_by:
        return f"ORDER BY {sort_by} DESC"

    if analysis_type == "by_date":
        return "ORDER BY date"
    if analysis_type == "by_date_channel":
        return "ORDER BY date, channel"
    if analysis_type == "by_channel":
        field = default_sort_field(intent["metrics"]) or "total_revenue"
        return f"ORDER BY {field} DESC"

    return ""


def build_limit_clause(intent):
    if intent.get("limit"):
        return f"LIMIT {intent['limit']}"
    return ""


def build_sql_from_intent(intent):
    analysis_type = intent["analysis_type"]
    metrics = intent["metrics"]

    group_fields = build_group_fields(analysis_type)
    metric_parts = build_metric_sql_parts(metrics)
    where_clause = build_where_clause(intent)
    order_clause = build_order_clause(intent, analysis_type)
    limit_clause = build_limit_clause(intent)

    select_parts = []
    if group_fields:
        select_parts.extend(group_fields)
    select_parts.extend(metric_parts)

    sql = "SELECT\n    " + ",\n    ".join(select_parts) + "\nFROM orders\n"

    if where_clause:
        sql += where_clause + "\n"

    if group_fields:
        sql += "GROUP BY " + ", ".join(group_fields) + "\n"

    if order_clause:
        sql += order_clause + "\n"

    if limit_clause:
        sql += limit_clause + "\n"

    return sql.strip()


def generate_sql_rule(user_query: str):
    intent = parse_user_query_to_intent(user_query)
    sql = build_sql_from_intent(intent)
    return intent, sql


def is_safe_select_sql(sql: str) -> bool:
    if not sql or not isinstance(sql, str):
        return False

    normalized = sql.strip().lower()

    if not normalized.startswith("select"):
        return False

    banned_keywords = [
        "insert ", "update ", "delete ", "drop ", "alter ",
        "truncate ", "create ", "replace ", "attach ", "copy "
    ]

    for keyword in banned_keywords:
        if keyword in normalized:
            return False

    if " from orders" not in normalized and "\nfrom orders" not in normalized:
        return False

    return True


def validate_sql_or_raise(sql: str):
    if not is_safe_select_sql(sql):
        raise ValueError("SQL 未通过只读安全校验")
    return True


def run_sql_tool(sql: str, csv_path: str) -> pd.DataFrame:
    con = duckdb.connect()
    con.execute(f"CREATE OR REPLACE TABLE orders AS SELECT * FROM read_csv_auto('{csv_path}')")
    df = con.execute(sql).df()
    con.close()
    return df
