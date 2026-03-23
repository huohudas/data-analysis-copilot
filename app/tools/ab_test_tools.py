import math
import numpy as np
import pandas as pd


def two_proportion_z_test(conv_a: int, users_a: int, conv_b: int, users_b: int):
    p1 = conv_a / users_a
    p2 = conv_b / users_b
    pooled = (conv_a + conv_b) / (users_a + users_b)
    se = math.sqrt(pooled * (1 - pooled) * (1 / users_a + 1 / users_b))

    if se == 0:
        return 0.0, 1.0

    z = (p2 - p1) / se
    cdf = 0.5 * (1 + math.erf(abs(z) / math.sqrt(2)))
    p_value = 2 * (1 - cdf)

    return z, p_value


def run_ab_test_tool(csv_path: str) -> str:
    df = pd.read_csv(csv_path)

    a = df[df["group"] == "A"].iloc[0]
    b = df[df["group"] == "B"].iloc[0]

    a_conv = a["conversions"] / a["users"]
    b_conv = b["conversions"] / b["users"]

    uplift = (b_conv - a_conv) / a_conv if a_conv else 0.0
    z_stat, p_value = two_proportion_z_test(
        int(a["conversions"]),
        int(a["users"]),
        int(b["conversions"]),
        int(b["users"]),
    )

    significant = "显著" if p_value < 0.05 else "不显著"
    winner = "B" if b_conv > a_conv else "A"
    arr = np.array([a_conv, b_conv], dtype=float)

    return (
        "A/B Test 分析结果：\n"
        f"- A组：用户 {a['users']}，转化 {a['conversions']}，转化率 {a_conv:.4f}\n"
        f"- B组：用户 {b['users']}，转化 {b['conversions']}，转化率 {b_conv:.4f}\n"
        f"- z-stat：{z_stat:.4f}\n"
        f"- p-value：{p_value:.6f}\n"
        f"- uplift：{uplift:.2%}\n"
        f"- 平均转化率：{np.mean(arr):.4f}\n"
        f"- 转化率标准差：{np.std(arr):.4f}\n"
        f"- 结论：{winner} 组转化率更高，统计结果{significant}。"
    )
