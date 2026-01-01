# 热点新闻收集 Agent 使用说明

## 功能概述

热点新闻收集 Agent 是一个定时任务，用于从多个平台自动收集热点新闻。该 Agent 会在应用启动时自动启动，并按照设定的时间定时执行。

## 支持的新闻源

- **weibo**: 微博热搜
- **zhihu**: 知乎热榜
- **bilibili-hot-search**: B站热搜
- **douyin**: 抖音热榜
- **tieba**: 百度贴吧

## 安装依赖

首先安装必要的依赖包：

```bash
pip install httpx apscheduler loguru
```

或者使用 requirements.txt：

```bash
pip install -r requirements.txt
```

## 配置

### 定时任务配置

默认配置在 `app/services/hot_news_scheduler.py` 中，默认每天上午 9:00 执行。

如需修改执行时间，可以在 `app/main.py` 中修改：

```python
hot_news_scheduler.start(hour=9, minute=0)  # 修改为其他时间
```

### 新闻源配置

默认会收集所有支持的新闻源。如需指定特定新闻源，可以通过 API 接口指定。

## API 接口

### 1. 手动触发热点新闻收集

```http
POST /api/hot-news/collect
Content-Type: application/json

{
  "sources": ["weibo", "zhihu"]  // 可选，不指定则收集所有源
}
```

**响应示例：**
```json
{
  "success": true,
  "total_news": 150,
  "successful_sources": 12,
  "total_sources": 12,
  "news_list": [...],  // 所有新闻列表（最多100条）
  "news_by_platform": {
    "微博热搜": [
      {"rank": 1, "title": "...", "url": "...", "source": "weibo", "source_name": "微博热搜"},
      ...
    ],
    "知乎热榜": [...],
    "B站热搜": [...]
  },
  "collection_time": "2024-01-01T09:00:00"
}
```

### 2. 获取定时任务状态

```http
GET /api/hot-news/status
```

**响应示例：**
```json
{
  "is_running": true,
  "last_run_time": "2024-01-01T09:00:00",
  "last_result": {
    "success": true,
    "total_news": 150,
    ...
  }
}
```

### 3. 立即执行一次收集（测试用）

```http
POST /api/hot-news/run-once
```

## 使用方式

### 方式1: 自动定时执行（推荐）

1. 启动应用：
   ```bash
   python -m app.main
   # 或
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. 定时任务会在应用启动时自动启动，按照配置的时间定时执行。

### 方式2: 手动触发

通过 API 接口手动触发热点新闻收集：

```bash
curl -X POST http://localhost:8000/api/hot-news/collect \
  -H "Content-Type: application/json" \
  -d '{"sources": ["weibo", "zhihu"]}'
```

### 方式3: 测试脚本

使用提供的测试脚本：

**测试所有平台（默认）：**
```bash
python test_hot_news.py
```

**测试指定平台：**
```bash
python test_hot_news.py --sources weibo zhihu bilibili-hot-search
```

**每个平台显示前20条热点：**
```bash
python test_hot_news.py --top 20
```

**列出所有支持的新闻源：**
```bash
python test_hot_news.py --list-sources
```

**组合使用：**
```bash
# 测试微博、知乎、B站，每个平台显示前5条
python test_hot_news.py --sources weibo zhihu bilibili-hot-search --top 5
```

## 代码结构

```
app/
├── services/
│   ├── hot_news_collector.py    # 新闻收集器核心逻辑
│   └── hot_news_scheduler.py    # 定时任务调度器
├── api/
│   └── endpoints.py              # API 接口定义
└── main.py                        # 应用入口，集成定时任务
```

## 注意事项

1. **API 限制**: 新闻 API 可能有请求频率限制，代码中已添加 0.5 秒的延迟以避免过快请求。

2. **网络连接**: 确保服务器能够访问 `https://newsnow.busiyi.world`。

3. **日志记录**: 使用 `loguru` 进行日志记录，所有操作都会记录日志。

4. **数据存储**: 当前版本只实现了新闻收集功能，数据存储功能可以根据需要后续添加（参考提供的数据库管理器代码）。

## 后续扩展

如果需要将收集的新闻存储到数据库，可以参考提供的 `DatabaseManager` 代码：

1. 创建数据库表（`daily_news` 和 `daily_topics`）
2. 在收集器中集成数据库保存功能
3. 添加查询接口用于查看历史新闻

## 故障排查

### 问题1: 导入错误

如果遇到 `ModuleNotFoundError`，请确保已安装所有依赖：
```bash
pip install httpx apscheduler loguru
```

### 问题2: 定时任务未执行

检查：
1. 应用是否正常启动
2. 查看日志确认定时任务是否已启动
3. 检查系统时间是否正确

### 问题3: 新闻收集失败

检查：
1. 网络连接是否正常
2. API 服务是否可访问
3. 查看日志中的详细错误信息

## 开发说明

- 定时任务使用 `APScheduler` 实现，支持灵活的调度配置
- 新闻收集使用 `httpx` 进行异步 HTTP 请求
- 所有操作都有详细的日志记录，便于调试和监控
