# 测试修改记录（用于快速回滚）

> 目的：将每个爬虫平台限制为只爬 1 条数据，加速工作流后续节点测试。测试完成后逐项回滚即可。

---

## 一、MediaCrawler 各平台 per-page 条目切片 (`[:1]`)

> 让每页搜索结果只取第 1 条，不再遍历全部条目。

| # | 文件 | 行号 | 旧代码 | 新代码 |
|---|------|------|--------|--------|
| 1 | `MediaCrawler/media_platform/xhs/core.py` | 166 | `for post_item in notes_res.get("items", {})` | `for post_item in notes_res.get("items", {})[:1]` |
| 2 | `MediaCrawler/media_platform/kuaishou/core.py` | 171 | `for video_detail in vision_search_photo.get("feeds"):` | `for video_detail in vision_search_photo.get("feeds", [])[:1]:` |
| 3 | `MediaCrawler/media_platform/douyin/core.py` | 155 | `for post_item in posts_res.get("data"):` | `for post_item in posts_res.get("data", [])[:1]:` |
| 4 | `MediaCrawler/media_platform/zhihu/core.py` | 189 | `for content in content_list:` | `for content in content_list[:1]:` |
| 5 | `MediaCrawler/media_platform/weibo/core.py` | 194 | `note_list = await self.batch_get_notes_full_text(note_list)` | `note_list = await self.batch_get_notes_full_text(note_list[:1])` |
| 6 | `MediaCrawler/media_platform/bilibili/core.py` | 219 | `task_list = [... for video_item in video_list]` | `task_list = [... for video_item in video_list[:1]]` |
| 7 | `MediaCrawler/media_platform/bilibili/core.py` | 292 | `task_list = [... for video_item in video_list]` | `task_list = [... for video_item in video_list[:1]]` |
| 8 | `MediaCrawler/media_platform/tieba/core.py` | 200 | `note_id_list=[... for note_detail in notes_list]` | `note_id_list=[... for note_detail in notes_list[:1]]` |

---

## 二、MediaCrawler 各平台 limit_count 修改

> 将每个平台内部的翻页阈值从 10/20/50 改为 1。

| # | 文件 | 行号 | 旧值 | 新值 |
|---|------|------|------|------|
| 1 | `MediaCrawler/media_platform/xhs/core.py` | 130 | `xhs_limit_count = 20` | `xhs_limit_count = 1` |
| 2 | `MediaCrawler/media_platform/douyin/core.py` | 120 | `dy_limit_count = 10` | `dy_limit_count = 1` |
| 3 | `MediaCrawler/media_platform/kuaishou/core.py` | 131 | `ks_limit_count = 20` | `ks_limit_count = 1` |
| 4 | `MediaCrawler/media_platform/zhihu/core.py` | 149 | `zhihu_limit_count = 20` | `zhihu_limit_count = 1` |
| 5 | `MediaCrawler/media_platform/weibo/core.py` | 143 | `weibo_limit_count = 10` | `weibo_limit_count = 1` |
| 6 | `MediaCrawler/media_platform/bilibili/core.py` | 186 | `bili_limit_count = 20` | `bili_limit_count = 1` |
| 7 | `MediaCrawler/media_platform/bilibili/core.py` | 243 | `bili_limit_count = 20` | `bili_limit_count = 1` |
| 8 | `MediaCrawler/media_platform/tieba/core.py` | 161 | `tieba_limit_count = 10` | `tieba_limit_count = 1` |
| 9 | `MediaCrawler/media_platform/tieba/core.py` | 220 | `tieba_limit_count = 50` | `tieba_limit_count = 1` |

---

## 三、MediaCrawler 全局上限修改

| # | 文件 | 行号 | 旧值 | 新值 |
|---|------|------|------|------|
| 1 | `MediaCrawler/config/base_config.py` | 83 | `CRAWLER_MAX_NOTES_COUNT = 15` | `CRAWLER_MAX_NOTES_COUNT = 1` |

---

## 四、app 侧调用参数修改

| # | 文件 | 行号 | 旧值 | 新值 |
|---|------|------|------|------|
| 1 | `app/agents/crawler/node.py` | 94 | `max_items=15` | `max_items=1` |

---

## 回滚方法

测试完成后，按上表逐条将「新代码/新值」改回「旧代码/旧值」即可。

也可用 git 回滚：

```bash
# 回滚 MediaCrawler 目录
git checkout -- MediaCrawler/

# 回滚 app/agents/crawler/node.py
git checkout -- app/agents/crawler/node.py
```
