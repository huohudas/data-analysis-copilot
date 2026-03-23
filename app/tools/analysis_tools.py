import os
import math
import numpy as np
import pandas as pd


def ensure_demo_data():
    os.makedirs("data", exist_ok=True)

    orders_path = "data/orders.csv"
    ab_path = "data/ab_test.csv"
    funnel_path = "data/funnel.csv"

    orders_df = pd.DataFrame(
        [
            {"date": "2026-03-01", "channel": "ads", "orders": 120, "revenue": 3600, "users": 1000},
            {"date": "2026-03-01", "channel": "seo", "orders": 80, "revenue": 2400, "users": 900},
            {"date": "2026-03-02", "channel": "ads", "orders": 150, "revenue": 4500, "users": 1200},
            {"date": "2026-03-02", "channel": "seo", "orders": 95, "revenue": 2850, "users": 980},
            {"date": "2026-03-03", "channel": "ads", "orders": 170, "revenue": 5100, "users": 1350},
            {"date": "2026-03-03", "channel": "seo", "orders": 110, "revenue": 3300, "users": 1050},
            {"date": "2026-03-04", "channel": "ads", "orders": 90, "revenue": 2700, "users": 1300},
            {"date": "2026-03-04", "channel": "seo", "orders": 130, "revenue": 3900, "users": 1100},
            {"date": "2026-03-05", "channel": "ads", "orders": 210, "revenue": 6300, "users": 1500},
            {"date": "2026-03-05", "channel": "seo", "orders": 125, "revenue": 3750, "users": 1080},
        ]
    )

    ab_df = pd.DataFrame(
        [
            {"group": "A", "users": 1000, "conversions": 120},
            {"group": "B", "users": 980, "conversions": 145},
        ]
    )

    funnel_df = pd.DataFrame(
        [
            {"step": "visit", "users": 5000},
            {"step": "signup", "users": 1800},
            {"step": "activate", "users": 900},
            {"step": "pay", "users": 300},
        ]
    )

    orders_df.to_csv(orders_path, index=False)
    ab_df.to_csv(ab_path, index=False)
    funnel_df.to_csv(funnel_path, index=False)

    return {
        "orders": orders_path,
        "ab_test": ab_path,
        "funnel": funnel_path,
    }


def summarize_numeric_series(name: str, values) -> str:
    arr = np.array(values, dtype=float)

    if len(arr) == 0:
        return f"{name} 无数据"

    return (
        f"{name}统计：均值 {np.mean(arr):.2f}，中位数 {np.median(arr):.2f}，"
        f"最大值 {np.max(arr):.2f}，最小值 {np.min(arr):.2f}，标准差 {np.std(arr):.2f}"
    )


def detect_outliers_by_zscore(values, threshold: float = 1.5):
    arr = np.array(values, dtype=float)

    if len(arr) < 3:
        return np.array([False] * len(arr))

    std = np.std(arr)
    if std == 0:
        return np.array([False] * len(arr))

    z_scores = (arr - np.mean(arr)) / std
    return np.abs(z_scores) >= threshold


def analyze_summary_result(df: pd.DataFrame) -> str:
    row = df.iloc[0]
    lines = ["分析结果："]

    has_orders = "total_orders" in df.columns
    has_revenue = "total_revenue" in df.columns
    has_users = "total_users" in df.columns
    has_conversion = "conversion_rate" in df.columns

    if has_orders:
        lines.append(f"- 总订单：{row['total_orders']}")
    if has_revenue:
        lines.append(f"- 总营收：{row['total_revenue']}")
    if has_users:
        lines.append(f"- 总用户：{row['total_users']}")
    if has_conversion:
        lines.append(f"- 总转化率：{row['conversion_rate']:.4f}")

    lines.append("")
    lines.append("Pandas/NumPy 二次分析：")

    if has_orders and has_revenue and row["total_orders"]:
        lines.append(f"- AOV：{row['total_revenue'] / row['total_orders']:.2f}")

    if has_users and has_revenue and row["total_users"]:
        lines.append(f"- ARPU近似：{row['total_revenue'] / row['total_users']:.2f}")

    lines.append("结论：当前为汇总分析，可继续结合分渠道或按天维度做更细分诊断。")
    return "\n".join(lines)


def analyze_channel_result(df: pd.DataFrame) -> str:
    df = df.copy()
    lines = ["分析结果：渠道维度汇总如下。"]

    has_orders = "total_orders" in df.columns
    has_revenue = "total_revenue" in df.columns
    has_users = "total_users" in df.columns
    has_conversion = "conversion_rate" in df.columns

    if has_revenue and df["total_revenue"].sum() != 0:
        df["revenue_share"] = df["total_revenue"] / df["total_revenue"].sum()
    else:
        df["revenue_share"] = 0.0

    if has_orders and df["total_orders"].sum() != 0:
        df["order_share"] = df["total_orders"] / df["total_orders"].sum()
    else:
        df["order_share"] = 0.0

    for _, row in df.iterrows():
        parts = [f"- {row['channel']}"]

        if has_orders:
            parts.append(f"订单 {row['total_orders']}")
        if has_revenue:
            parts.append(f"营收 {row['total_revenue']}")
        if has_users:
            parts.append(f"用户 {row['total_users']}")
        if has_conversion:
            parts.append(f"转化率 {row['conversion_rate']:.4f}")
        if has_revenue:
            parts.append(f"营收占比 {row['revenue_share']:.2%}")
        if has_orders:
            parts.append(f"订单占比 {row['order_share']:.2%}")

        lines.append("，".join(parts))

    lines.append("")
    lines.append("Pandas/NumPy 二次分析：")

    if has_revenue:
        top = df.loc[df["total_revenue"].idxmax()]
        lines.append(f"- 营收最高渠道：{top['channel']}（{top['total_revenue']}）")
        lines.append(f"- {summarize_numeric_series('营收', df['total_revenue'])}")

    if has_conversion:
        best = df.loc[df["conversion_rate"].idxmax()]
        worst = df.loc[df["conversion_rate"].idxmin()]
        lines.append(f"- 转化率最高渠道：{best['channel']}（{best['conversion_rate']:.4f}）")
        lines.append(f"- 转化率最低渠道：{worst['channel']}（{worst['conversion_rate']:.4f}）")

    if has_orders:
        lines.append(f"- {summarize_numeric_series('订单', df['total_orders'])}")

    return "\n".join(lines)


def analyze_daily_result(df: pd.DataFrame) -> str:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    lines = ["分析结果：按天趋势如下。"]

    has_orders = "total_orders" in df.columns
    has_revenue = "total_revenue" in df.columns
    has_users = "total_users" in df.columns
    has_conversion = "conversion_rate" in df.columns

    if has_orders:
        df["orders_growth"] = df["total_orders"].pct_change().fillna(0.0)
        df["order_outlier"] = detect_outliers_by_zscore(df["total_orders"].tolist())
    else:
        df["orders_growth"] = 0.0
        df["order_outlier"] = False

    if has_revenue:
        df["revenue_growth"] = df["total_revenue"].pct_change().fillna(0.0)
        df["revenue_outlier"] = detect_outliers_by_zscore(df["total_revenue"].tolist())
    else:
        df["revenue_growth"] = 0.0
        df["revenue_outlier"] = False

    for _, row in df.iterrows():
        parts = [f"- {row['date'].date()}"]

        if has_orders:
            parts.append(f"订单 {row['total_orders']}")
            parts.append(f"订单环比 {row['orders_growth']:.2%}")
        if has_revenue:
            parts.append(f"营收 {row['total_revenue']}")
            parts.append(f"营收环比 {row['revenue_growth']:.2%}")
        if has_users:
            parts.append(f"用户 {row['total_users']}")
        if has_conversion:
            parts.append(f"转化率 {row['conversion_rate']:.4f}")

        tags = []
        if has_orders and bool(row["order_outlier"]):
            tags.append("订单异常波动")
        if has_revenue and bool(row["revenue_outlier"]):
            tags.append("营收异常波动")

        text = "，".join(parts)
        if tags:
            text += f"（{'，'.join(tags)}）"

        lines.append(text)

    lines.append("")
    lines.append("Pandas/NumPy 二次分析：")

    if has_revenue:
        top_day = df.loc[df["total_revenue"].idxmax()]
        lines.append(f"- 营收最高日期：{top_day['date'].date()}（{top_day['total_revenue']}）")
        lines.append(f"- {summarize_numeric_series('每日营收', df['total_revenue'])}")

    if has_orders:
        lines.append(f"- {summarize_numeric_series('每日订单', df['total_orders'])}")

    return "\n".join(lines)


def analyze_daily_channel_result(df: pd.DataFrame) -> str:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "channel"]).reset_index(drop=True)

    lines = ["分析结果：按天按渠道结果如下。"]

    for date, group in df.groupby("date"):
        lines.append(f"- {date.date()}：")
        for _, row in group.iterrows():
            parts = [f"  - {row['channel']}"]
            if "total_orders" in df.columns:
                parts.append(f"订单 {row['total_orders']}")
            if "total_revenue" in df.columns:
                parts.append(f"营收 {row['total_revenue']}")
            if "conversion_rate" in df.columns:
                parts.append(f"转化率 {row['conversion_rate']:.4f}")
            lines.append("，".join(parts))

    lines.append("")
    lines.append("Pandas/NumPy 二次分析：")

    if "total_revenue" in df.columns:
        top = df.loc[df["total_revenue"].idxmax()]
        lines.append(f"- 单日单渠道最高营收：{top['date'].date()} / {top['channel']} / {top['total_revenue']}")

    return "\n".join(lines)


def analyze_sql_result(df: pd.DataFrame) -> str:
    if df.empty:
        return "分析结果：SQL 返回为空，没有可分析的数据。"

    if "date" in df.columns and "channel" in df.columns:
        return analyze_daily_channel_result(df)

    if "channel" in df.columns:
        return analyze_channel_result(df)

    if "date" in df.columns:
        return analyze_daily_result(df)

    return analyze_summary_result(df)


def suggest_chart_spec(df: pd.DataFrame) -> dict:
    cols = set(df.columns)

    if "date" in cols and "channel" in cols:
        return {"chart_type": "line", "x": "date", "series": "channel"}
    if "date" in cols:
        return {"chart_type": "line", "x": "date"}
    if "channel" in cols:
        return {"chart_type": "bar", "x": "channel"}

    return {"chart_type": "table"}
