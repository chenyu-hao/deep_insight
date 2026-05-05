# GlobalInSight 项目现状与优化规划

---

## 一、项目概述

GlobalInSight 是一个基于 LangGraph 的多 Agent 协作舆情分析系统，核心包含两大子系统：

1. **Deep Insight Workflow** — 热点话题深度洞察工作流（8 节点 Agent 流水线）
2. **Hot News Pipeline** — 多源热榜数据聚合与演化追踪

技术栈：Python / FastAPI / LangGraph / LangChain / 7 种 LLM 提供商（OpenAI / Gemini / DeepSeek / Kimi / 豆包 / 智谱 / MiniMax）

---

## 二、Deep Insight Workflow 架构详解

### 2.1 工作流节点调用链路

```
START → crawler_agent → reporter → analyst → debater ⇄ analyst（辩论循环） → writer → image_generator → xhs_publisher → END
```

### 2.2 各节点职责与数据流

| 顺序 | 节点 | 代码位置 | 功能 | 关键输入字段 | 关键输出字段 |
|------|------|----------|------|-------------|-------------|
| ① | crawler_agent | `app/agents/deep_insight_workflow/crawler/node.py` | 多平台爬取（小红书/抖音/B站/微博/知乎/Reddit 等），支持话题翻译 | topic, platforms | crawler_data, platform_data, safety_blocked |
| ② | reporter | `app/agents/deep_insight_workflow/reporter/node.py` | 基于爬取数据总结核心新闻事实（5W1H） | topic, crawler_data, platform_data | news_content |
| ③ | analyst | `app/agents/deep_insight_workflow/analyst/node.py` | 深度舆论分析，接收 debater 反驳后修订 | news_content, critique | initial_analysis, revision_count, debate_history |
| ④ | debater | `app/agents/deep_insight_workflow/debater/node.py` | 魔鬼代言人，批判性审查分析师观点 | initial_analysis, topic, news_content | critique, debate_history |
| ⑤ | writer | `app/agents/deep_insight_workflow/writer/node.py` | 整合最终文案（小红书风格），输出 Markdown 文件 | initial_analysis, topic, news_content, debate_history | final_copy, output_file |
| ⑥ | image_generator | `app/agents/deep_insight_workflow/image_generator/node.py` | 调用文生图 API 生成配图 | final_copy, initial_analysis, image_count | image_urls |
| ⑦ | xhs_publisher | `app/agents/deep_insight_workflow/xhs_publisher/node.py` | 发布到小红书（可选，需开启 auto_publish） | final_copy, image_urls | xhs_publish_result |

### 2.3 辩论循环机制（核心设计）

`should_continue` 函数控制 analyst ↔ debater 的多轮对抗：

```
debater 输出 critique
  → 含 "PASS" 或 revision_count ≥ debate_rounds → 进入 writer
  → 否则 → 回到 analyst（根据 critique 修订分析，revision_count + 1）
```

- 每轮都会追加 debate_history
- 最大轮数受 `settings.DEBATE_MAX_ROUNDS` 约束（默认 3）

### 2.4 安全护栏

crawler_agent 入口处检测敏感政治话题，命中后设置 `safety_blocked = True`，后续所有节点跳过核心逻辑，返回安全占位字符串。

### 2.5 共享状态（GraphState）

所有节点通过 `TypedDict(GraphState)` 共享同一个状态字典，核心字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| urls | List[str] | 用户提供的 URL |
| topic | str | 热点话题 |
| platforms | List[str] | 选中的爬取平台 |
| debate_rounds | int | 辩论轮数 |
| image_count | int | 生成图片数量 |
| crawler_data | List[Dict] | 爬取原始数据 |
| platform_data | Dict[str, List] | 按平台分组的数据 |
| news_content | str | 新闻摘要 |
| initial_analysis | str | 分析结果 |
| critique | Optional[str] | 反驳意见 |
| revision_count | int | 修订轮次 |
| final_copy | str | 最终文案 |
| image_urls | List[str] | 生成图片 URL |
| debate_history | List[str] | 辩论过程记录 |
| safety_blocked | bool | 安全阻断标记 |
| xhs_publish_result | Optional[Dict] | 发布结果 |

### 2.6 API 入口

- `POST /api/analyze` — 传入 `NewsRequest{topic, platforms, debate_rounds, image_count}`，通过 `app_graph.astream(initial_state)` 执行工作流，SSE 流式返回各节点执行结果

---

## 三、Hot News 热榜系统架构详解

### 3.1 模块总览

热榜系统由 9 个核心模块组成，总代码量约 1800 行：

| 模块 | 文件 | 行数 | 职责 |
|------|------|------|------|
| 调度器 | `app/services/hotnews/hot_news_scheduler.py` | 110 | APScheduler 定时采集 |
| 缓存 | `app/services/hotnews/hot_news_cache.py` | 180 | 内存 + JSON 文件双写缓存 |
| 聚类对齐 | `app/services/hotnews/hotnews_alignment.py` | 412 | 标题归一化 + 多源聚类 + 争议度 |
| 热度信号 | `app/services/hotnews/hotnews_signals.py` | 77 | 快照间 delta/growth 计算 |
| 历史存储 | `app/services/hotnews/hotnews_history.py` | 106 | JSONL 追加 + 定期压缩 |
| LLM 解读 | `app/services/hotnews/hotnews_interpreter.py` | 213 | 单话题 LLM 演化解读 |
| LLM 富文本 | `app/services/hotnews/hotnews_llm_enricher.py` | 145 | 批量簇的标题归一/关键词 |
| TopHub 采集 | `app/services/hotnews/tophub_collector.py` | 435 | 爬取 TopHub 8 个平台 |
| HN 采集 | `app/services/hotnews/hn_hot_collector.py` | 306 | 爬取 Hacker News API |

### 3.2 多源热榜数据采集

**TopHub**：统一采集 8 个国内平台热榜（微博/知乎/百度/贴吧/抖音/36氪/少数派/IT之家），通过 httpx 异步请求，间隔 0.5s 防反爬。

**Hacker News**：调用 Firebase API，并发获取前 60 条详情（Semaphore(10) 限流）。

### 3.3 混合相似度聚类去重算法

**标题归一化**：
- 去除排名前缀（`#1 ` 等）
- 全量标点 → 空格
- 合并空格、小写

**相似度计算**（混合模型）：
```
similarity = 0.55 × SequenceMatcher.ratio() + 0.45 × 2-gram Jaccard
```
- SequenceMatcher 对英文友好
- 2-gram Jaccard 对中文短文本友好

**聚类流程**：
1. 按 hot_score 降序排列所有 item
2. 贪心遍历，与已有簇计算 title_similarity
3. ≥ 阈值（0.74）→ 归入该簇，否则创建新簇（最多 900 个）
4. 每个簇内按 (platform_id, url, title) 去重

### 3.4 争议度计算

规则引擎，24 个中文争议关键词（塌房、曝光、造假、维权、反转等）：

```
争议度 = 18 × (命中关键词数) + 60 × (1 - 平均标题相似度) + min(20, log1p(hot_score) / 2)
```

### 3.5 热度演化追踪

**周期性快照**：每 4 小时通过 JSONL 追加保存一次快照，定期压缩（保留 30 天、最多 2000 行）。

**delta/growth 计算**：
- `delta = cur_score - prev_score`（绝对值变化）
- `growth_pct = delta / prev_score × 100%`（相对增长率）
- `is_new`：上一快照中不存在该 cluster_id

**生命周期阶段**（启发式判定）：
- 爆发期：is_new && growth >= 0
- 扩散期：growth >= 30 || delta >= 0
- 回落期：growth <= -15 || delta < 0
- 盘整期：其余情况

### 3.6 缓存策略

| 缓存 | 文件 | 粒度 | 过期策略 |
|------|------|------|---------|
| 热榜数据 | `cache/hot_news_{key}_{date}.json` | 按天分文件，240 分钟 TTL | 有过期判断，SWR 后台刷新 |
| LLM 解读 | `outputs/hotnews_interpret_cache.json` | 天:话题ID:采集时间 | 永不过期，无限增长 |
| LLM 富文本 | `outputs/hotnews_llm_cache.json` | 天:簇ID | 永不过期，无限增长 |

### 3.7 数据流向

```
定时调度（4h） → TopHub 采集 + HN 采集 → 缓存 JSON
                                           ↓
用户请求 /hot-news/collect → 读缓存（SWR 模式） → 聚类对齐 → 历史信号 → 返回前端
                                              ↓
                         LLM 解读（按需） ← 用户点开单条
```

---

## 四、已确认存在的问题

### 4.1 Deep Insight Workflow 问题

| # | 问题 | 严重程度 | 位置 |
|---|------|---------|------|
| 1 | **无 Checkpoint 持久化**，工作流中断无法恢复 | 🔴 高 | `graph.py:L91` — `workflow.compile()` 未传 checkpointer |
| 2 | **爬虫串行执行**，多平台逐个执行效率低 | 🔴 高 | `crawler/node.py:L73` — for 循环逐个 await |
| 3 | **Debater 判定粗糙**，仅靠字符串 `"PASS" in critique` | 🟡 中 | `graph.py:L51-L54` |
| 4 | **无 content moderator 节点**，仅有政治一审 | 🟡 中 | 缺失 |
| 5 | **Prompt 全部硬编码** Python 字符串常量 | 🟡 中 | `prompts/workflow/` 下全部 |
| 6 | **SSE 无背压处理**，客户端断开后仍继续执行 | 🟡 中 | `endpoints.py:L246` |
| 7 | **图片生成后无质量过滤/重试** | 🟢 低 | `image_generator/node.py` |
| 8 | **Writer 输出格式不稳定**，LLM 不遵守 TITLE/CONTENT 格式时无回退 | 🟢 低 | `writer/node.py` |

### 4.2 Hot News 系统问题

| # | 问题 | 严重程度 | 位置 |
|---|------|---------|------|
| 1 | **LLM 缓存文件无限增长**，从不清除 | 🔴 高 | `hotnews_interpreter.py` / `hotnews_llm_enricher.py` |
| 2 | **调度器不执行完整流水线**，仅做采集不聚类 | 🔴 高 | `hot_news_scheduler.py:L77` |
| 3 | **只比最近 1 个快照**，看不出时间段内的趋势 | 🟡 中 | `hotnews_signals.py` |
| 4 | **无热度时序衰减**，旧数据权重与新数据相同 | 🟡 中 | `hotnews_alignment.py:L221` |
| 5 | **聚类无语义相似度**，中英跨语言标题无法匹配 | 🟡 中 | `hotnews_alignment.py` — 仅字符串匹配 |
| 6 | **900 个簇硬上限**，超出直接静默丢弃 | 🟡 中 | `hotnews_alignment.py:L243` |
| 7 | **无热度异常检测**（z-score / 阈值告警） | 🟡 中 | 缺失 |
| 8 | **无 retry / 熔断机制**，HTTP 请求失败不重试 | 🟡 中 | `tophub_collector.py` / `hn_hot_collector.py` |
| 9 | **endpoints.py 上帝函数**，`_rebuild_aligned_clusters` 混合采集/聚类/缓存/存储 | 🟡 中 | `endpoints.py:L72-L190` |
| 10 | **无分布式协调**，多实例部署会重复执行定时任务 | 🟢 低 | `hot_news_scheduler.py` |
| 11 | **heuristic_stage 判定过于宽松**，`delta >= 0` 就判扩散期 | 🟢 低 | `hotnews_interpreter.py:L45-L53` |
| 12 | **JSON 缓存并发不安全**，无文件锁 | 🟢 低 | `hotnews_interpreter.py` / `hotnews_llm_enricher.py` |
| 13 | **cleanup_old_caches 从未被调用** | 🟢 低 | `hot_news_cache.py:L152` |
| 14 | **全局单例模式**，不利于单元测试 | 🟢 低 | 所有热榜模块 |

---

## 五、优化方案（简历可写）

### 5.1 工作流侧（3 点）

| # | 优化项 | 简历描述 | 技术栈 | 优先级 |
|---|--------|---------|--------|--------|
| ① | **多 Agent 协作工作流**（已有） | 基于 LangGraph 设计 8 节点多 Agent 协作工作流（爬虫→记者→分析师→辩手→撰稿→配图→发布），实现新闻热点全自动深度解读与多模态内容生产 | LangGraph / LLM | ✅ 已有 |
| ② | **爬虫并发改造** | 引入 `asyncio.gather` 并发框架重构多平台爬虫调度，将 7+ 社交媒体平台的爬取耗时从线性累加（~15min）降低至单平台最长耗时（~2min），吞吐量提升 5-7 倍 | Python asyncio | 🔴 P0 |
| ③ | **断点续跑** | 采用 LangGraph Checkpoint + SQLite 实现工作流状态持久化与断点续跑，支持任意节点中断恢复与执行历史回溯 | SQLite / LangGraph | 🔴 P0 |

### 5.2 热榜侧（2 点）

| # | 优化项 | 简历描述 | 技术栈 | 优先级 |
|---|--------|---------|--------|--------|
| ④ | **跨平台话题聚合** | 设计多源异构热榜数据聚合管道，基于混合相似度聚类算法（2-gram Jaccard + SequenceMatcher）实现 9 个平台的跨平台话题对齐与智能去重，结合规则引擎进行争议度评分与内容热力分级 | 聚类算法 / NLP | 🔴 P0 |
| ⑤ | **热榜演化追踪** | 构建热榜演化追踪体系，基于周期性快照（JSONL）实现多时间窗口趋势分析、生命周期阶段识别（爆发/扩散/盘整/回落）与 z-score 异常热度检测 | 时序分析 / 信号计算 | 🟡 P1 |

### 5.3 能力覆盖

| 能力维度 | 对应优化点 | 子领域 |
|---------|-----------|--------|
| Agent / 工作流工程 | ①②③ | 状态图设计、并发调度、持久化 |
| 并发 / 性能优化 | ② | asyncio.gather |
| 数据管道 / ETL | ④ | 多源采集、归一化、聚类去重 |
| 算法 / 时序分析 | ⑤ | 相似度、趋势检测、异常检测 |
| 持久化 / 可靠性 | ③ | Checkpoint、断点续跑 |

---

## 六、实现计划

### 阶段一：工作流核心改造（Week 1-2）

**② 爬虫并发改造**
- 目标文件：`app/agents/deep_insight_workflow/crawler/node.py`
- 改造方式：用 `asyncio.gather` 替代 for 循环串行调用
- 涉及函数：`crawler_router_service.crawl_platform`
- 要点：各平台独立、无共享状态，天然适合并发

**③ Checkpoint 持久化**
- 目标文件：`app/agents/deep_insight_workflow/graph.py`
- 改造方式：引入 `SqliteSaver`，编译时传入 checkpointer
- 涉及点：
  - `workflow.compile(checkpointer=SqliteSaver.from_conn_string("checkpoints.db"))`
  - API 调用时传入 `config = {"configurable": {"thread_id": request_id}}`
  - 新增 API 端点：查询历史执行记录、恢复中断任务

### 阶段二：热榜系统打磨（Week 3-4）

**④ 聚类算法完善**
- 目标文件：`app/services/hotnews/hotnews_alignment.py`
- 现有基础已较好（混合相似度 + 归一化 + 去重）
- 可选增强：
  - 嵌入语义去重（multilingual sentence-transformers）
  - 修复 900 簇硬上限的静默丢弃

**⑤ 热榜演化追踪**
- 目标文件：`app/services/hotnews/hotnews_signals.py`、`hotnews_interpreter.py`
- 改进点：
  - 多窗口趋势分析（读最近 3-5 个快照）
  - 热度时序衰减（指数加权）
  - z-score 异常检测
  - 修正 heuristic_stage 判定逻辑

---

*文档生成时间：2026-05-05*
