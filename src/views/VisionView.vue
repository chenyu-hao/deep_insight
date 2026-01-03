<template>
  <div class="view-section animate-fade-in py-12 px-4">
    <div class="max-w-7xl mx-auto">
      <div class="text-center mb-16">
        <h2 class="text-3xl md:text-4xl font-bold text-slate-900 mb-4">愿景与价值</h2>
        <p class="text-slate-500 text-lg max-w-3xl mx-auto">
          基于多智能体协作的舆情洞察系统，实现跨平台热点追踪、智能解读与内容生成的一体化解决方案
        </p>
      </div>

      <!-- 核心价值主张 -->
      <div class="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-2xl shadow-xl border border-blue-100 p-8 md:p-12 mb-12">
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl mb-4">
            <Target class="w-8 h-8 text-white" />
          </div>
          <h3 class="text-2xl font-bold text-slate-900 mb-3">核心价值主张</h3>
          <p class="text-slate-600 max-w-2xl mx-auto">
            通过多Agent协作架构，将热点追踪、舆情分析、内容生成整合为端到端的智能工作流，
            为内容创作者、舆情分析师、研究人员提供高效、准确、可解释的决策支持工具
          </p>
        </div>
      </div>

      <!-- 已实现的核心能力 -->
      <div class="mb-12">
        <h3 class="text-2xl font-bold text-slate-900 mb-6 flex items-center gap-3">
          <CheckCircle2 class="w-7 h-7 text-emerald-600" />
          已实现的核心能力
        </h3>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- 多平台热点聚合 -->
          <div class="bg-white rounded-xl p-6 shadow-lg border border-slate-200 hover:shadow-xl transition-all group">
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-200 transition-colors">
              <Network class="w-6 h-6 text-blue-600" />
            </div>
            <h4 class="font-bold text-lg text-slate-800 mb-2">多平台热点聚合</h4>
            <p class="text-sm text-slate-600 mb-3">
              实时收集8个国内平台（微博、B站、知乎、抖音等）及Hacker News热点，统一数据格式与热度归一化
            </p>
            <div class="flex flex-wrap gap-2">
              <span class="text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded-full">TopHub</span>
              <span class="text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded-full">HN</span>
              <span class="text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded-full">缓存机制</span>
            </div>
          </div>

          <!-- 智能对齐聚类 -->
          <div class="bg-white rounded-xl p-6 shadow-lg border border-slate-200 hover:shadow-xl transition-all group">
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-purple-200 transition-colors">
              <GitBranch class="w-6 h-6 text-purple-600" />
            </div>
            <h4 class="font-bold text-lg text-slate-800 mb-2">智能对齐聚类</h4>
            <p class="text-sm text-slate-600 mb-3">
              基于标题相似度的跨平台热点对齐算法，自动识别同一事件在不同平台的表达，聚合热度数据
            </p>
            <div class="flex flex-wrap gap-2">
              <span class="text-xs px-2 py-1 bg-purple-50 text-purple-700 rounded-full">相似度计算</span>
              <span class="text-xs px-2 py-1 bg-purple-50 text-purple-700 rounded-full">热度聚合</span>
            </div>
          </div>

          <!-- 历史信号分析 -->
          <div class="bg-white rounded-xl p-6 shadow-lg border border-slate-200 hover:shadow-xl transition-all group">
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-green-200 transition-colors">
              <TrendingUp class="w-6 h-6 text-green-600" />
            </div>
            <h4 class="font-bold text-lg text-slate-800 mb-2">历史信号分析</h4>
            <p class="text-sm text-slate-600 mb-3">
              JSONL格式快照存储，支持增长趋势、热度变化、新颖性检测，识别爆发式热点与潜在争议
            </p>
            <div class="flex flex-wrap gap-2">
              <span class="text-xs px-2 py-1 bg-green-50 text-green-700 rounded-full">增长检测</span>
              <span class="text-xs px-2 py-1 bg-green-50 text-green-700 rounded-full">新颖性</span>
            </div>
          </div>

          <!-- 多Agent协作系统 -->
          <div class="bg-white rounded-xl p-6 shadow-lg border border-slate-200 hover:shadow-xl transition-all group">
            <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-orange-200 transition-colors">
              <BrainCircuit class="w-6 h-6 text-orange-600" />
            </div>
            <h4 class="font-bold text-lg text-slate-800 mb-2">多Agent协作系统</h4>
            <p class="text-sm text-slate-600 mb-3">
              6个专用Agent分工协作：事实提取、舆情分析、智能辩论、文案生成、演化解读、查询构建
            </p>
            <div class="flex flex-wrap gap-2">
              <span class="text-xs px-2 py-1 bg-orange-50 text-orange-700 rounded-full">LangGraph</span>
              <span class="text-xs px-2 py-1 bg-orange-50 text-orange-700 rounded-full">流式传输</span>
            </div>
          </div>

          <!-- 热点演化解读 -->
          <div class="bg-white rounded-xl p-6 shadow-lg border border-slate-200 hover:shadow-xl transition-all group">
            <div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-indigo-200 transition-colors">
              <Sparkles class="w-6 h-6 text-indigo-600" />
            </div>
            <h4 class="font-bold text-lg text-slate-800 mb-2">热点演化解读</h4>
            <p class="text-sm text-slate-600 mb-3">
              按需LLM调用+智能缓存，解读生命周期阶段、扩散路径、分歧点与观察点，提供可解释的分析链路
            </p>
            <div class="flex flex-wrap gap-2">
              <span class="text-xs px-2 py-1 bg-indigo-50 text-indigo-700 rounded-full">按需调用</span>
              <span class="text-xs px-2 py-1 bg-indigo-50 text-indigo-700 rounded-full">成本优化</span>
            </div>
          </div>

          <!-- 前端智能分类 -->
          <div class="bg-white rounded-xl p-6 shadow-lg border border-slate-200 hover:shadow-xl transition-all group">
            <div class="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-pink-200 transition-colors">
              <Tags class="w-6 h-6 text-pink-600" />
            </div>
            <h4 class="font-bold text-lg text-slate-800 mb-2">前端智能分类</h4>
            <p class="text-sm text-slate-600 mb-3">
              300+关键词规则库，自动分类热点至娱乐/社会/科技/国际/财经等类别，支持加权评分与阈值控制
            </p>
            <div class="flex flex-wrap gap-2">
              <span class="text-xs px-2 py-1 bg-pink-50 text-pink-700 rounded-full">关键词匹配</span>
              <span class="text-xs px-2 py-1 bg-pink-50 text-pink-700 rounded-full">高准确率</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 应用场景 -->
      <div class="mb-12">
        <h3 class="text-2xl font-bold text-slate-900 mb-6 flex items-center gap-3">
          <Lightbulb class="w-7 h-7 text-amber-600" />
          应用场景
        </h3>
        <div class="grid md:grid-cols-2 gap-6">
          <!-- 内容创作者 -->
          <div class="bg-gradient-to-br from-blue-50 to-white rounded-xl p-6 shadow-lg border border-blue-100">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 bg-blue-600 text-white rounded-lg flex items-center justify-center">
                <PenTool class="w-5 h-5" />
              </div>
              <h4 class="font-bold text-lg text-slate-800">内容创作者</h4>
            </div>
            <ul class="space-y-2 text-sm text-slate-600">
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>实时追踪全网热点，第一时间捕捉爆款话题</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>AI生成小红书/抖音风格文案，提升创作效率</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>热点演化解读，把握内容发布最佳时机</span>
              </li>
            </ul>
          </div>

          <!-- 舆情分析师 -->
          <div class="bg-gradient-to-br from-purple-50 to-white rounded-xl p-6 shadow-lg border border-purple-100">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 bg-purple-600 text-white rounded-lg flex items-center justify-center">
                <BarChart3 class="w-5 h-5" />
              </div>
              <h4 class="font-bold text-lg text-slate-800">舆情分析师</h4>
            </div>
            <ul class="space-y-2 text-sm text-slate-600">
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-purple-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>跨平台热点对齐，全面掌握事件传播路径</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-purple-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>历史信号分析，识别潜在争议与爆发点</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-purple-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>多Agent协作分析，提供可解释的洞察结论</span>
              </li>
            </ul>
          </div>

          <!-- 研究人员 -->
          <div class="bg-gradient-to-br from-green-50 to-white rounded-xl p-6 shadow-lg border border-green-100">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 bg-green-600 text-white rounded-lg flex items-center justify-center">
                <GraduationCap class="w-5 h-5" />
              </div>
              <h4 class="font-bold text-lg text-slate-800">研究人员</h4>
            </div>
            <ul class="space-y-2 text-sm text-slate-600">
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>大规模热点数据收集，支持学术研究需求</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>分析链路可追溯，满足可复现性要求</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>多平台数据对比，研究跨平台传播规律</span>
              </li>
            </ul>
          </div>

          <!-- 企业决策者 -->
          <div class="bg-gradient-to-br from-orange-50 to-white rounded-xl p-6 shadow-lg border border-orange-100">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 bg-orange-600 text-white rounded-lg flex items-center justify-center">
                <Building2 class="w-5 h-5" />
              </div>
              <h4 class="font-bold text-lg text-slate-800">企业决策者</h4>
            </div>
            <ul class="space-y-2 text-sm text-slate-600">
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-orange-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>实时监控行业热点，把握市场趋势变化</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-orange-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>智能预警潜在风险，提前制定应对策略</span>
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-orange-500 rounded-full mt-1.5 flex-shrink-0"></div>
                <span>数据驱动的决策支持，提升响应速度与准确性</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 未来展望 -->
      <div class="bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl shadow-lg border border-slate-200 p-8">
        <h3 class="text-2xl font-bold text-slate-900 mb-6 flex items-center gap-3">
          <Telescope class="w-7 h-7 text-purple-600" />
          未来展望
        </h3>
        <div class="grid md:grid-cols-2 gap-6">
          <div class="bg-white rounded-xl p-6 border border-slate-200">
            <div class="flex items-center gap-3 mb-4">
              <ArrowRightCircle class="w-6 h-6 text-blue-600" />
              <h4 class="font-bold text-lg text-slate-800">技术增强</h4>
            </div>
            <ul class="space-y-2 text-sm text-slate-600">
              <li>• 引入更多国际平台（Twitter、Reddit等），实现全球化热点追踪</li>
              <li>• 增强LLM推理能力，支持更复杂的多轮对话与深度分析</li>
              <li>• 优化缓存策略，提升系统响应速度与成本效率</li>
              <li>• 引入向量数据库，支持语义相似度计算与智能推荐</li>
            </ul>
          </div>
          <div class="bg-white rounded-xl p-6 border border-slate-200">
            <div class="flex items-center gap-3 mb-4">
              <ArrowRightCircle class="w-6 h-6 text-purple-600" />
              <h4 class="font-bold text-lg text-slate-800">生态扩展</h4>
            </div>
            <ul class="space-y-2 text-sm text-slate-600">
              <li>• 开放API接口，赋能第三方应用接入舆情分析能力</li>
              <li>• 构建SaaS平台，面向企业提供定制化舆情监控服务</li>
              <li>• 开发移动端应用，支持随时随地热点追踪与分析</li>
              <li>• 建立社区生态，鼓励用户贡献关键词规则与Agent能力</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  Target,
  CheckCircle2,
  Network,
  GitBranch,
  TrendingUp,
  BrainCircuit,
  Sparkles,
  Tags,
  Lightbulb,
  PenTool,
  BarChart3,
  GraduationCap,
  Building2,
  Telescope,
  ArrowRightCircle
} from 'lucide-vue-next'
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
