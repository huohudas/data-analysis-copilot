from pathlib import Path
import re
from typing import List, Dict


DOC_DIR = Path("app/rag/documents")

SYNONYM_MAP = {
    "a/b": ["ab", "实验", "显著性", "uplift", "对照组", "实验组", "ab_test"],
    "ab": ["a/b", "实验", "显著性", "uplift", "ab_test"],
    "实验": ["a/b", "ab", "显著性", "uplift", "实验组", "对照组"],
    "显著性": ["实验", "a/b", "ab", "p-value", "uplift"],
    "漏斗": ["转化", "流失", "步骤", "环节", "链路", "funnel"],
    "流失": ["漏斗", "转化", "步骤", "环节"],
    "环节": ["漏斗", "流失", "步骤"],
    "转化率": ["conversion_rate", "转化", "订单数", "用户数"],
    "schema": ["字段", "表", "结构", "schema"],
    "字段": ["schema", "表", "结构"],
}


def tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9_一-龥/.-]+", text.lower())


def expand_query_tokens(tokens: List[str]) -> List[str]:
    expanded = set(tokens)

    for token in list(tokens):
        if token in SYNONYM_MAP:
            expanded.update(SYNONYM_MAP[token])

    joined = " ".join(tokens)

    if "a/b" in joined or "ab" in joined or "实验" in joined:
        expanded.update(["显著性", "uplift", "实验组", "对照组"])
    if "漏斗" in joined or "流失" in joined:
        expanded.update(["转化", "步骤", "环节", "链路", "funnel"])
    if "转化率" in joined:
        expanded.update(["conversion_rate", "订单数", "用户数"])

    return list(expanded)


def score_document(query: str, text: str) -> int:
    q_tokens = expand_query_tokens(tokenize(query))
    doc_text = text.lower()
    d_tokens = set(tokenize(text))

    score = 0
    for token in q_tokens:
        if token in d_tokens:
            score += 2
        elif token in doc_text:
            score += 1
    return score


def load_documents() -> List[Dict]:
    docs = []

    if not DOC_DIR.exists():
        return docs

    for path in DOC_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        docs.append(
            {
                "title": path.name,
                "text": text,
            }
        )

    return docs


def retrieve_documents(query: str, top_k: int = 3) -> List[Dict]:
    docs = load_documents()
    scored = []

    for doc in docs:
        score = score_document(query, doc["text"])
        if score > 0:
            scored.append({**doc, "score": score})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def extract_key_lines(text: str, max_lines: int = 6) -> List[str]:
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        # markdown 标题去掉井号，保留文字
        line = re.sub(r"^#+\s*", "", line)

        # 普通行统一转成更好看的 bullets
        if not line.startswith("-") and not re.match(r"^\d+[.)、]\s*", line):
            line = f"- {line}"

        lines.append(line)

    return lines[:max_lines]


def build_business_context(query: str, top_k: int = 3) -> str:
    hits = retrieve_documents(query, top_k=top_k)

    if not hits:
        return "未检索到明显相关的业务知识文档。"

    parts = [f"共检索到 {len(hits)} 份相关业务文档：", ""]

    for idx, hit in enumerate(hits, start=1):
        parts.append(f"{idx}. 文档：{hit['title']}")
        parts.append(f"   相关度：{hit['score']}")
        parts.append("   关键信息：")

        key_lines = extract_key_lines(hit["text"], max_lines=6)
        for line in key_lines:
            if line.startswith("-"):
                parts.append(f"   {line}")
            else:
                parts.append(f"   - {line}")

        parts.append("")

    return "\n".join(parts).strip()
