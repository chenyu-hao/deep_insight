# API 接口文档

## 基础信息
- Base URL: `http://localhost:8000/api`
- 所有接口都支持 CORS

---

## 1. 完整工作流分析

### `POST /api/analyze`
执行完整的工作流（爬取 → 分析 → 创作），支持平台选择

**请求体：**
```json
{
  "topic": "主题",
  "urls": [],  // 可选：URL列表
  "platforms": ["wb", "bili", "xhs"]  // 可选：指定平台，不传则使用默认平台
}
```

**响应：** SSE 流式输出
```
data: {"agent_name": "Crawler_agent", "step_content": "...", "status": "thinking"}
data: {"agent_name": "Reporter", "step_content": "...", "status": "thinking"}
...
data: {"agent_name": "System", "step_content": "Analysis Complete", "status": "finished"}
```

**说明：**
- `platforms` 字段支持根据前端勾选框选择平台
- 支持的平台：`wb`(微博), `bili`(B站), `xhs`(小红书), `dy`(抖音), `ks`(快手), `tieba`(贴吧), `zhihu`(知乎)
- 如果不传 `platforms`，将使用配置中的默认平台

---

## 2. 配置管理

### `GET /api/config`
获取当前配置

**响应：**
```json
{
  "llm_providers": {
    "reporter": [
      {"provider": "deepseek", "model": "deepseek-chat"},
      {"provider": "moonshot", "model": "kimi-k2-turbo-preview"}
    ],
    "analyst": [...],
    "debater": [...],
    "writer": [...]
  },
  "crawler_limits": {
    "wb": {"max_items": 5, "max_comments": 10},
    "bili": {"max_items": 5, "max_comments": 10},
    ...
  },
  "debate_max_rounds": 4,
  "default_platforms": ["wb", "bili"]
}
```

### `PUT /api/config`
更新配置（部分更新）

**请求体：**
```json
{
  "debate_max_rounds": 6,  // 可选
  "crawler_limits": {  // 可选
    "wb": {"max_items": 10, "max_comments": 20}
  },
  "default_platforms": ["wb", "xhs"]  // 可选
}
```

**响应：**
```json
{
  "success": true,
  "message": "配置已更新: debate_max_rounds, crawler_limits.wb",
  "updated_fields": ["debate_max_rounds", "crawler_limits.wb"]
}
```

---

## 3. 历史输出文件

### `GET /api/outputs`
获取历史输出文件列表

**查询参数：**
- `limit`: 返回数量限制（默认20）
- `offset`: 偏移量（默认0）

**响应：**
```json
{
  "files": [
    {
      "filename": "2025-12-30_17-57-36_武汉大学图书馆.md",
      "topic": "武汉大学图书馆",
      "created_at": "2025-12-30T17:57:36",
      "size": 12345
    },
    ...
  ],
  "total": 50
}
```

### `GET /api/outputs/{filename}`
获取指定输出文件的内容

**路径参数：**
- `filename`: 文件名（如：`2025-12-30_17-57-36_武汉大学图书馆.md`）

**响应：**
```json
{
  "filename": "2025-12-30_17-57-36_武汉大学图书馆.md",
  "content": "# 武汉大学图书馆\n\n## 最终文案\n\n...",
  "created_at": "2025-12-30T17:57:36"
}
```

**错误：**
- `404`: 文件不存在
- `400`: 无效的文件名

---

## 4. 工作流状态

### `GET /api/workflow/status`
获取当前工作流执行状态

**响应（无运行任务）：**
```json
{
  "running": false,
  "current_step": null,
  "progress": 0,
  "started_at": null,
  "topic": null
}
```

**响应（有运行任务）：**
```json
{
  "running": true,
  "current_step": "analyst",
  "progress": 50,
  "started_at": "2025-12-30T20:00:00",
  "topic": "武汉大学图书馆"
}
```

**进度说明：**
- `crawler_agent`: 10%
- `reporter`: 30%
- `analyst`: 50%
- `debater`: 70%
- `writer`: 90%
- `finished`: 100%

---

## 接口使用示例

### 前端调用示例（JavaScript）

```javascript
// 1. 获取配置
const config = await fetch('http://localhost:8000/api/config').then(r => r.json());

// 2. 更新配置
await fetch('http://localhost:8000/api/config', {
  method: 'PUT',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    debate_max_rounds: 6,
    default_platforms: ['wb', 'xhs']
  })
});

// 3. 执行分析（支持平台选择）
const eventSource = new EventSource(
  'http://localhost:8000/api/analyze?' + 
  new URLSearchParams({
    topic: '测试主题',
    platforms: JSON.stringify(['wb', 'bili'])
  })
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.agent_name, data.step_content);
};

// 4. 获取工作流状态
const status = await fetch('http://localhost:8000/api/workflow/status')
  .then(r => r.json());

// 5. 获取历史文件列表
const files = await fetch('http://localhost:8000/api/outputs?limit=10')
  .then(r => r.json());

// 6. 获取文件内容
const content = await fetch('http://localhost:8000/api/outputs/2025-12-30_17-57-36_武汉大学图书馆.md')
  .then(r => r.json());
```

---

## 注意事项

1. **平台选择**：`/api/analyze` 接口的 `platforms` 字段支持前端通过勾选框动态选择
2. **配置更新**：配置更新是内存中的，重启服务后会恢复默认值（如需持久化，需要额外实现）
3. **文件安全**：`/api/outputs/{filename}` 接口已做路径遍历攻击防护
4. **工作流状态**：状态是实时更新的，前端可以轮询获取最新状态
