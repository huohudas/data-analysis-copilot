from typing import Dict, Any

from app.rag.retriever import retrieve_documents, build_business_context


def run_rag_agent(user_query: str, top_k: int = 3) -> Dict[str, Any]:
    hits = retrieve_documents(user_query, top_k=top_k)
    context = build_business_context(user_query, top_k=top_k)

    return {
        "user_query": user_query,
        "rag_source": "local_docs_keyword_retrieval",
        "hit_count": len(hits),
        "hits": [
            {
                "title": hit["title"],
                "score": hit["score"],
                "snippet": hit["text"][:200].replace("\n", " "),
            }
            for hit in hits
        ],
        "business_context": context,
    }
