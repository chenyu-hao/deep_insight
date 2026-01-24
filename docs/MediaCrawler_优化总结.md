# MediaCrawler 登录机制优化总结

**日期**: 2026-01-24
**作者**: Antigravity (AI Assistant)
**关联服务**: `MediaCrawler Service`

## 1. 问题背景
在优化 MediaCrawler 的用户体验时，我们试图实现“静默爬取”（Headless Mode），即在检测到曾经登录过的情况下，不再弹窗要求扫码。

**遇到的问题**：
B站（Bilibili）陷入了“登录死循环”。
1. 系统检测到存在历史数据（`bili_user_data_dir`）。
2. 系统因此判定“已登录”，并强制开启了 **Headless Mode** 和 **CDP Mode**（高级抗检测模式）。
3. 爬虫启动后，因为 **CDP Mode 使用独立的用户数据目录** (`cdp_...`)，无法读取到旧版（Standard Mode）的 `bili_user_data_dir` 中的登录 Cookie。
4. 结果：爬虫在静默模式下启动，但处于“未登录”状态，导致爬取失败。
5. 下次运行：系统依然检测到旧数据存在，再次进入死循环。

## 2. 根本原因
**MediaCrawler 的各种模式数据隔离机制**：
*   **Standard Mode** (Headless=False/True): 数据存储在 `browser_data/{platform}_user_data_dir`。
*   **CDP Mode** (Enable CDP=True): 数据存储在 `browser_data/cdp_{platform}_user_data_dir`。

这两个目录的数据**不互通**。若强行切换模式，会导致登录态丢失。

## 3. 解决方案：智能模式选择 (Smart Mode Selection)

我们在 `app/services/media_crawler_service.py` 中实现了更智能的启动逻辑：

### 核心逻辑
不再一刀切地开启 CDP 模式，而是根据**现存的数据目录类型**来决定启动参数。

1.  **优先检测 CDP 数据** (`cdp_{platform}_user_data_dir`)：
    *   如果存在 -> 说明用户是在 CDP 模式下登录的。
    *   **Action**: 开启 `HEADLESS=True` + `ENABLE_CDP_MODE=True`。
    
2.  **检测标准数据** (`{platform}_user_data_dir`)：
    *   如果只存在标准数据（无 CDP 数据） -> 说明用户是在旧版普通模式下登录的。
    *   **Action**: 开启 `HEADLESS=True`，但 **强制关闭 CDP (`ENABLE_CDP_MODE=False`)**。
    *   **效果**: 爬虫会复用旧版数据目录，成功识别登录态。

3.  **无数据**：
    *   **Action**: `HEADLESS=False`，弹出浏览器让用户扫码。默认使用 CDP 模式（为未来积累 CDP 数据）。

### 代码变更片段
```python
                    # Smart Mode Selection: Use CDP only if we have CDP data or Cookies (defaulting to CDP for fresh cookies)
                    # If we ONLY have standard data, force standard mode to retain login
                    if has_cdp_data:
                        mc_config.ENABLE_CDP_MODE = True
                        mode_name = "CDP模式"
                    elif has_standard_data:
                        mc_config.ENABLE_CDP_MODE = False  # <--- 关键修正：复用旧数据
                        mode_name = "普通模式"
                    else:
                        mc_config.ENABLE_CDP_MODE = True
                        mode_name = "CDP模式(基于Cookie)"
```

## 4. 验证结果
*   **小红书 (Xiaohongshu)**: 继续正常运行（可能拥有 CDP 数据或无需强登录）。
*   **B站 (Bilibili)**: 系统识别到仅有 `bili_user_data_dir`，自动切换回“普通模式”启动静默爬虫，成功读取旧 Cookie，恢复登录状态。

## 5. 建议
无需用户手动干预。系统会自动适配现有的数据文件夹。
如果用户希望迁移到 CDP 模式（更稳定），可以删除 `browser_data` 下的所有文件夹，重新触发一次弹窗扫码即可。
