# DataMind Copilot

面向企业分析场景的 Multi-Agent 数据分析决策助手。

## 项目简介

DataMind Copilot 是一个适合简历展示的 AI 数据分析 Agent 项目。  
系统支持自然语言分析请求、规则 / LLM 双轨 NL2SQL、Pandas / NumPy 二次分析、A/B Test、漏斗分析、RAG 业务知识检索、Memory 记忆管理、Reflection 复核、LangGraph 工作流编排与结构化报告输出。

当前版本定位为 **V2 MVP / 工程原型**：
- 已完成多 Agent 架构与主工作流联调
- 已完成规则模式与 LLM 模式接入
- LLM 在 Router、Planner、SQL Intent、Reflection 等节点已实际生效
- SQL 生成节点仍保留规则 fallback，以解决模型在聚合 SQL 上的稳定性问题

---

## 核心能力

### 1. Multi-Agent 架构
- Planner Agent
- RAG Agent
- SQL Agent
- Analysis Agent
- A/B Test Agent
- Funnel Agent
- Reflection Agent
- Reporter Agent

### 2. LangGraph 状态图编排
工作流核心链路：

用户问题  
→ Planner Agent  
→ RAG Agent  
→ 条件路由  
  - SQL Agent → Analysis Agent  
  - A/B Test Agent  
  - Funnel Agent  
→ Reflection Agent  
→ Reporter Agent

### 3. 规则 / 大模型双模式
- `rule` 模式：完全本地规则逻辑，保证稳定性
- `llm` 模式：启用大模型进行任务路由、规划、SQL Intent 生成与结果复核
- `fallback`：LLM 不可用、超时或生成错误 SQL 时，自动回退到规则逻辑

### 4. 数据分析能力
- 自然语言转 SQL
- DuckDB 查询执行
- Pandas / NumPy 趋势分析与异常波动检测
- A/B Test 显著性分析
- Funnel 漏斗流失分析

### 5. 上下文增强
- RAG 检索指标定义、实验规范、Schema 文档
- Working Memory 保存最近会话
- Semantic Memory 保存用户偏好

### 6. 评估与治理
- SQL 评估
- Analysis 评估
- Answer 评估
- Process 评估
- Reflection 复核

### 7. 最小可演示前端
- Streamlit Demo UI
- 展示任务类型、业务上下文、SQL、分析结果、最终报告

---

## 当前项目状态

### 已完成
- 多 Agent 架构与 LangGraph 编排
- 规则模式全链路稳定运行
- RAG / Memory / Evaluation / Streamlit 已接入
- LLM 模式下 Router、Planner、SQL Intent、Reflection 已验证生效
- SQL 节点具备 fallback 机制

### 当前已知限制
- LLM SQL Generator 在部分 SQL case 上会生成不稳定的聚合 SQL，因此会 fallback 到规则 SQL
- Reflection 在单独测试中偶发超时，但在完整图工作流中已成功跑通过
- 当前数据源仍为 demo CSV / DuckDB，本质是 MVP 原型，不是生产级系统

---

## 技术栈

- Python
- LangGraph
- DuckDB
- Pandas
- NumPy
- Streamlit
- Requests
- Python-dotenv

---

## 模型接入

当前支持两类模型提供商：

- GLM
  - 推荐模型：`glm-4.7`
- DeepSeek
  - 推荐模型：`deepseek-reasoner`

---

## 环境变量

复制环境变量模板：

```bash
cp .env.example .env
使用 GLM
APP_MODE=llm
MODEL_PROVIDER=glm
GLM_API_KEY=你的真实GLM_API_KEY
GLM_MODEL=glm-4.7
使用 DeepSeek
APP_MODE=llm
MODEL_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的真实DEEPSEEK_API_KEY
DEEPSEEK_MODEL=deepseek-reasoner

如果不配置 API Key，系统会自动回退到 rule 模式。

本地运行

安装依赖：

python -m pip install -r requirements.txt

启动主程序：

python -m app.main

启动前端：

python -m streamlit run ui/streamlit_app.py

运行评估：

python -m tests.test_evaluation

运行回归测试：

python -m tests.test_langgraph_workflow

运行 LLM 诊断：

python -m tests.test_fallback_diagnostics
python -m tests.test_llm_integration
项目亮点
不是单纯问答机器人，而是面向企业分析场景的多 Agent 决策助手
采用 LangGraph 状态图工作流，而不是简单顺序脚本
同时具备规则模式与大模型模式，兼顾可靠性与扩展性
SQL 查询之后还有 Pandas / NumPy 二次分析层
加入 RAG、Memory、Reflection、Evaluation，完整体现 AI 产品工程化能力
面向数据分析 / AIPM 场景设计，支持 SQL、实验分析、漏斗分析、结构化汇报输出

后续迭代方向
强化 LLM SQL Generator 的聚合 SQL 约束与后处理修正
接入真实数据库 / 数仓而非 demo CSV
引入语义层与指标口径中心
增加权限控制、日志追踪与可观测性
增加更完整的前端交互与图表可视化