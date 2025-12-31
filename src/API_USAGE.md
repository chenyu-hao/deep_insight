# 前端 API 使用说明

## 新增功能

### 1. API 服务 (`src/api/index.js`)
统一管理所有后端接口调用，包括：
- `analyze()` - 执行工作流分析
- `getConfig()` - 获取配置
- `updateConfig()` - 更新配置
- `getOutputFiles()` - 获取历史文件列表
- `getOutputFile()` - 获取文件内容
- `getWorkflowStatus()` - 获取工作流状态

### 2. Store 管理

#### `src/stores/config.js` - 配置管理
- `fetchConfig()` - 获取配置
- `updateConfig()` - 更新配置
- Getters: `llmProviders`, `crawlerLimits`, `debateMaxRounds`, `defaultPlatforms`

#### `src/stores/outputs.js` - 输出文件管理
- `fetchFiles()` - 获取文件列表
- `fetchFileContent()` - 获取文件内容
- `clearCurrentFile()` - 清除当前文件

#### `src/stores/workflow.js` - 工作流状态管理
- `fetchStatus()` - 获取状态
- `startPolling()` - 开始轮询
- `stopPolling()` - 停止轮询

#### `src/stores/analysis.js` - 分析工作流（已更新）
- 新增 `selectedPlatforms` - 选中的平台
- 新增 `setSelectedPlatforms()` - 设置选中的平台
- 新增 `availablePlatforms` getter - 可用平台列表

### 3. 新增组件

#### `ConfigPanel.vue` - 配置面板
- 显示和编辑配置
- 支持更新辩论轮数、默认平台、爬虫限制

#### `OutputFiles.vue` - 历史文件列表
- 显示所有历史输出文件
- 支持分页浏览
- 点击文件可加载内容

#### `WorkflowStatus.vue` - 工作流状态
- 实时显示工作流执行状态
- 显示进度条和当前步骤
- 自动轮询更新

#### `NewsInput.vue` - 输入组件（已更新）
- 新增平台选择功能
- 支持多选平台
- 选中的平台会传递给后端

## 使用示例

### 在组件中使用 API

```javascript
import { api } from '../api';

// 获取配置
const config = await api.getConfig();

// 更新配置
await api.updateConfig({
  debate_max_rounds: 6,
  default_platforms: ['wb', 'xhs']
});

// 获取历史文件
const files = await api.getOutputFiles(20, 0);

// 获取工作流状态
const status = await api.getWorkflowStatus();
```

### 在组件中使用 Store

```javascript
import { useConfigStore } from '../stores/config';
import { useOutputsStore } from '../stores/outputs';
import { useWorkflowStore } from '../stores/workflow';

const configStore = useConfigStore();
const outputsStore = useOutputsStore();
const workflowStore = useWorkflowStore();

// 获取配置
await configStore.fetchConfig();

// 更新配置
await configStore.updateConfig({ debate_max_rounds: 6 });

// 获取文件列表
await outputsStore.fetchFiles(20, 0);

// 获取工作流状态（带轮询）
workflowStore.startPolling(2000); // 每2秒轮询一次
```

## 界面布局

新的界面布局：
```
┌─────────────────────────────────────────────┐
│  主工作区（3列）                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ NewsInput │ │Thinking  │ │Xiaohongshu│  │
│  │           │ │Chain     │ │Card      │   │
│  └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  管理和状态区（3列）                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │Workflow │ │Config    │ │Output    │   │
│  │Status   │ │Panel     │ │Files     │   │
│  └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────┘
```

## 平台选择功能

在 `NewsInput` 组件中：
- 用户可以通过勾选框选择要爬取的平台
- 如果未选择任何平台，将使用配置中的默认平台
- 选中的平台会通过 `platforms` 字段传递给后端

支持的平台代码：
- `wb` - 微博
- `bili` - B站
- `xhs` - 小红书
- `dy` - 抖音
- `ks` - 快手
- `tieba` - 贴吧
- `zhihu` - 知乎
