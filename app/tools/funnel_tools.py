import numpy as np
import pandas as pd


def run_funnel_tool(csv_path: str) -> str:
    df = pd.read_csv(csv_path).copy()

    lines = ["漏斗分析结果："]
    prev_users = None
    first_users = None

    step_rates = []
    drop_rates = []
    total_rates = []

    for i, row in df.iterrows():
        step = row["step"]
        users = row["users"]

        if i == 0:
            first_users = users
            lines.append(f"- {step}：{users} 用户，整体转化率 100.00%")
            total_rates.append(1.0)
        else:
            step_rate = users / prev_users if prev_users else 0
            total_rate = users / first_users if first_users else 0
            step_rates.append(step_rate)
            drop_rates.append(1 - step_rate)
            total_rates.append(total_rate)

            lines.append(
                f"- {step}：{users} 用户，环节转化率 {step_rate:.2%}，整体转化率 {total_rate:.2%}"
            )

        prev_users = users

    drops = []
    for i in range(1, len(df)):
        prev_row = df.iloc[i - 1]
        curr_row = df.iloc[i]
        drop_ratio = 1 - (curr_row["users"] / prev_row["users"])
        drops.append((f"{prev_row['step']} -> {curr_row['step']}", drop_ratio))

    biggest_drop = max(drops, key=lambda x: x[1])

    lines.append("")
    lines.append("Pandas/NumPy 二次分析：")
    if step_rates:
        lines.append(f"- 平均环节转化率：{np.mean(step_rates):.2%}")
        lines.append(f"- 中位数环节转化率：{np.median(step_rates):.2%}")
    if drop_rates:
        lines.append(f"- 平均环节流失率：{np.mean(drop_rates):.2%}")
        lines.append(f"- 最大环节流失率：{np.max(drop_rates):.2%}")
    lines.append(f"- 最终付费转化率：{total_rates[-1]:.2%}")
    lines.append(f"结论：流失最严重的环节是 {biggest_drop[0]}，流失率 {biggest_drop[1]:.2%}。")

    return "\n".join(lines)
