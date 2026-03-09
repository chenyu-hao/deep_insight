**最终修正版实施计划 v2**

**1. 核心修正**
1. 卡片服务不再采用“页面截图”方案。
2. 卡片生成改为“浏览器运行时直接调用现有 `generateImage()` / canvas 导出逻辑”，返回 `data:image/png;base64,...`、本地文件路径或对象存储 URL。
3. `xhsMCP` 继续沿用现有发布 contract，不改发布协议。
4. `AI Daily` 走独立新 pipeline，不替换现有 `hotnews`。
5. `Skill` 只调用统一 API，不直接耦合前端或 MCP 细节。

**2. 现状确认**
1. `xhsMCP` 最终接收的是 `title + content + images + tags`，其中 `images` 支持 `data URL / 本地绝对路径 / HTTP URL`。关键代码在 [xiaohongshu_publisher.py:14](/Volumes/Work/Projects/GlobalInSight/app/services/xiaohongshu_publisher.py#L14) 和 [xiaohongshu_publisher.py:238](/Volumes/Work/Projects/GlobalInSight/app/services/xiaohongshu_publisher.py#L238)。
2. 后端发布入口是 [endpoints.py:1278](/Volumes/Work/Projects/GlobalInSight/app/api/endpoints.py#L1278) 的 `/api/xhs/publish`。
3. 标题卡当前就是前端直接出图，不是截图，逻辑在 [XiaohongshuCard.vue:160](/Volumes/Work/Projects/GlobalInSight/src/components/XiaohongshuCard.vue#L160)。
4. 三张分析卡当前也是前端直接出图，逻辑入口在 [DataView.vue:533](/Volumes/Work/Projects/GlobalInSight/src/views/DataView.vue#L533)。
5. 当前前端发布链路已经支持“标题卡 + DataView 卡 + AI 图”组合发布，入口在 [HomeView.vue:1358](/Volumes/Work/Projects/GlobalInSight/src/views/HomeView.vue#L1358)。

**3. 最终目标架构**
```text
Claude Skill / MCP
  -> AI Insight API
     -> AI Daily Pipeline
     -> Analysis Pipeline
     -> Card Render Proxy
     -> XHS Publish Adapter

Card Render Proxy
  -> Renderer Service (独立容器)
     -> Headless Browser Runtime
     -> 调用前端卡片导出函数
     -> 返回 dataURL / 文件 URL / 文件路径

XHS Publish Adapter
  -> /api/xhs/publish
  -> xiaohongshu_publisher
  -> xhsMCP
```

**4. 服务拆分**
1. `api` 容器
负责业务 API、AI Daily pipeline、现有分析工作流、XHS 发布代理。
2. `renderer` 容器
负责标题卡、三张分析卡、每日榜单卡的图片导出。
3. `Skill`
只面向 `api` 容器暴露的公网地址，不直接请求 `renderer`。
4. `xhsMCP`
作为发布适配层保留，仍由 `api` 调用。

**5. 渲染方案 v2**
1. 不做 DOM screenshot。
2. 保留现有前端 canvas 导出思路，把绘图逻辑抽成可复用模块。
3. Vue 组件继续负责预览；导出逻辑移到共享 renderer 模块。
4. `renderer` 服务通过 Headless Browser 仅作为 JS 运行时，执行导出函数并拿回 data URL。
5. `api` 层将 data URL 原样传给 `/api/xhs/publish`，由现有发布逻辑转临时文件并交给 MCP。

**6. 渲染层重构方式**
1. 从现有组件中抽出共享导出函数。
建议新建：
- `src/renderers/title_card_renderer.ts`
- `src/renderers/radar_card_renderer.ts`
- `src/renderers/timeline_card_renderer.ts`
- `src/renderers/trend_card_renderer.ts`
- `src/renderers/daily_rank_renderer.ts`

2. 现有组件改为“预览 + 复用 renderer”。
涉及：
- [XiaohongshuCard.vue](/Volumes/Work/Projects/GlobalInSight/src/components/XiaohongshuCard.vue)
- [RadarChartCanvas.vue](/Volumes/Work/Projects/GlobalInSight/src/components/canvas/RadarChartCanvas.vue)
- [DebateTimelineCanvas.vue](/Volumes/Work/Projects/GlobalInSight/src/components/canvas/DebateTimelineCanvas.vue)
- [TrendChartCanvas.vue](/Volumes/Work/Projects/GlobalInSight/src/components/canvas/TrendChartCanvas.vue)

3. 新增专用渲染入口页。
建议新增：
- `src/views/RenderView.vue`

4. `RenderView.vue` 职责
- 接收卡片类型和 payload
- 装载对应 renderer
- 暴露统一浏览器端方法，例如 `window.__CARD_RENDERER__.render(payload)`
- 返回 data URL，不负责截图

**7. Renderer Service 设计**
1. 新增目录：
- `renderer/server.ts`
- `renderer/Dockerfile`
- `renderer/playwright/*`

2. `renderer` 对外接口：
- `POST /render/title`
- `POST /render/radar`
- `POST /render/timeline`
- `POST /render/trend`
- `POST /render/daily-rank`
- `GET /healthz`

3. 每个接口内部流程：
- 打开 `RenderView`
- 注入 payload
- 执行页面内 `render()` 方法
- 直接取回 data URL
- 可选上传对象存储
- 返回 `image_data_url` 或 `image_url`

4. 标准响应：
```json
{
  "success": true,
  "image_data_url": "data:image/png;base64,...",
  "image_url": null,
  "width": 1080,
  "height": 1440,
  "mime_type": "image/png"
}
```

**8. API 层对渲染服务的封装**
1. 不让 Skill 直接碰 `renderer`。
2. 在 `api` 容器新增统一代理：
- `POST /api/cards/title`
- `POST /api/cards/radar`
- `POST /api/cards/timeline`
- `POST /api/cards/trend`
- `POST /api/cards/daily-rank`

3. 新增：
- `app/services/card_render_client.py`

4. 好处
- Skill 只记一个域名
- 后面更换渲染实现不会影响 Skill contract
- 发布链路也能统一复用

**9. AI Daily 信息源策略**
首期主源分成四类。

1. 中文媒体源
- [AIBase 新闻](https://news.aibase.com/zh/)
- [机器之心](https://www.jiqizhixin.com/)
- [量子位](https://www.qbitai.com/)

2. 英文产品与开源源
- [GitHub Trending](https://github.com/trending)
- [Product Hunt AI](https://www.producthunt.com/topics/artificial-intelligence)

3. 英文研究源
- [Hugging Face Trending Papers](https://huggingface.co/papers/trending)

4. 英文媒体补充源
- [TechCrunch AI](https://techcrunch.com/category/artificial-intelligence/)

二期增强：
- Brave Search API 仅做补充召回
- Hacker News 仅做 AI 主题补充，不做主源

**10. AI Daily 独立新 Pipeline**
1. 新增 `collectors`
建议目录：
- `app/services/collectors/aibase_collector.py`
- `app/services/collectors/jiqizhixin_collector.py`
- `app/services/collectors/qbitai_collector.py`
- `app/services/collectors/github_trending_collector.py`
- `app/services/collectors/producthunt_ai_collector.py`
- `app/services/collectors/hf_papers_collector.py`
- `app/services/collectors/techcrunch_ai_collector.py`

2. 新增 pipeline 服务
- `app/services/ai_daily_pipeline.py`
- `app/services/ai_news_scorer.py`
- `app/services/ai_topic_cluster.py`
- `app/services/ai_daily_cache.py`

3. 处理流程
- 多源抓取
- 统一结构
- 去重
- 聚类
- AI 相关性过滤
- 评分
- 中文摘要生成
- 标签分类
- 写入 daily pool

4. 缓存策略
- `cache/ai_daily/YYYY-MM-DD.json`

**11. AI Daily 数据结构**
`SourceItem`
```json
{
  "id": "hash",
  "title": "string",
  "url": "string",
  "source": "aibase",
  "source_type": "media",
  "lang": "zh",
  "published_at": "2026-03-08T10:00:00Z",
  "summary": "string",
  "tags": ["agent", "llm"]
}
```

`DailyTopic`
```json
{
  "topic_id": "cluster_xxx",
  "title": "string",
  "summary_zh": "string",
  "sources": [],
  "tags": [],
  "source_count": 4,
  "lang_mix": ["zh", "en"],
  "ai_relevance_score": 9.4,
  "impact_score": 8.2,
  "freshness_score": 8.8,
  "discussion_score": 7.1,
  "final_score": 8.7
}
```

**12. 新增 API Contract**
1. `POST /api/ai-daily/collect`
作用：主动重建当天 AI 榜单。

2. `GET /api/ai-daily`
作用：返回今日榜单。
建议参数：`lang=zh|en|all`、`top=10|20|50`

3. `GET /api/ai-daily/{topic_id}`
作用：返回单条热点详情。

4. `POST /api/ai-daily/{topic_id}/analyze`
作用：把单条热点送入现有分析链路。

5. `POST /api/ai-daily/{topic_id}/cards`
作用：一次性返回该热点的卡片包。

6. `POST /api/cards/daily-rank`
作用：生成今日榜单卡。

**13. 与现有分析系统的衔接**
1. 不重写 multi-agent debate。
2. 新增 `DailyTopic -> workflow input` 的转换层。
3. 复用 [workflow.py](/Volumes/Work/Projects/GlobalInSight/app/services/workflow.py) 现有 `reporter / analyst / debater / writer` 节点。
4. `AI Daily` 只是替换“输入语义”，不是重写“分析流程”。

**14. 发布链路 v2**
1. 继续沿用现有 `/api/xhs/publish`。
2. 不改 `xhsMCP` 的字段协议。
3. 新增发布服务：
- `app/services/publish/ai_daily_publish_service.py`

4. 两类发布包：
- `analysis_pack`：`title + radar + timeline + trend + ai_images`
- `daily_pack`：`daily_rank + optional_title`

5. `images` 字段优先使用 `data URL`。
6. 如果后面接对象存储，再支持 `image_url`。

**15. Skill 设计**
目录建议：
```text
.claude/skills/ai-insight/
  SKILL.md
  examples.md
  references/api.md
  references/source-policy.md
  agents/openai.yaml
```

Skill 只保留两条主命令：
1. `/ai-daily`
获取今天 AI 热点榜单、摘要、榜单卡。

2. `/analyze <topic_or_id>`
对指定 AI 热点做深度分析，并可生成卡片/发布。

建议参数：
- `/ai-daily --lang all --top 10 --with-card`
- `/analyze DeepSeek R2 --with-cards --publish`

**16. MCP 适配**
1. 不污染旧 `hotnews` 语义。
2. 新增工具：
- `get_ai_daily`
- `analyze_ai_topic`
- `publish_ai_daily`

3. 保留旧工具做兼容。
4. `opinion_mcp` 只改扩展，不做破坏式替换。

**17. 文件变更范围**
新增：
- `app/services/collectors/*`
- `app/services/ai_daily_pipeline.py`
- `app/services/ai_news_scorer.py`
- `app/services/ai_topic_cluster.py`
- `app/services/ai_daily_cache.py`
- `app/services/card_render_client.py`
- `app/services/publish/ai_daily_publish_service.py`
- `src/renderers/*`
- `src/views/RenderView.vue`
- `src/components/canvas/DailyRankCanvas.vue`
- `renderer/*`
- `.claude/skills/ai-insight/*`
- `tests/*`

修改：
- [app/api/endpoints.py](/Volumes/Work/Projects/GlobalInSight/app/api/endpoints.py)
- [app/main.py](/Volumes/Work/Projects/GlobalInSight/app/main.py)
- [app/config.py](/Volumes/Work/Projects/GlobalInSight/app/config.py)
- [app/services/workflow.py](/Volumes/Work/Projects/GlobalInSight/app/services/workflow.py)
- [src/components/XiaohongshuCard.vue](/Volumes/Work/Projects/GlobalInSight/src/components/XiaohongshuCard.vue)
- [src/views/DataView.vue](/Volumes/Work/Projects/GlobalInSight/src/views/DataView.vue)
- [src/views/HomeView.vue](/Volumes/Work/Projects/GlobalInSight/src/views/HomeView.vue)
- `opinion_mcp/server.py`
- `opinion_mcp/config.py`
- `opinion_mcp/tools/*`

暂不动：
- 旧 `hotnews` pipeline
- 旧手动前端分析页面交互
- 现有 `xhsMCP` 协议

**18. 测试计划**
1. 先补顶层 `tests/` 基础设施。
2. collector 测试全部用 fixture HTML，不依赖线上页面直连。
3. 新增：
- `tests/collectors/test_aibase_collector.py`
- `tests/collectors/test_jiqizhixin_collector.py`
- `tests/collectors/test_qbitai_collector.py`
- `tests/collectors/test_github_trending_collector.py`
- `tests/collectors/test_hf_papers_collector.py`
- `tests/services/test_ai_news_scorer.py`
- `tests/services/test_ai_daily_pipeline.py`
- `tests/api/test_ai_daily_api.py`
- `tests/renderer/test_card_export.py`

4. 渲染测试验证的是 `data URL` 有效性、尺寸、mime type，不是截图像素对比。

**19. 部署与验证**
1. `docker compose up --build`
2. `GET /api/health`
3. `POST /api/ai-daily/collect`
4. `GET /api/ai-daily?lang=all&top=10`
5. `POST /api/cards/title`
6. `POST /api/cards/daily-rank`
7. `POST /api/ai-daily/{topic_id}/analyze`
8. `POST /api/xhs/publish`

重点验收：
- renderer 返回的是 `data URL / URL`，不是 screenshot 文件
- `/api/xhs/publish` 能直接消费 renderer 输出
- `AI Daily` 与旧 `hotnews` 并存
- Skill 只需配置一个 API 地址即可跑通

**20. 推荐实施顺序**
1. Phase A：冻结 contract 与数据结构
2. Phase B：抽离共享 renderer，跑通 `title/radar/timeline/trend`
3. Phase C：接入 renderer 容器与 `/api/cards/*`
4. Phase D：实现 `AI Daily` collectors 与 pipeline
5. Phase E：接入现有 workflow 做深度分析
6. Phase F：重写 Skill 与 MCP 工具
7. Phase G：补测试、部署、联调发布

**21. 最终落地口径**
这次升级不是“把前端截图搬上云”，而是：
- 保留你现有直接生图能力
- 把直接生图逻辑从页面实例里抽出来
- 用双容器把它服务化
- 再把 AI 热点聚合作为一条独立新业务线接进来
