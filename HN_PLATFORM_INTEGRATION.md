# HN 热榜作为平台集成 - 实现总结

## 概述
成功将 Hacker News 热榜（HN Top Stories 和 HN Best Stories）集成为独立的爬虫平台，与微博、B站、抖音等平台同级。

## 实现方案

### 核心思路
1. 创建 `hn_hot_collector.py` 来专门收集 HN 热榜数据
2. 修改 `foreign_news_crawler_service.py` 支持 `hn_hot` 和 `hn_best` 平台
3. 更新 `crawler_router_service.py` 添加新平台支持
4. 在前端平台选择器中添加 "HN 热门" 和 "HN 最佳" 选项
5. 配置爬虫限制和平台映射

### 文件变更清单

| 文件 | 修改 | 说明 |
|------|------|------|
| `app/services/hn_hot_collector.py` | 新建 | HN 热榜收集器，支持 top/best 两种故事 |
| `app/services/foreign_news_crawler_service.py` | 修改 | 增加对 `hn_hot` / `hn_best` 平台的支持 |
| `app/services/crawler_router_service.py` | 修改 | 扩展 FOREIGN_PLATFORMS 集合 |
| `app/config.py` | 修改 | 添加 `hn_hot` 和 `hn_best` 的爬虫限制配置 |
| `src/stores/analysis.js` | 修改 | 在 availablePlatforms 中添加 HN 平台选项 |
| `app/api/endpoints.py` | 修改 | 增强 `/api/hotnews` 支持 HN（可选，已保留） |

## 功能特点

### 1. 平台选择
用户在平台选择中可勾选三个 HN 相关选项：
- **"Hacker News (搜索)"** - 根据输入的话题关键词搜索 HN
- **"HN 热门"** - 获取 HN 最新的热门故事（Top Stories）
- **"HN 最佳"** - 获取 HN 历史最佳故事（Best Stories）

### 2. 热度值
- HN 热榜的热度值为 **point 数**（社区投票数）
- 返回格式标准化，与其他平台一致
- 数据字段：`hot_value` 包含点数

### 3. 数据标准化
无论是国内平台还是 HN，返回的数据结构统一：
```python
{
    "content_id": "...",
    "title": "故事标题",
    "url": "https://...",
    "platform": "hackernews",
    "hot_value": "77",  # HN 的 point 数
    "comments": 27,     # HN 的 descendants（评论数）
    "content": "..."
}
```

## 工作流程

### 用户视角
1. 在首页平台选择中勾选 "HN 热门" 或 "HN 最佳"
2. 输入话题（如 "AI") 并点击"启动分析"
3. 系统自动：
   - 从 HN 热榜抓取指定数量的故事
   - 与其他平台数据汇总
   - 进行多角度分析
   - 生成洞察和文案

### 系统内部流程
```
用户请求 (topic="AI", platforms=["hn_hot"])
    ↓
工作流启动 (crawler_agent_node)
    ↓
CrawlerRouterService.crawl_platform(platform="hn_hot", keywords="AI")
    ↓
ForeignNewsCrawlerService.crawl_platform(platform="hn_hot", ...)
    ↓
检测 platform.startswith("hn_")
    ↓
hn_hot_collector.collect_news(story_type="top", max_items=30)
    ↓
并发获取 HN API (topstories + item details)
    ↓
返回标准化数据
    ↓
与其他平台数据合并分析
```

## API 端点

### 旧端点（保留用于主页热搜）
- `GET /api/hotnews?source=hn_top&limit=10` - 获取 HN 热榜数据

### 核心端点（用于分析）
- `POST /api/analyze` - 分析请求，支持 platforms 参数中的 `hn_hot` / `hn_best`

## 配置

### CRAWLER_LIMITS (app/config.py)
```python
CRAWLER_LIMITS = {
    ...
    "hn_hot": {"max_items": 30, "max_comments": 0},
    "hn_best": {"max_items": 30, "max_comments": 0},
    ...
}
```

### PLATFORM_MAP (foreign_news_crawler_service.py)
```python
PLATFORM_MAP = {
    ...
    "hn_hot": "hn_hot",
    "hn_top": "hn_hot",  # 别名
    "hn_best": "hn_best",
    ...
}
```

## 测试验证

### 测试脚本
- `test_hn_hot.py` - 直接测试 HN 收集器
- `test_hn_platform.py` - 测试 HN 作为平台的完整流程
- `test_complete_workflow.py` - 端到端工作流测试

### 测试结果示例
```
HN 热门故事获取：✓ 30 条
HN 最佳故事获取：✓ 30 条
热度值示例：77 points
平台标准化：✓
```

## 关键改进

1. **无缝集成** - HN 热榜像其他平台一样，在平台选择器中出现，用户体验一致
2. **数据标准化** - 统一的返回格式，便于后续分析聚合
3. **配置灵活** - 通过 CRAWLER_LIMITS 可调整每个平台的爬取数量
4. **后向兼容** - 原有的 HN 搜索功能保持不变
5. **高效并发** - HN 故事详情并发获取，Semaphore 限制为 10

## 使用示例

### 前端 Vue 代码
```javascript
// 用户选择平台
const selectedPlatforms = ["wb", "bili", "hn_hot"];

// 发送分析请求
api.startAnalysis({
    topic: "AI最新进展",
    platforms: selectedPlatforms,
    debate_rounds: 2
});
```

### 后端 Python 代码
```python
# 系统自动路由到相应的爬虫
results = await crawler_router_service.crawl_platform(
    platform="hn_hot",
    keywords="AI最新进展",
    max_items=30
)
# 返回 HN Top Stories 数据，热度值为 point 数
```

## 下一步可能的优化

1. **缓存机制** - 为 HN 热榜添加后台定时更新和缓存
2. **评论集成** - 获取 HN 热门评论并融入分析
3. **趋势追踪** - 记录同一话题在 HN 的排名变化
4. **智能排序** - 根据热度、新鲜度、评论质量综合排序
5. **多语言支持** - 自动翻译 HN 故事标题到中文

## 文件大小统计

| 文件 | 行数 |
|------|------|
| hn_hot_collector.py | ~180 |
| foreign_news_crawler_service.py | 修改 ~35 行 |
| crawler_router_service.py | 修改 ~5 行 |
| config.py | 修改 ~3 行 |
| analysis.js | 修改 ~2 行 |

## 总结

HN 热榜已完全集成到 AgentPro 系统中，用户现在可以：
✓ 在平台选择中勾选 HN 热门/最佳
✓ 与国内平台数据一起分析
✓ 获得包含 HN point 热度值的数据
✓ 进行多角度的国内国外数据对比分析
