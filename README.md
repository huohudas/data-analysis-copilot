# DataMind Copilot

面向企业分析场景的 Multi-Agent 数据分析决策助手。

## 项目简介

DataMind Copilot 是一个适合简历展示的 AI 数据分析 Agent 项目。  
系统支持自然语言分析请求、规则/LLM 双轨 NL2SQL、Pandas/NumPy 二次分析、A/B Test、漏斗分析、RAG 业务知识检索、Memory 记忆管理、Reflection 复核、LangGraph 工作流编排与结构化报告输出。

## 核心能力

- 多 Agent 架构
  - Planner Agent
  - RAG Agent
  - SQL Agent
  - Analysis Agent
  - A/B Test Agent
  - Funnel Agent
  - Reflection Agent
  - Reporter Agent

- LangGraph 状态图编排
  - planner
  - rag
  - sql / ab_test / funnel
  - reflection
  - reporter

- 规则 / 大模型双模式
  - rule 模式：完全本地规则逻辑
  - llm 模式：启用大模型进行任务规划、SQL 生成与结果复核
  - fallback：LLM 不可用或失败时自动回退规则逻辑

- 数据分析能力
  - 自然语言转 SQL
  - DuckDB 查询执行
  - Pandas / NumPy 趋势分析与异常波动检测
  - A/B Test 显著性分析
  - 漏斗流失分析

- 上下文增强
  - RAG 检索指标定义、实验规范、Schema 文档
  - Working Memory 保存最近会话
  - Semantic Memory 保存简单用户偏好

- 评估与治理
  - SQL 评估
  - Analysis 评估
  - Answer 评估
  - Process 评估
  - Reflection 复核

- 最小可演示前端
  - Streamlit Demo UI
  - 可直接展示任务类型、SQL、业务上下文、分析结果、最终报告

## 系统架构

用户问题  
→ Planner Agent  
→ RAG Agent  
→ 条件路由  
  - SQL Agent → Analysis Agent  
  - A/B Test Agent  
  - Funnel Agent  
→ Reflection Agent  
→ Reporter Agent

## 技术栈

- Python
- LangGraph
- DuckDB
- Pandas
- NumPy
- Streamlit
- Requests
- Python-dotenv

## 模型接入

当前支持两类模型提供商：

- GLM
  - 推荐模型：glm-4.7
- DeepSeek
  - 推荐模型：deepseek-reasoner
