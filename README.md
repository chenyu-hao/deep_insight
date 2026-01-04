# AgentPro - 多阶段舆情解读与热点对齐系统（Multi-Stage Public Opinion Interpretation Agent System）

## 项目名称
**AgentPro：多阶段舆情解读与热点对齐系统**

## 运行环境
- **Python**：3.10+（推荐 3.11）
- **Node.js**：16+（推荐 18+）
- **包管理**：pip / npm

## 依赖库及安装命令

### 后端（FastAPI + 多Agent工作流）
在项目根目录执行：

```bash
pip install -r requirements.txt
```

### 前端（Vue + Vite + Tailwind）
在项目根目录执行：

```bash
npm install
```

## 详细运行步骤（评委一步步复现）

### 1. 启动后端 API 服务
在项目根目录执行：

```bash
python -m app.main
```

默认后端地址：
- `http://127.0.0.1:8000`
- API 前缀：`/api`

> 如需使用不同端口，请查看 `app/main.py` 中的启动配置，或使用你自己的 uvicorn 启动命令。

### 2. 启动前端开发服务器
新开一个终端，在项目根目录执行：

```bash
npm run dev
```

Vite 默认地址一般为：
- `http://127.0.0.1:5173`

### 3. 使用方式（推荐演示路径）
- 打开前端首页（Home）输入议题 → 启动分析（SSE 实时日志）
- 在 HotView 热榜页：刷新热榜 → 切平台（全榜数据本地筛选）→ 点选单条热点生成“演化解读卡”
- 在 DataView：切换数据源（workflow/hotnews）→ 查看“平台热度对比 / 关键词 / 情感等”图表

## 项目结构说明（简要）
- `app/`：后端（FastAPI、LLM Agent、爬虫/热榜、对齐聚类、缓存）
- `src/`：前端（Vue3、Pinia、Tailwind、图表与可视化）
- `MediaCrawler/`：第三方/子模块级爬虫能力（项目内集成使用）

## 交付物建议打包方式
- **Project_SourceCode**：直接将整个项目目录压缩为 zip（包含本 README）
- **Project_Documentation**：见 `Project_Documentation/` 目录（可导出为 PDF）

