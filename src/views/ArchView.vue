<template>
  <div class="view-section animate-fade-in py-12 px-4">
    <div class="max-w-7xl mx-auto">
      <div class="text-center mb-12">
        <h2 class="text-3xl md:text-4xl font-bold text-slate-900 mb-4">系统技术架构</h2>
        <p class="text-slate-500 text-lg">基于多智能体（Multi-Agent）协作的舆情洞察与内容生成系统</p>
      </div>

      <!-- 整体架构流程图 -->
      <div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl shadow-xl border border-blue-100 p-8 md:p-12 mb-8">
        <h3 class="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
          <Network class="w-6 h-6 text-blue-600" />
          系统架构总览
        </h3>
        <div class="grid md:grid-cols-4 gap-6">
          <!-- 数据收集层 -->
          <div class="bg-white rounded-xl p-5 shadow-md border-2 border-blue-200">
            <div class="flex items-center gap-2 mb-3">
              <Database class="w-5 h-5 text-blue-600" />
              <h4 class="font-bold text-blue-700">数据收集层</h4>
            </div>
            <ul class="text-sm text-slate-600 space-y-2">
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>TopHub Collector<br/>（8个国内平台）</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>HN Collector<br/>（Hacker News）</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>缓存机制<br/>（30分钟TTL）</span>
              </li>
            </ul>
          </div>

          <!-- 数据处理层 -->
          <div class="bg-white rounded-xl p-5 shadow-md border-2 border-purple-200">
            <div class="flex items-center gap-2 mb-3">
              <Cpu class="w-5 h-5 text-purple-600" />
              <h4 class="font-bold text-purple-700">数据处理层</h4>
            </div>
            <ul class="text-sm text-slate-600 space-y-2">
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-purple-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>跨平台对齐聚类</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-purple-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>历史快照分析</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-purple-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>增长/新颖性信号</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-purple-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>前端关键词分类</span>
              </li>
            </ul>
          </div>

          <!-- Agent智能体层 -->
          <div class="bg-white rounded-xl p-5 shadow-md border-2 border-green-200">
            <div class="flex items-center gap-2 mb-3">
              <BrainCircuit class="w-5 h-5 text-green-600" />
              <h4 class="font-bold text-green-700">Agent智能体层</h4>
            </div>
            <ul class="text-sm text-slate-600 space-y-2">
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>Reporter（事实提取）</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>Analyst（舆情分析）</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>Debater（智能辩论）</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>Writer（文案生成）</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>HotNews Interpreter<br/>（演化解读）</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>Translator（查询构建）</span>
              </li>
            </ul>
          </div>

          <!-- 前端交互层 -->
          <div class="bg-white rounded-xl p-5 shadow-md border-2 border-orange-200">
            <div class="flex items-center gap-2 mb-3">
              <Layout class="w-5 h-5 text-orange-600" />
              <h4 class="font-bold text-orange-700">前端交互层</h4>
            </div>
            <ul class="text-sm text-slate-600 space-y-2">
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-orange-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>热榜展示<br/>（实时刷新）</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-orange-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>关键词分类<br/>（300+关键词）</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-orange-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>演化解读卡片<br/>（按需LLM调用）</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-orange-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>舆情推演工作流</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 详细架构说明 -->
      <div class="grid md:grid-cols-2 gap-6 mb-8">
        <!-- 数据收集与处理 -->
        <div class="bg-white rounded-2xl shadow-lg border border-slate-200 p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600">
              <Database class="w-6 h-6" />
            </div>
            <h3 class="font-bold text-lg text-slate-800">数据收集与处理</h3>
          </div>
          <div class="space-y-3 text-sm text-slate-600">
            <div class="bg-slate-50 p-4 rounded-lg border border-slate-100">
              <p class="font-semibold text-slate-700 mb-2">数据源</p>
              <ul class="space-y-1.5 text-xs">
                <li>• <strong>TopHub:</strong> 微博、B站、知乎、抖音、百度、贴吧、快手、IT之家等8个平台</li>
                <li>• <strong>Hacker News:</strong> Top/Best/New 三个榜单</li>
                <li>• <strong>缓存策略:</strong> 内存+文件双重缓存，30分钟TTL</li>
              </ul>
            </div>
            <div class="bg-slate-50 p-4 rounded-lg border border-slate-100">
              <p class="font-semibold text-slate-700 mb-2">数据处理</p>
              <ul class="space-y-1.5 text-xs">
                <li>• <strong>跨平台对齐:</strong> 基于标题相似度的智能聚类算法</li>
                <li>• <strong>历史分析:</strong> JSONL格式快照存储，支持增长/新颖性计算</li>
                <li>• <strong>热度归一化:</strong> 统一不同平台的热度计算口径</li>
                <li>• <strong>前端分类:</strong> 300+关键词规则，自动分类（娱乐/社会/科技/国际/财经）</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Agent智能体系统 -->
        <div class="bg-white rounded-2xl shadow-lg border border-slate-200 p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600">
              <BrainCircuit class="w-6 h-6" />
            </div>
            <h3 class="font-bold text-lg text-slate-800">Agent智能体系统</h3>
          </div>
          <div class="space-y-3 text-sm text-slate-600">
            <div class="bg-slate-50 p-4 rounded-lg border border-slate-100">
              <p class="font-semibold text-slate-700 mb-2">工作流Agent（4个）</p>
              <ul class="space-y-1.5 text-xs">
                <li>• <strong>Reporter:</strong> 从多平台数据中提取核心事实</li>
                <li>• <strong>Analyst:</strong> 深度舆情分析，生成洞察结论</li>
                <li>• <strong>Debater:</strong> 多角度辩论，进行观点碰撞与事实核查</li>
                <li>• <strong>Writer:</strong> 生成小红书/抖音风格爆款文案</li>
              </ul>
            </div>
            <div class="bg-slate-50 p-4 rounded-lg border border-slate-100">
              <p class="font-semibold text-slate-700 mb-2">专用Agent（2个）</p>
              <ul class="space-y-1.5 text-xs">
                <li>• <strong>HotNews Interpreter:</strong> 热点演化解读（生命周期/扩散/分歧），按需LLM调用+缓存</li>
                <li>• <strong>Translator:</strong> 中文话题→英文搜索关键词转换</li>
              </ul>
            </div>
            <div class="bg-slate-50 p-4 rounded-lg border border-slate-100">
              <p class="font-semibold text-slate-700 mb-2">技术特性</p>
              <ul class="space-y-1.5 text-xs">
                <li>• <strong>多Provider支持:</strong> DeepSeek/Moonshot/Doubao等，自动Fallback</li>
                <li>• <strong>LangGraph编排:</strong> 基于状态图的工作流管理</li>
                <li>• <strong>流式传输:</strong> Server-Sent Events (SSE) 实时推送</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- 技术栈 -->
      <div class="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
        <h3 class="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
          <Code class="w-6 h-6 text-slate-600" />
          技术栈
        </h3>
        <div class="grid md:grid-cols-3 gap-6">
          <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-5 border border-blue-200">
            <h4 class="font-bold text-blue-800 mb-3">后端技术</h4>
            <ul class="text-sm text-blue-700 space-y-1.5">
              <li>• Python 3.11+</li>
              <li>• FastAPI (RESTful API)</li>
              <li>• LangChain + LangGraph</li>
              <li>• httpx (异步HTTP客户端)</li>
              <li>• Pydantic (数据验证)</li>
            </ul>
          </div>
          <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-5 border border-purple-200">
            <h4 class="font-bold text-purple-800 mb-3">LLM集成</h4>
            <ul class="text-sm text-purple-700 space-y-1.5">
              <li>• DeepSeek API</li>
              <li>• Moonshot (Kimi) API</li>
              <li>• Doubao (字节) API</li>
              <li>• 多Provider Fallback机制</li>
              <li>• 统一Agent接口抽象</li>
            </ul>
          </div>
          <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-5 border border-green-200">
            <h4 class="font-bold text-green-800 mb-3">前端技术</h4>
            <ul class="text-sm text-green-700 space-y-1.5">
              <li>• Vue 3 (Composition API)</li>
              <li>• Pinia (状态管理)</li>
              <li>• Tailwind CSS</li>
              <li>• Lucide Icons</li>
              <li>• 响应式设计</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 核心特性 -->
      <div class="mt-8 bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl shadow-lg border border-slate-200 p-8">
        <h3 class="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
          <Sparkles class="w-6 h-6 text-slate-600" />
          核心特性
        </h3>
        <div class="grid md:grid-cols-2 gap-4">
          <div class="bg-white rounded-lg p-4 border border-slate-200">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-2 h-2 bg-emerald-500 rounded-full"></div>
              <span class="font-semibold text-slate-700">智能对齐聚类</span>
            </div>
            <p class="text-sm text-slate-600">基于标题相似度的跨平台热点对齐，支持多平台热度聚合与归一化</p>
          </div>
          <div class="bg-white rounded-lg p-4 border border-slate-200">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-2 h-2 bg-emerald-500 rounded-full"></div>
              <span class="font-semibold text-slate-700">历史信号分析</span>
            </div>
            <p class="text-sm text-slate-600">增长趋势、热度变化、新颖性检测，基于历史快照的智能分析</p>
          </div>
          <div class="bg-white rounded-lg p-4 border border-slate-200">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-2 h-2 bg-emerald-500 rounded-full"></div>
              <span class="font-semibold text-slate-700">按需LLM调用</span>
            </div>
            <p class="text-sm text-slate-600">热点演化解读仅在用户点击时触发，缓存机制降低token成本</p>
          </div>
          <div class="bg-white rounded-lg p-4 border border-slate-200">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-2 h-2 bg-emerald-500 rounded-full"></div>
              <span class="font-semibold text-slate-700">多Agent协作</span>
            </div>
            <p class="text-sm text-slate-600">6个专用Agent分工协作，支持工作流编排与实时状态追踪</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Database, BrainCircuit, Layout, Network, Cpu, Code, Sparkles } from 'lucide-vue-next'
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
