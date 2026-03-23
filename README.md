# DataMind Copilot

面向企业分析场景的 Multi-Agent 数据分析决策助手。

## 项目简介

DataMind Copilot 是一个适合简历展示的 AI 数据分析 Agent 项目，目标是把自然语言分析请求转化为完整、可执行、可解释的数据分析流程，而不是只做一个简单问答机器人。

系统当前支持以下能力：

- 自然语言分析请求理解
- Multi-Agent 任务拆解与协作
- 规则 / LLM 双轨 NL2SQL
- Pandas / NumPy 二次分析
- A/B Test 显著性分析
- Funnel 漏斗分析
- RAG 业务知识检索
- Memory 记忆管理
- Reflection 结果复核
- LangGraph 状态图编排
- Streamlit 可演示前端
- Evaluation 评估闭环

当前版本定位为 **V2 MVP / 工程原型**：

- 已完成多 Agent 架构与主工作流联调
- 已完成规则模式与 LLM 模式接入
- 已具备可演示前端与完整分析链路
- 已具备 fallback 机制与评估模块
- 已可作为 Agent 项目写入简历

## 项目目标

传统 BI 工具通常要求使用者熟悉 SQL、指标口径和分析流程，而 DataMind Copilot 的目标是：

> 让用户直接通过自然语言提出分析问题，系统自动理解任务、检索业务上下文、执行分析并生成结构化结论。

例如用户可以直接提问：

- 每个渠道的订单、营收和转化率是多少？
- 2026-03-01 到 2026-03-05 每天的营收趋势如何？
- 请分析这个 A/B 实验结果
- 请分析这个漏斗，找出流失最大的环节

## 核心能力

### 1. Multi-Agent 架构

项目将系统拆分为多个职责清晰的 Agent：

- **Planner Agent**
  - 识别问题类型
  - 生成执行计划
  - 决定后续应该走 SQL / A/B Test / Funnel 分支

- **RAG Agent**
  - 检索业务知识文档
  - 提供指标定义、实验规范、Schema、分析 Playbook 等上下文

- **SQL Agent**
  - 解析自然语言分析意图
  - 生成 SQL
  - 执行 SQL 并返回结构化结果
  - 在 LLM SQL 失败时回退到规则 SQL

- **Analysis Agent**
  - 对 SQL 结果做 Pandas / NumPy 二次分析
  - 输出趋势、占比、异常波动、关键结论

- **A/B Test Agent**
  - 输出 uplift、z-stat、p-value、显著性判断
  - 给出实验结果解释

- **Funnel Agent**
  - 计算每一步转化率、整体转化率、流失率
  - 找出最大流失环节

- **Reflection Agent**
  - 检查分析结果是否完整
  - 判断结果是否与任务类型匹配
  - 作为质量复核节点

- **Reporter Agent**
  - 把业务上下文、分析结果、复核意见整合成结构化报告

### 2. LangGraph 状态图工作流

本项目基于 LangGraph 构建状态图工作流，而不是使用简单顺序脚本。

核心流程如下：

用户问题  
→ Planner Agent  
→ RAG Agent  
→ 条件路由  
→ SQL Agent → Analysis Agent  
→ 或 A/B Test Agent  
→ 或 Funnel Agent  
→ Reflection Agent  
→ Reporter Agent

这种设计的好处是：

- 支持条件分支
- 支持 fallback
- 支持统一 state 管理
- 支持后续加入重试、人工审核、更多工具节点
- 更符合真实 Agent 系统工程模式

### 3. 规则模式与 LLM 模式

系统支持两种运行模式：

#### rule 模式
完全依赖本地规则逻辑：

- 路由由规则判断
- SQL 由规则生成
- Reflection 由规则复核

优点：

- 稳定
- 无需 API
- 成本低
- 适合本地开发与回归测试

#### llm 模式
启用大模型增强能力：

- LLM Router：任务分类
- LLM Planner：任务规划
- LLM SQL Intent：结构化分析意图抽取
- LLM SQL Generator：SQL 生成
- LLM Reflection：结果复核

#### fallback 机制
为了保证系统稳定性，项目实现了 fallback 机制：

- 如果 LLM 不可用，则自动退回规则模式
- 如果 LLM SQL 生成失败，则回退规则 SQL
- 如果 LLM Reflection 超时或解析失败，则回退规则 Reflection

这使得系统即使在大模型输出不稳定时，仍能完成任务。

### 4. 数据分析能力

#### SQL 指标分析

支持：

- 汇总分析
- 按渠道分析
- 按天分析
- 按天按渠道分析
- Top 渠道分析
- 条件过滤
- 时间区间过滤

#### Python 二次分析

通过 Pandas / NumPy 对 SQL 结果做进一步处理，例如：

- 渠道占比
- 环比变化
- 最高 / 最低表现项
- 基本统计量
- 简单异常波动检测

#### A/B Test 分析

支持：

- A 组 / B 组转化率计算
- uplift 计算
- z-stat 计算
- p-value 计算
- 显著性判断
- 业务结论输出

#### Funnel 分析

支持：

- 各步骤环节转化率
- 整体转化率
- 平均环节流失率
- 最大环节流失率
- 最大流失点定位

## RAG 与上下文增强

项目内置本地业务知识文档，并通过 RAG Agent 在分析前进行上下文检索。

当前知识文档包括：

- `metric_definitions.md`
- `experiment_guideline.md`
- `schema_reference.md`
- `analysis_playbook.md`

RAG 的作用：

- 对齐指标口径
- 对齐实验规范
- 提供 schema 上下文
- 提升分析结果可解释性
- 减少脱离业务语义的错误分析

## Memory 记忆管理

项目实现了两类记忆：

### Working Memory

用于保存最近几次会话结果，例如：

- 最近提问
- 最近输出
- 最近任务类型

### Semantic Memory

用于保存长期偏好，例如：

- 默认渠道偏好
- 报告简洁版 / 详细版偏好

## Evaluation 评估闭环

项目加入了独立评估模块，覆盖四类评估：

### SQL Eval

检查：

- SQL 是否存在
- SQL 是否只读
- SQL 是否返回结果

### Analysis Eval

检查：

- 分析结果是否包含关键分析要素
- 是否与任务类型匹配

### Answer Eval

检查：

- 最终回答是否存在
- 最终报告是否完整
- 文本长度和结构是否合理

### Process Eval

检查：

- 是否存在 task_type
- 是否存在 plan
- 是否存在 reflection
- 是否存在 business_context

这使得项目不只是能跑，而是有基本的质量评估能力。

## 最小可演示前端

项目提供一个基于 Streamlit 的 Demo UI，可以展示：

- 当前模式
- 用户问题输入
- 任务类型
- 执行计划
- 业务上下文
- SQL Query
- Reflection 结果
- 分析结果
- 最终报告

这使得项目不仅能在终端运行，也适合截图、演示和 GitHub 展示。

## 技术栈

- Python
- LangGraph
- DuckDB
- Pandas
- NumPy
- Streamlit
- Requests
- python-dotenv

## 项目结构

```text
data-analysis-copilot/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── state.py
│   ├── graph/
│   │   └── builder.py
│   ├── agents/
│   │   ├── planner.py
│   │   ├── rag_agent.py
│   │   ├── sql_agent.py
│   │   ├── analysis_agent.py
│   │   ├── ab_test_agent.py
│   │   ├── funnel_agent.py
│   │   ├── reflection_agent.py
│   │   └── reporter.py
│   ├── tools/
│   │   ├── sql_tools.py
│   │   ├── analysis_tools.py
│   │   ├── ab_test_tools.py
│   │   └── funnel_tools.py
│   ├── llm/
│   │   ├── client.py
│   │   ├── prompts.py
│   │   └── prompt_utils.py
│   ├── rag/
│   │   ├── retriever.py
│   │   └── documents/
│   ├── memory/
│   │   ├── short_term.py
│   │   └── long_term.py
│   └── evaluation/
│       ├── sql_eval.py
│       ├── analysis_eval.py
│       ├── answer_eval.py
│       └── process_eval.py
├── data/
├── tests/
├── ui/
├── outputs/
├── README.md
├── requirements.txt
├── .env
└── .env.example
```

## 模型接入

当前支持两类模型提供商：

- **GLM**
  - 推荐模型：`glm-4.7`

- **DeepSeek**
  - 推荐模型：`deepseek-reasoner`

## 环境变量

复制模板：

```bash
cp .env.example .env
```

### 使用 GLM

```env
APP_MODE=llm
MODEL_PROVIDER=glm
GLM_API_KEY=你的真实GLM_API_KEY
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/chat/completions
GLM_MODEL=glm-4.7

DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com/chat/completions
DEEPSEEK_MODEL=deepseek-reasoner

LLM_TIMEOUT=120
LLM_TEMPERATURE=0.1
```

### 使用 DeepSeek

```env
APP_MODE=llm
MODEL_PROVIDER=deepseek
GLM_API_KEY=
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/chat/completions
GLM_MODEL=glm-4.7

DEEPSEEK_API_KEY=你的真实DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL=https://api.deepseek.com/chat/completions
DEEPSEEK_MODEL=deepseek-reasoner

LLM_TIMEOUT=120
LLM_TEMPERATURE=0.1
```

如果没有配置有效 API Key，系统会自动回退到 `rule` 模式。

## 运行方式

安装依赖：

```bash
python -m pip install -r requirements.txt
```

启动主程序：

```bash
python -m app.main
```

启动前端：

```bash
python -m streamlit run ui/streamlit_app.py
```

## 测试方式

回归测试：

```bash
python -m tests.test_langgraph_workflow
```

评估测试：

```bash
python -m tests.test_evaluation
```

前端展示测试：

```bash
python -m tests.test_report_format
```

LLM 诊断：

```bash
python -m tests.test_prompt_rendering
python -m tests.test_fallback_diagnostics
python -m tests.test_llm_integration
```

## 当前项目状态

### 已完成

- 多 Agent 架构与 LangGraph 状态图编排
- rule 模式主链路稳定运行
- RAG / Memory / Evaluation / Streamlit 已接入
- LLM Router、Planner、SQL Intent、Reflection 已实际生效
- SQL 节点具备 fallback 机制
- 项目可完整演示、可截图、可写入简历

### 当前限制

- LLM SQL Generator 在部分 SQL case 上仍可能生成不稳定的聚合 SQL，因此会回退到规则 SQL
- Reflection 在单独诊断测试中偶发超时，但在完整工作流中已成功运行
- 当前真实数据源尚未接入，默认仍使用 demo CSV + DuckDB
- 当前版本仍属于工程原型 / MVP，而非生产级系统

## 项目亮点

1. 不是单纯聊天机器人，而是面向企业分析场景的 Multi-Agent 决策助手
2. 采用 LangGraph 状态图工作流，而不是简单顺序脚本
3. 同时具备规则模式与大模型模式，兼顾可靠性与扩展性
4. SQL 查询之后还有 Pandas / NumPy 二次分析层
5. 加入 RAG、Memory、Reflection、Evaluation，完整体现 AI 产品工程化能力
6. 支持 SQL、实验分析、漏斗分析、结构化报告输出
7. 已具备前端展示能力，适合做简单的演示


## 后续迭代方向

- 进一步约束 LLM SQL Generator，提升聚合 SQL 生成稳定性
- 接入真实数据库 / 数仓而非 demo CSV
- 引入指标口径中心与语义层
- 增加权限控制、日志追踪与可观测性
- 增加更完整的图表可视化与交互前端
- 提升 LLM 节点的重试与超时治理能力
```
