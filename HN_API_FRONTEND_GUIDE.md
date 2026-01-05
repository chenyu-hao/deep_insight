# HN 新闻收集器 - 前端集成指南

## API 端点说明

### 基础URL
```
GET /api/hotnews/hn
```

### 请求参数

| 参数 | 类型 | 默认值 | 范围 | 说明 |
|------|------|--------|------|------|
| `limit` | integer | 30 | 1-100 | 返回新闻条数 |
| `story_type` | string | "top" | top\|best\|new | 榜单类型 |
| `force_refresh` | boolean | false | true\|false | 强制刷新（跳过缓存） |

### 返回数据结构

#### 成功响应 (Status 200)
```json
{
  "success": true,
  "items": [
    {
      "title": "10 years of personal finances in plain text files",
      "url": "https://sgoel.dev/posts/10-years-of-personal-finances-in-plain-text-files/",
      "rank": 1,
      "hot_value": "99分 · 32条评论",
      "source": "HN 最热",
      "source_id": "top",
      "score": 99,
      "descendants": 32,
      "author": "wrxd",
      "posted_time": 1767352071
    },
    {
      "title": "FracturedJson",
      "url": "https://github.com/j-brooke/FracturedJson/wiki",
      "rank": 2,
      "hot_value": "20分 · 2条评论",
      "source": "HN 最热",
      "source_id": "top",
      "score": 20,
      "descendants": 2,
      "author": "PretzelFisch",
      "posted_time": 1767357991
    }
  ],
  "total": 30,
  "story_type": "top",
  "source": "hackernews",
  "from_cache": false,
  "collection_time": "2026-01-02T21:12:00.000000"
}
```

#### 错误响应 (Status 500)
```json
{
  "detail": "HN 热榜抓取失败: 错误信息"
}
```

## 使用示例

### Vue 3 组合式API

```javascript
import { ref, computed } from 'vue'

export default {
  setup() {
    const hnNews = ref([])
    const loading = ref(false)
    const storyType = ref('top')
    const limit = ref(30)
    const error = ref(null)

    // 获取 HN 新闻
    const fetchHNNews = async (forceRefresh = false) => {
      loading.value = true
      error.value = null
      
      try {
        const params = {
          limit: limit.value,
          story_type: storyType.value,
          force_refresh: forceRefresh
        }
        
        const queryString = new URLSearchParams(params).toString()
        const response = await fetch(`/api/hotnews/hn?${queryString}`)
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        
        const data = await response.json()
        
        if (data.success) {
          hnNews.value = data.items
        } else {
          error.value = data.detail || '获取失败'
        }
      } catch (err) {
        error.value = err.message
        console.error('HN 新闻获取失败:', err)
      } finally {
        loading.value = false
      }
    }

    return {
      hnNews,
      loading,
      storyType,
      limit,
      error,
      fetchHNNews
    }
  }
}
```

### React Hooks

```javascript
import { useState, useEffect } from 'react'

export function HNNewsList() {
  const [news, setNews] = useState([])
  const [loading, setLoading] = useState(false)
  const [storyType, setStoryType] = useState('top')
  const [limit, setLimit] = useState(30)

  const fetchNews = async (forceRefresh = false) => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        limit,
        story_type: storyType,
        force_refresh: forceRefresh
      })
      
      const response = await fetch(`/api/hotnews/hn?${params}`)
      const data = await response.json()
      
      if (data.success) {
        setNews(data.items)
      }
    } catch (error) {
      console.error('Error fetching HN news:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchNews()
  }, [storyType, limit])

  return (
    <div className="hn-news-container">
      <div className="controls">
        <select 
          value={storyType} 
          onChange={(e) => setStoryType(e.target.value)}
        >
          <option value="top">最热 (Top)</option>
          <option value="best">最佳 (Best)</option>
          <option value="new">最新 (New)</option>
        </select>
        
        <input 
          type="number" 
          min="1" 
          max="100" 
          value={limit}
          onChange={(e) => setLimit(e.target.value)}
          placeholder="数量"
        />
        
        <button onClick={() => fetchNews(true)}>刷新</button>
      </div>

      {loading && <p>加载中...</p>}

      <div className="news-list">
        {news.map((item) => (
          <div key={item.source_id + '_' + item.rank} className="news-item">
            <h3>
              <a href={item.url} target="_blank" rel="noopener noreferrer">
                [{item.rank}] {item.title}
              </a>
            </h3>
            <div className="meta">
              <span className="hot-value">{item.hot_value}</span>
              <span className="author">by {item.author}</span>
              <span className="score">得分: {item.score}</span>
              <span className="comments">评论: {item.descendants}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

### 原生 JavaScript

```javascript
// 获取 HN 新闻的简单函数
async function getHNNews(limit = 30, storyType = 'top', forceRefresh = false) {
  const params = new URLSearchParams({
    limit,
    story_type: storyType,
    force_refresh: forceRefresh
  });
  
  const response = await fetch(`/api/hotnews/hn?${params}`);
  const data = await response.json();
  
  return data;
}

// 使用示例
getHNNews(30, 'top', true).then(data => {
  if (data.success) {
    console.log('获取的新闻数:', data.items.length);
    
    data.items.forEach(item => {
      console.log(`[${item.rank}] ${item.title}`);
      console.log(`  热度: ${item.hot_value}`);
      console.log(`  作者: ${item.author}`);
      console.log(`  链接: ${item.url}`);
    });
  }
});
```

## 数据字段说明

### 返回项目的字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `title` | string | 新闻标题 | "10 years of personal finances..." |
| `url` | string | 原始链接（外部链接） | "https://sgoel.dev/..." |
| `rank` | integer | 排名（1-100） | 1 |
| `hot_value` | string | 格式化热度值 | "99分 · 32条评论" |
| `source` | string | 来源名称 | "HN 最热" |
| `source_id` | string | 来源ID | "top" |
| `score` | integer | HN 得分（点赞数） | 99 |
| `descendants` | integer | 评论数 | 32 |
| `author` | string | 发布者用户名 | "wrxd" |
| `posted_time` | integer | 发布时间（Unix时间戳） | 1767352071 |

### 顶级字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | 请求是否成功 |
| `items` | array | 新闻项目列表 |
| `total` | integer | 返回的新闻条数 |
| `story_type` | string | 榜单类型 |
| `source` | string | 数据源（"hackernews"） |
| `from_cache` | boolean | 是否来自缓存 |
| `collection_time` | string | 数据收集时间（ISO 8601） |

## 常见场景

### 场景1: 显示 HN 热榜前30条

```javascript
// 获取数据
const response = await fetch('/api/hotnews/hn?limit=30&story_type=top')
const { items } = await response.json()

// 渲染
items.forEach(item => {
  const html = `
    <div class="news-item">
      <h3><a href="${item.url}" target="_blank">[${item.rank}] ${item.title}</a></h3>
      <p class="meta">
        热度: ${item.hot_value} | 作者: ${item.author}
      </p>
    </div>
  `
  document.getElementById('news-container').innerHTML += html
})
```

### 场景2: 显示最佳文章前50条

```javascript
const response = await fetch('/api/hotnews/hn?limit=50&story_type=best&force_refresh=true')
const { items } = await response.json()

// 按得分排序（如果需要）
items.sort((a, b) => b.score - a.score)

// 显示
showNewsList(items)
```

### 场景3: 自动刷新

```javascript
// 每5分钟刷新一次
setInterval(() => {
  fetchHNNews(true) // force_refresh=true
}, 5 * 60 * 1000)
```

### 场景4: 响应式切换榜单

```javascript
// HTML
<select id="story-type">
  <option value="top">Top Stories</option>
  <option value="best">Best Stories</option>
  <option value="new">New Stories</option>
</select>

// JavaScript
document.getElementById('story-type').addEventListener('change', (e) => {
  const storyType = e.target.value
  fetchHNNews(storyType, 30) // 切换榜单时刷新
})
```

## 错误处理

### 网络错误
```javascript
try {
  const response = await fetch('/api/hotnews/hn')
  if (!response.ok) {
    console.error(`HTTP Error: ${response.status}`)
  }
} catch (error) {
  console.error('Network error:', error)
}
```

### API 错误
```javascript
const response = await fetch('/api/hotnews/hn')
const data = await response.json()

if (!data.success) {
  console.error('API Error:', data.detail)
}
```

## 性能建议

1. **使用缓存** - 不加 `force_refresh` 参数时会使用缓存
2. **限制条数** - limit 过大会增加响应时间
3. **异步加载** - 在后台加载新闻，不阻塞UI
4. **虚拟滚动** - 大列表用虚拟滚动优化渲染
5. **分页显示** - 如果需要显示100+条，考虑分页

## 常见问题

### Q: 如何让数据保持最新？
A: 添加 `force_refresh=true` 参数跳过缓存：
```javascript
fetch('/api/hotnews/hn?force_refresh=true')
```

### Q: 响应太慢怎么办？
A: 
1. 减少 `limit` 参数（如30而非100）
2. 使用缓存（不添加 force_refresh）
3. 从最常用的榜单开始加载

### Q: 如何转换时间戳？
A:
```javascript
const date = new Date(item.posted_time * 1000)
console.log(date.toLocaleString())
```

### Q: 支持其他榜单吗？
A: 目前支持：
- `top` - 最热 (默认)
- `best` - 最佳
- `new` - 最新

## 参考

- [HN API 文档](https://github.com/HackerNews/API)
- [API 端点文档](./HN_COLLECTOR_IMPLEMENTATION.md)
