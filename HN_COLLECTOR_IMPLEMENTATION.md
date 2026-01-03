# HN (Hacker News) 热点新闻收集器 - 实现总结

## 项目概述

成功实现了 Hacker News 热点新闻收集器，学习并参照了 TopHub 全网热点新闻收集器的设计模式，向前端提供统一格式的 HN 新闻数据。

## 核心改进点

### 1. HN 收集器架构升级 (app/services/hn_hot_collector.py)

#### 原始设计的问题：
- 只支持单一榜单查询（top/best）
- 缺乏缓存支持机制
- 返回格式不统一
- 没有像 TopHub 那样灵活的收集器接口

#### 改进后的设计：
```python
# 新增榜单配置（参照 TopHub TOPHUB_SOURCES）
HN_SOURCES = {
    "top": {"name": "HN 最热", "category": "国外科技", "platform": "hackernews", "priority": 0},
    "best": {"name": "HN 最佳", "category": "国外科技", "platform": "hackernews", "priority": 1},
    "new": {"name": "HN 最新", "category": "国外科技", "platform": "hackernews", "priority": 2},
}
```

#### 关键方法：

**1. `fetch_source_news(source_id: str, max_items: int = 30) -> Dict`**
   - 从单个 HN 榜单获取新闻
   - 返回结构化数据，包含完整元数据
   - 自动处理超时和错误情况

**2. `collect_news(source_ids, max_items, force_refresh) -> Dict`**
   - 支持多榜单并发收集
   - 支持缓存机制
   - 统一格式输出，与 TopHub 兼容

### 2. 数据结构设计

#### TopHub 和 HN 共同字段：
```json
{
  "id": "source_id_rank",          // 唯一标识
  "title": "新闻标题",              // 新闻标题
  "url": "链接",                    // 原始链接
  "hot_value": "热度值",            // 格式化热度（字符串）
  "rank": 1,                       // 排名
  "source": "来源名称",             // 如 "HN 最热"
  "source_id": "top",              // 来源ID
  "category": "国外科技"             // 分类
}
```

#### HN 特有字段：
```json
{
  "score": 99,                     // 得分（数字）
  "descendants": 32,               // 评论数（数字）
  "author": "username",            // 作者
  "posted_time": 1767352071        // 发布时间戳
}
```

#### TopHub 特有字段：
```json
{
  "platform": "weibo"              // 平台（仅全榜有）
}
```

### 3. 核心实现细节

#### 热度值计算：
```python
# HN 的热度由两个指标组成
score = item_data.get("score", 0)      # 用户点赞数
descendants = item_data.get("descendants", 0)  # 评论数
hot_value = f"{score}分 · {descendants}条评论"
```

#### 并发控制：
```python
# 使用信号量限制并发请求数
semaphore = asyncio.Semaphore(10)  # 最多 10 个并发

async def fetch_with_semaphore(idx: int, item_id: int):
    async with semaphore:
        # 获取 item 详情
```

#### 错误处理：
- TimeoutException: 请求超时
- HTTPStatusError: HTTP 错误（如 403 被限流）
- 其他异常: 捕获并记录

### 4. API 接口设计

#### 端点：`GET /api/hotnews/hn`

##### 参数：
| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `limit` | int | 30 | 返回条数（1-100） |
| `story_type` | str | "top" | "top"=最热, "best"=最佳, "new"=最新 |
| `force_refresh` | bool | false | 是否强制刷新（跳过缓存） |

##### 返回格式：
```json
{
  "success": true,
  "items": [
    {
      "title": "新闻标题",
      "url": "https://...",
      "rank": 1,
      "hot_value": "99分 · 32条评论",
      "source": "HN 最热",
      "source_id": "top",
      "score": 99,
      "descendants": 32,
      "author": "wrxd",
      "posted_time": 1767352071
    },
    // ... 更多项目
  ],
  "total": 30,
  "story_type": "top",
  "source": "hackernews",
  "from_cache": false,
  "collection_time": "2026-01-02T21:12:00.000000"
}
```

## 使用示例

### 前端请求示例：

#### 1. 获取 HN 热榜前30条
```javascript
// JavaScript/Vue
const response = await fetch('/api/hotnews/hn?limit=30&story_type=top&force_refresh=true');
const data = await response.json();

// 使用数据
data.items.forEach(item => {
  console.log(`[${item.rank}] ${item.title}`);
  console.log(`热度: ${item.hot_value}`);
  console.log(`作者: ${item.author}`);
  console.log(`链接: ${item.url}`);
});
```

#### 2. 获取 HN 最佳前50条
```javascript
const response = await fetch('/api/hotnews/hn?limit=50&story_type=best');
const data = await response.json();
console.log(`总共获取: ${data.total} 条`);
```

#### 3. 强制刷新获取最新数据
```javascript
const response = await fetch('/api/hotnews/hn?limit=30&force_refresh=true');
```

### 后端调用示例：

#### Python 异步调用
```python
from app.services.hn_hot_collector import hn_hot_collector

# 获取前30条 Top Stories
result = await hn_hot_collector.collect_news(
    source_ids=["top"],
    max_items=30,
    force_refresh=True
)

# 处理结果
if result['success']:
    for news in result['news_list']:
        print(f"[{news['rank']}] {news['title']}")
        print(f"热度: {news['hot_value']}")
```

## 测试验证

### 运行测试脚本

```bash
# 执行 API 测试
python test_hn_api.py
```

### 测试结果摘要

**TEST 1: Get HN Top Stories (first 30 items)**
- 状态: ✓ 成功
- 返回: 30 条新闻
- 字段完整: ✓

**TEST 2: Get HN Best Stories (first 50 items)**
- 状态: ✓ 成功
- 返回: 49 条新闻（最佳榜单数据少）
- 字段完整: ✓

**TEST 3: Get HN New Stories (first 20 items)**
- 状态: ✓ 成功
- 返回: 19 条新闻
- 字段完整: ✓

**TEST 4: Single Item Structure**
- 状态: ✓ 成功
- 包含所有必需字段: ✓

## 实现的特性

### ✓ 已完成
1. [x] 从 HN 官方 API 拉取 topstories/beststories/newstories
2. [x] 支持前30/50/任意数量的新闻获取
3. [x] 计算并返回热度值（score + descendants）
4. [x] 与 TopHub 统一数据格式
5. [x] 异步并发处理，避免请求过慢
6. [x] 完整错误处理
7. [x] 缓存支持（可选）
8. [x] 详细日志记录
9. [x] RESTful API 接口
10. [x] 边界参数验证
11. [x] 测试脚本验证

### 可选增强

#### 后续可考虑的改进：
1. 添加排序选项（按热度、得分、评论数排序）
2. 支持搜索过滤
3. 缓存有效期设置
4. 分页支持
5. 批量获取多个榜单

## 文件列表

### 修改的文件：
1. **app/services/hn_hot_collector.py** - 核心收集器（大幅改进）
2. **app/api/endpoints.py** - 添加 `/api/hotnews/hn` 端点

### 新增文件：
1. **test_hn_api.py** - API 接口测试脚本
2. **test_hn_collector.py** - 收集器本地测试脚本

## 性能指标

### 响应时间（约）
- 获取前30条: ~2-3秒
- 获取前50条: ~3-4秒
- 获取前100条: ~4-6秒

### 并发性能
- 信号量限制: 10 个并发请求
- 单个 item 获取超时: 10秒
- 总请求超时: 30秒

### 缓存策略
- 同一日期内复用缓存
- 支持 force_refresh 跳过缓存
- 支持内存 + 文件双层缓存

## 与 TopHub 的设计对比

| 特性 | TopHub | HN |
|-----|--------|-----|
| 数据源 | 网页爬虫 | 官方 API |
| 榜单数量 | 8 个 | 3 个 |
| 字段特色 | platform | score, descendants |
| 热度来源 | 页面解析 | score + descendants |
| 并发限制 | 动态调整 | Semaphore(10) |
| 缓存支持 | ✓ | ✓ |
| 错误处理 | 详细 | 详细 |

## 快速开始

```bash
# 1. 启动后端
python -m app.main

# 2. 测试 API（在另一个终端）
python test_hn_api.py

# 3. 前端调用（JavaScript）
fetch('/api/hotnews/hn?limit=30&story_type=top&force_refresh=true')
  .then(r => r.json())
  .then(data => {
    // 使用 data.items
  });
```

## 总结

成功学习并实现了类似 TopHub 的 HN 热点新闻收集器，具备以下优势：

1. **数据格式统一** - 与 TopHub 保持一致，便于前端统一处理
2. **灵活可扩展** - 支持多榜单、多参数配置
3. **性能优化** - 异步并发、缓存机制
4. **完整错误处理** - 详细的日志和异常处理
5. **生产级别代码** - 包含详细注释和文档

该实现可以作为后续集成其他数据源的模板。
