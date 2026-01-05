# HN 热榜功能实现文档

## 功能概述
成功为 AgentPro 项目添加了 Hacker News (HN) 热点排行榜功能，与现有的 TopHub 国内热榜进行整合。

## 实现细节

### 1. 后端实现

#### 新建文件：`app/services/hn_hot_collector.py`
- **功能**：专门用于收集 HN 热点新闻的收集器类
- **核心能力**：
  - 支持 HN 的 Top Stories 和 Best Stories 两种排行榜
  - 并发获取故事详情（Semaphore 限制为 10 个并发）
  - 返回标准化的新闻项（title, url, score, descendants 等）
  - 完整的日志记录和错误处理
  
- **关键方法**：
  - `collect_news(story_type="top", max_items=30)`：主要方法，支持 "top" 或 "best"
  - `_fetch_item(client, item_id)`：获取单个 HN item 详情

- **API 来源**：
  - `/v0/topstories.json` - 获取热门故事 ID 列表
  - `/v0/beststories.json` - 获取最佳故事 ID 列表
  - `/v0/item/{id}.json` - 获取故事详情（标题、URL、分数、评论数等）

#### 修改文件：`app/api/endpoints.py`
- **修改内容**：
  1. 导入 `hn_hot_collector`
  2. 增强 `/api/hotnews` 端点支持 HN 来源
  
- **新增功能**：
  - 检测 `source` 参数是否以 "hn_" 开头
  - 若是 HN 来源，调用 `hn_hot_collector.collect_news()`
  - 若是 TopHub 来源，使用现有的 `tophub_collector.collect_news()`
  - 统一返回格式，HN 返回含 "points" 和 "comments" 的 hot_value 字段

- **支持的 source 参数**：
  - `"hot"` - TopHub 全榜（默认）
  - `"hn_top"` - HN Top Stories（最新热门）
  - `"hn_best"` - HN Best Stories（历史最佳）
  - `"all"` - 所有 TopHub 榜单
  - 其他 ID - 指定的 TopHub 榜单

### 2. 前端实现

#### 修改文件：`src/views/HomeView.vue`
- **新增状态变量**：
  - `hotNewsSource` - 当前选择的热榜来源（默认 "hot"）
  
- **UI 改进**：
  - 在热搜区域添加了下拉选择器，用户可切换热榜来源
  - 支持三个选项：TopHub 全榜、HN 热门、HN 最佳
  - 选择变化时自动刷新热搜列表
  
- **逻辑更新**：
  - `refreshTrending()` 方法现在使用 `hotNewsSource.value` 参数
  - 根据不同来源设置不同的日期显示文案
    - TopHub：显示日期（如 "1月2日"）
    - HN Top：显示 "HN热门"
    - HN Best：显示 "HN最佳"

#### 修改文件：`src/api/index.js`
- **文档更新**：
  - 更新 `getHotNews()` 方法的注释说明
  - 新增 HN 来源选项文档

### 3. 数据流图

```
前端 (HomeView.vue)
  ↓
选择热榜来源 (hotNewsSource)
  ↓
调用 api.getHotNews(limit, source, forceRefresh)
  ↓
后端 (/api/hotnews)
  ├─ 如果是 HN 来源 (hn_top/hn_best)
  │  └─ 调用 hn_hot_collector.collect_news()
  │     ├─ 获取故事 ID 列表 (Firebase API)
  │     └─ 并发获取故事详情 (Firebase API)
  │        └─ 返回标准化数据
  │
  └─ 如果是 TopHub 来源
     └─ 调用 tophub_collector.collect_news()
        └─ 返回标准化数据
```

## 测试验证

### 测试脚本：`test_hn_hot.py`
```bash
python test_hn_hot.py
```

**测试结果**（示例）：
- ✓ Top Stories: 成功获取 5 条新闻
  - 示例：《10 years of personal finances in plain text files》
  - 分数：74 | 评论：25
  
- ✓ Best Stories: 成功获取 5 条新闻
  - 示例：《2025: The Year in LLMs》
  - 分数：881 | 评论：531

## 功能特点

1. **多来源支持**：用户可在 TopHub（国内热榜）和 HN（国外热榜）之间快速切换

2. **高效并发**：
   - HN 故事详情并发获取（Semaphore 限制为 10 个并发）
   - 避免 API 请求过快导致被限制

3. **数据标准化**：
   - 统一的返回格式
   - HN 返回包含得分和评论数
   - TopHub 返回包含热度值

4. **无缝集成**：
   - 与现有的 TopHub 功能完全兼容
   - 复用现有的缓存机制和 API 接口
   - 前端无需大改，只需添加选择器

5. **用户友好**：
   - 直观的选择器切换
   - 自动更新日期显示文案
   - 3 条滑动窗口展示，点击刷新按钮旋转

## 使用示例

### 前端使用
```javascript
// 获取 HN Top Stories
const res = await api.getHotNews(10, 'hn_top', false);
console.log(res.items); // HN 热门故事

// 获取 HN Best Stories
const res = await api.getHotNews(10, 'hn_best', false);
console.log(res.items); // HN 最佳故事

// 获取 TopHub 全榜
const res = await api.getHotNews(10, 'hot', false);
console.log(res.items); // TopHub 全榜
```

### 后端直接使用
```python
from app.services.hn_hot_collector import hn_hot_collector
import asyncio

result = asyncio.run(
    hn_hot_collector.collect_news(story_type="top", max_items=10)
)
print(result['news_items'])
```

## 返回数据格式

### HN 热榜返回示例
```json
{
  "success": true,
  "items": [
    {
      "title": "10 years of personal finances in plain text files",
      "url": "https://sgoel.dev/posts/10-years-of-personal-finances-in-pla...",
      "rank": 1,
      "hot_value": "74 points, 25 comments",
      "source": "HN TOP Stories",
      "source_id": "hn_top"
    },
    ...
  ],
  "total": 3,
  "source": "hn_top",
  "from_cache": false,
  "collection_time": "2026-01-02T20:43:38.123456"
}
```

## 下一步可能的扩展

1. **缓存支持**：为 HN 热榜添加专门的缓存机制（目前 HN 收集器暂不缓存）
2. **定时更新**：在后台定时收集 HN 热榜并缓存
3. **搜索集成**：在用户选择 HN 故事后，自动在 HN 上搜索相关话题
4. **评论集成**：展示 HN 故事的热门评论
5. **组合视图**：在一个视图中同时显示 TopHub 和 HN 的热点

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `app/services/hn_hot_collector.py` | 新建 | HN 热榜收集器 |
| `app/api/endpoints.py` | 修改 | 增强 `/api/hotnews` 支持 HN |
| `src/views/HomeView.vue` | 修改 | 添加热榜来源选择器 |
| `src/api/index.js` | 修改 | 更新 API 文档注释 |
| `test_hn_hot.py` | 新建 | HN 热榜功能测试脚本 |
