import streamlit as st

from app.graph.builder import build_graph
from app.config import settings


st.set_page_config(page_title="DataMind Copilot", layout="wide")

st.title("DataMind Copilot")
st.caption("Multi-Agent 数据分析决策助手 Demo")

st.info(settings.startup_note())
st.write(f"当前 effective mode: **{settings.effective_mode}**")

default_query = "每个渠道的订单、营收和转化率是多少"
query = st.text_area("请输入分析问题", value=default_query, height=100)

if st.button("运行分析"):
    graph = build_graph()

    state = graph.invoke(
        {
            "session_id": "streamlit_user",
            "user_query": query,
            "retry_count": 0,
            "errors": [],
        }
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("任务类型")
        st.write(state.get("task_type"))

        st.subheader("执行计划")
        st.text(state.get("plan", ""))

        if state.get("sql_query"):
            st.subheader("SQL Query")
            st.code(state.get("sql_query", ""), language="sql")

        st.subheader("Reflection")
        st.json(state.get("reflection", {}))

    with col2:
        st.subheader("业务上下文")
        st.text(state.get("business_context", ""))

        st.subheader("分析结果")
        st.text(state.get("analysis_result", ""))

    st.subheader("最终报告")
    st.text(state.get("reporter_output", ""))
