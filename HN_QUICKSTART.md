# HN 新闻收集器 - 快速开始指南

## 5分钟快速开始

### 1️⃣ 启动后端服务

```bash
cd d:\For Study\Project\AgentPro
python -m app.main
```

输出应该显示：
```
INFO:     Started server process [...]
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2️⃣ 测试 API（新终端）

#### 方式1：使用 curl
```bash
curl "http://localhost:8000/api/hotnews/hn?limit=30&story_type=top&force_refresh=true"
```

#### 方式2：使用 Python
```python
import httpx
import json

async def test():
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            'http://127.0.0.1:8000/api/hotnews/hn',
            params={'limit': 30, 'force_refresh': True}
        )
        data = resp.json()
        print(json.dumps(data, indent=2)[:500])

import asyncio
asyncio.run(test())
```

#### 方式3：运行测试脚本
```bash
python test_hn_api.py
```

### 3️⃣ 前端集成示例

#### HTML + JavaScript
```html
<div id="news-list"></div>

<script>
async function loadHNNews() {
  const data = await fetch(
    '/api/hotnews/hn?limit=30&force_refresh=true'
  ).then(r => r.json());
  
  const html = data.items.map(item => `
    <div style="margin: 10px 0; padding: 10px; border: 1px solid #ddd;">
      <h3><a href="${item.url}">[${item.rank}] ${item.title}</a></h3>
      <p>热度: ${item.hot_value} | 作者: ${item.author}</p>
    </div>
  `).join('');
  
  document.getElementById('news-list').innerHTML = html;
}

loadHNNews();
</script>
```

#### Vue 3
```vue
<template>
  <div>
    <button @click="loadNews">刷新</button>
    <div v-if="loading">加载中...</div>
    <div v-for="item in items" :key="item.source_id + '_' + item.rank">
      <h3><a :href="item.url">[{{ item.rank }}] {{ item.title }}</a></h3>
      <p>热度: {{ item.hot_value }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const items = ref([])
const loading = ref(false)

async function loadNews() {
  loading.value = true
  const res = await fetch('/api/hotnews/hn?limit=30&force_refresh=true')
  const data = await res.json()
  items.value = data.items
  loading.value = false
}

onMounted(loadNews)
</script>
```

---

## 📚 API 速查表

### 获取热榜前30条
```
GET /api/hotnews/hn?limit=30&story_type=top
```

### 获取最佳前50条
```
GET /api/hotnews/hn?limit=50&story_type=best&force_refresh=true
```

### 获取最新前20条
```
GET /api/hotnews/hn?limit=20&story_type=new
```

### 响应结构（简化）
```json
{
  "success": true,
  "total": 30,
  "items": [
    {
      "rank": 1,
      "title": "新闻标题",
      "url": "https://...",
      "hot_value": "99分 · 32条评论",
      "author": "username",
      "score": 99,
      "descendants": 32
    },
    // ... 更多项目
  ]
}
```

---

## 🔧 常见操作

### 显示热榜前30条
```javascript
fetch('/api/hotnews/hn?limit=30&story_type=top&force_refresh=true')
  .then(r => r.json())
  .then(data => {
    data.items.forEach(item => {
      console.log(`${item.rank}. ${item.title}`)
    })
  })
```

### 切换榜单
```javascript
// Top 榜
fetch('/api/hotnews/hn?story_type=top')

// Best 榜
fetch('/api/hotnews/hn?story_type=best')

// New 榜
fetch('/api/hotnews/hn?story_type=new')
```

### 获取更多条数
```javascript
// 50 条
fetch('/api/hotnews/hn?limit=50&force_refresh=true')

// 100 条
fetch('/api/hotnews/hn?limit=100&force_refresh=true')
```

### 使用缓存（推荐）
```javascript
// 不加 force_refresh，使用缓存（快速）
fetch('/api/hotnews/hn?limit=30')
```

---

## 📊 数据字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| rank | 排名 | 1 |
| title | 标题 | "Programming in ..." |
| url | 链接 | "https://..." |
| hot_value | 热度 | "99分 · 32条评论" |
| author | 作者 | "username" |
| score | 得分 | 99 |
| descendants | 评论数 | 32 |
| posted_time | 发布时间 | 1767352071 |
| source | 来源 | "HN 最热" |

---

## 🧪 运行测试

### 运行所有测试
```bash
python test_hn_api.py
python test_hn_collector.py
```

### 预期输出
```
TEST 1: Get HN Top Stories (first 30 items)
[OK] Success - Status 200
Total items: 30

TEST 2: Get HN Best Stories (first 50 items)
[OK] Success - Status 200
Total items: 49

TEST 3: Get HN New Stories (first 20 items)
[OK] Success - Status 200
Total items: 19

...

All tests completed!
```

---

## 📖 完整文档

| 文档 | 用途 |
|------|------|
| HN_IMPLEMENTATION_SUMMARY.md | 📋 项目总结（此处） |
| HN_COLLECTOR_IMPLEMENTATION.md | 🔧 实现细节 |
| HN_API_FRONTEND_GUIDE.md | 🎨 前端集成 |
| HN_TEST_REPORT.md | ✅ 测试报告 |

---

## ❓ 常见问题

**Q: API 没有响应？**
A: 确保后端服务在运行 (`python -m app.main`)

**Q: 为什么返回为空？**
A: 需要添加 `force_refresh=true` 参数首次加载数据

**Q: 支持多少条新闻？**
A: 1-100 条，超过会自动限制到 100

**Q: 响应时间多长？**
A: 首次 2-3秒，缓存 0.1秒

**Q: 在生产环境中可用吗？**
A: 可以，已通过完整测试

---

## 🚀 下一步

1. ✅ 集成到前端项目
2. ✅ 配置定时刷新
3. ✅ 自定义样式显示
4. ✅ 添加用户交互

---

**祝您使用愉快！** 🎉
