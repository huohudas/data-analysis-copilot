from app.agents.rag_agent import run_rag_agent


def main():
    cases = [
        "请分析这个A/B实验结果，并给出显著性结论",
        "转化率是怎么定义的",
        "orders 表里有哪些字段",
        "请分析这个漏斗，找出流失最大的环节",
    ]

    for q in cases:
        result = run_rag_agent(q)
        print("=" * 100)
        print("QUERY:", q)
        print("RAG_SOURCE:", result["rag_source"])
        print("HIT_COUNT:", result["hit_count"])
        print("HITS:")
        for item in result["hits"]:
            print(" -", item["title"], "| score =", item["score"])
        print("BUSINESS_CONTEXT:")
        print(result["business_context"])
        print()


if __name__ == "__main__":
    main()
