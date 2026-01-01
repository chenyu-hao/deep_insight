<template>
  <div class="view-section animate-fade-in">
    <header class="relative bg-white border-b border-slate-100 pt-12 pb-8 px-4">
      <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-3xl md:text-5xl font-extrabold text-slate-900 tracking-tight mb-4">
          舆情洞察与<span class="gradient-text">爆款文案生成</span>引擎
        </h1>
        
        <div class="max-w-2xl mx-auto mt-8 relative z-10">
          <div class="relative group">
            <div class="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
            <div class="relative flex items-center bg-white rounded-xl shadow-xl border border-slate-200 p-1">
              <div class="pl-4 text-slate-400">
                <Search class="w-5 h-5" />
              </div>
              <input
                v-model="topic"
                type="text"
                class="w-full py-3 px-4 text-slate-700 bg-transparent outline-none placeholder:text-slate-400"
                placeholder="输入您想了解的任何议题..."
                @keyup.enter="handleStart"
              />
              
              <div class="h-8 border-l border-slate-200 mx-2"></div>
              
              <div class="flex items-center gap-2 pr-2" title="辩论轮数">
                <span class="text-xs text-slate-400 font-bold whitespace-nowrap">轮数:</span>
                <input
                  v-model.number="debateRounds"
                  type="number"
                  min="1"
                  max="5"
                  class="w-12 py-1 px-2 text-center text-sm border border-slate-200 rounded-lg outline-none focus:border-blue-500"
                />
              </div>

              <button
                @click="handleStart"
                :class="[
                  'px-6 py-2 text-white font-medium rounded-lg transition-colors flex items-center gap-2 shadow-md whitespace-nowrap min-w-[120px] justify-center',
                  isLoading ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'
                ]"
              >
                <component :is="isLoading ? Square : Sparkles" class="w-4 h-4" />
                {{ isLoading ? '停止分析' : '启动分析' }}
              </button>
            </div>
          </div>
          
          <div class="mt-4 flex flex-wrap justify-center items-center gap-2 text-xs text-slate-500">
            <div class="flex items-center gap-1 font-bold text-red-500">
              <TrendingUp class="w-3 h-3" />
              <span>{{ trendingDate }}热搜:</span>
            </div>
            <div class="flex gap-2">
              <button
                v-for="(t, idx) in trendingTopics"
                :key="idx"
                @click="topic = t"
                class="px-3 py-1 bg-white border border-slate-200 rounded-full hover:border-blue-300 hover:text-blue-600 transition-colors animate-fade-in text-xs whitespace-nowrap"
              >
                {{ t }}
              </button>
            </div>
            <button
              @click="refreshTrending"
              class="ml-1 p-1 hover:bg-slate-100 rounded-full text-slate-400 transition-colors"
              title="刷新热搜"
            >
              <RefreshCw class="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </header>

    <section class="py-8 px-4 max-w-7xl mx-auto space-y-8">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <!-- Left: Debate & Insight -->
        <div class="lg:col-span-7 flex flex-col gap-6">
          <div class="flex flex-col gap-2">
            <div class="flex items-center justify-between px-1 h-8">
              <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2">
                <Cpu class="w-5 h-5 text-blue-600" /> 智能体协作 (Multi-Agent Debate)
              </h2>
              <div v-if="isLoading" class="flex items-center gap-2">
                <div class="px-3 py-1 bg-green-50 text-green-700 rounded-full border border-green-100 text-xs font-medium flex items-center gap-2">
                  <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                  </span>
                  <span>Real-time Inference</span>
                </div>
              </div>
            </div>

            <div class="glass-card rounded-xl flex flex-col border-t-4 border-t-blue-500 h-[450px] shadow-lg relative overflow-hidden">
              <div class="p-3 bg-slate-50/80 border-b border-slate-100 flex justify-between items-center backdrop-blur text-xs font-bold text-slate-600 z-10">
                <span>AI 辩论过程实时推演</span>
                <span class="text-slate-400 font-normal text-[10px]">{{ activeModelDisplay }}</span>
              </div>
              <div class="flex-1 p-4 overflow-y-auto custom-scrollbar space-y-4 font-mono text-sm bg-white/50 relative scroll-smooth">
                <!-- 调试信息 -->
                <div v-if="false" class="text-xs text-red-500 p-2 bg-red-50 mb-2">
                  调试: debateLogs.length={{ debateLogs.length }}, storeLogs.length={{ storeLogs.length }}
                </div>
                <div v-if="debateLogs.length === 0" class="h-full flex flex-col items-center justify-center text-slate-400 opacity-60">
                  <Bot class="w-16 h-16 mb-4 stroke-1" />
                  <p>等待指令启动...</p>
                  <p class="text-xs mt-2 text-slate-300">Store日志数: {{ storeLogs.length }} | 显示日志数: {{ debateLogs.length }}</p>
                </div>
                <div
                  v-for="(log, idx) in debateLogs"
                  :key="`log-${idx}-${log.name}`"
                  :class="[
                    'debate-bubble p-3 rounded-lg border text-xs leading-relaxed mb-3 shadow-sm bg-white animate-fade-in',
                    getBubbleClass(log.role)
                  ]"
                >
                  <div class="font-bold mb-1 opacity-80 flex justify-between items-center border-b border-slate-200/50 pb-1 mb-2">
                    <span class="flex items-center gap-1">
                      <component :is="getIcon(log.role)" class="w-3 h-3" />
                      {{ log.name }}
                    </span>
                    <span v-if="log.model" class="text-[9px] font-normal text-slate-400 bg-slate-50 px-1 rounded">
                      {{ log.model }}
                    </span>
                  </div>
                  <div class="text-slate-700 prose prose-xs max-w-none" v-html="renderMarkdown(log.content)"></div>
                </div>
              </div>
            </div>
          </div>

          <div class="flex flex-col gap-2">
            <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2 px-1">
              <Lightbulb class="w-5 h-5 text-yellow-500" /> 核心洞察 (Grand Insight)
            </h2>
            <div class="glass-card rounded-xl p-5 shadow-md border-l-4 border-l-yellow-400 min-h-[140px] flex flex-col">
              <div class="text-sm text-slate-600 leading-relaxed flex-1 flex flex-col">
                <div v-if="!insight" class="h-full flex items-center justify-center text-slate-400 border border-dashed border-slate-200 rounded-lg p-3 bg-slate-50/50 italic text-xs">
                  等待辩论结论产出...
                </div>
                <div v-else class="animate-fade-in p-4 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg border border-yellow-100 text-slate-700 shadow-sm h-full overflow-y-auto">
                  <strong class="text-orange-600 block mb-2 flex items-center gap-1 text-sm uppercase tracking-wider">
                    <Zap class="w-4 h-4" /> Grand Insight
                  </strong>
                  <p class="text-sm leading-relaxed">{{ insight }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: XHS Preview -->
        <div class="lg:col-span-5 flex flex-col gap-2">
          <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2 px-1">
            <Smartphone class="w-5 h-5 text-purple-600" /> 实时生成预览 (Preview)
          </h2>

          <div class="glass-card p-6 rounded-xl shadow-lg flex justify-center bg-slate-100/50">
            <div class="glass-card rounded-[3rem] overflow-hidden shadow-2xl bg-white w-full max-w-[300px] h-[600px] flex flex-col transform transition hover:scale-[1.02] duration-300" style="border: 8px solid #1e293b;">
              <!-- Status Bar -->
              <div class="relative bg-white px-5 h-10 flex items-center justify-between z-10 flex-shrink-0 select-none">
                <span class="text-[10px] font-bold text-slate-900 w-8">09:41</span>
                <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-6 bg-black rounded-full flex justify-center items-center">
                  <div class="w-1.5 h-1.5 bg-gray-800 rounded-full absolute right-4"></div>
                </div>
                <div class="w-8 flex justify-end">
                  <Wifi class="w-3 h-3 text-slate-900" />
                </div>
              </div>

              <!-- Screen Content -->
              <div
                class="relative cursor-pointer group flex-1 flex flex-col overflow-hidden"
                @click="switchPhoneImage"
                title="点击切换配图风格"
              >
                <div
                  :class="[
                    'aspect-[3/4] relative overflow-hidden flex-shrink-0 transition-colors duration-500',
                    phoneStyles[currentPhoneStyleIndex].bg
                  ]"
                >
                  <div
                    v-if="!xhsPreview.title"
                    class="absolute inset-0 flex flex-col items-center justify-center text-slate-400 transition-opacity duration-300"
                  >
                    <Image class="w-8 h-8 mb-2 opacity-50" />
                    <span class="text-xs">AI 配图生成区</span>
                  </div>
                  <div
                    v-else
                    class="absolute inset-0 flex flex-col items-center justify-center opacity-100 transition-opacity duration-700 p-4 text-center"
                  >
                    <div class="text-6xl mb-4 drop-shadow-sm transition-transform duration-300 group-hover:scale-110">
                      {{ phoneStyles[currentPhoneStyleIndex].icon }}
                    </div>
                    <h2
                      :class="[
                        'text-xl font-black bg-white/80 backdrop-blur-md px-4 py-2 rounded-xl shadow-lg transform -rotate-2 border border-slate-100',
                        phoneStyles[currentPhoneStyleIndex].textColor
                      ]"
                    >
                      {{ xhsPreview.title.substring(0, 15) }}
                    </h2>
                    <div class="absolute bottom-4 right-4 bg-black/50 text-white text-[10px] px-2 py-1 rounded-full backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity">
                      点击切换风格 <RefreshCcw class="w-3 h-3 inline" />
                    </div>
                  </div>
                </div>

                <div class="p-4 bg-white flex-1 flex flex-col overflow-hidden">
                  <h4 class="font-bold text-sm text-slate-900 mb-2 truncate">
                    {{ xhsPreview.title || '标题生成中...' }}
                  </h4>
                  <div class="text-xs text-slate-600 space-y-2 flex-1 overflow-y-auto custom-scrollbar pr-1">
                    <div v-if="!xhsPreview.content" class="space-y-2">
                      <div class="h-2 bg-slate-100 rounded w-full animate-pulse"></div>
                      <div class="h-2 bg-slate-100 rounded w-5/6 animate-pulse"></div>
                      <div class="h-2 bg-slate-100 rounded w-4/6 animate-pulse"></div>
                    </div>
                    <div v-else class="prose prose-xs max-w-none" v-html="renderMarkdown(xhsPreview.content)"></div>
                  </div>
                  <div class="mt-auto pt-3 border-t border-slate-50 flex items-center justify-between text-slate-400 text-[10px]">
                    <div class="flex gap-2">
                      <span><Heart class="w-3 h-3 inline" /> 1.2w</span>
                      <span><Star class="w-3 h-3 inline" /> 5k</span>
                    </div>
                    <span><MessageCircle class="w-3 h-3 inline" /> 892</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Copywriting Section -->
      <div class="flex flex-col gap-2">
        <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2 px-1">
          <PenTool class="w-5 h-5 text-emerald-600" /> 文案生成 (Copywriting)
        </h2>
        <div class="glass-card rounded-xl p-6 shadow-lg border-t-4 border-t-emerald-500">
          <div v-if="isLoading" class="flex items-center gap-2 mb-4 text-sm font-bold text-emerald-600 animate-pulse">
            <Loader2 class="w-4 h-4 animate-spin" /> 正在后台处理信息，生成最终文案...
          </div>
          
          <div class="relative">
            <textarea
              :value="finalCopy"
              readonly
              class="w-full h-40 p-4 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 font-mono resize-none focus:outline-none focus:border-blue-500 transition-colors"
              placeholder="等待辩论结束后，在此生成可直接发布的文案..."
            ></textarea>
            <button
              @click="copyToClipboard"
              :disabled="!finalCopy || finalCopy.length === 0"
              class="absolute top-3 right-3 px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-600 rounded text-xs font-bold shadow-sm transition-colors flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Copy class="w-3 h-3" /> 复制全文
            </button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import {
  Search, Sparkles, Square, TrendingUp, RefreshCw, Cpu, Bot, Lightbulb, Zap,
  Smartphone, Wifi, Image, RefreshCcw, Heart, Star, MessageCircle, PenTool,
  Loader2, Copy, Shield, ThumbsUp, ThumbsDown, Glasses
} from 'lucide-vue-next'
import { useAnalysisStore } from '../stores/analysis'
import { useConfigStore } from '../stores/config'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()
const analysisStore = useAnalysisStore()
const configStore = useConfigStore()

// 使用 storeToRefs 确保响应式
const { logs: storeLogs } = storeToRefs(analysisStore)

const topic = ref('')
const debateRounds = ref(2)
const isLoading = computed(() => analysisStore.isLoading)
const debateLogs = ref([])
const insight = computed(() => analysisStore.insight)
const xhsPreview = ref({ title: '', content: '' })
const finalCopy = computed(() => {
  if (analysisStore.finalCopy.title && analysisStore.finalCopy.body) {
    return `${analysisStore.finalCopy.title}\n\n${analysisStore.finalCopy.body}`
  }
  return ''
})
const activeModelDisplay = ref('')
const trendingDate = ref('')
const trendingTopics = ref([])
const currentPhoneStyleIndex = ref(0)

const phoneStyles = [
  { bg: 'bg-gradient-to-br from-indigo-50 to-pink-50', icon: '🤔', textColor: 'text-slate-800' },
  { bg: 'bg-slate-900', icon: '😱', textColor: 'text-white' },
  { bg: 'bg-red-50', icon: '🔥', textColor: 'text-red-900' },
  { bg: 'bg-emerald-50', icon: '🥗', textColor: 'text-emerald-900' }
]

const renderMarkdown = (text) => {
  if (!text) return ''
  return md.render(text)
}

const getBubbleClass = (role) => {
  const map = {
    moderator: 'border-yellow-200 bg-yellow-50',
    pro: 'border-blue-200 bg-blue-50',
    con: 'border-red-200 bg-red-50',
    analyst: 'border-purple-200 bg-purple-50',
    system: 'border-slate-100 bg-slate-50'
  }
  return map[role] || 'border-slate-200 bg-slate-50'
}

const getIcon = (role) => {
  const map = {
    moderator: Shield,
    pro: ThumbsUp,
    con: ThumbsDown,
    analyst: Glasses,
    system: Bot
  }
  return map[role] || Bot
}

const refreshTrending = () => {
  const today = new Date()
  trendingDate.value = `${today.getMonth() + 1}月${today.getDate()}日`
  const topics = ['OpenAI Sora 2.0 发布', '国内油价调整', '高考分数线公布', '星舰第五次发射', 'DeepSeek V3 开源', '新能源车降价潮']
  trendingTopics.value = topics.sort(() => 0.5 - Math.random()).slice(0, 3)
}

const switchPhoneImage = () => {
  currentPhoneStyleIndex.value = (currentPhoneStyleIndex.value + 1) % phoneStyles.length
}

const handleStart = async () => {
  if (!topic.value.trim()) {
    alert('请输入议题！')
    return
  }

  // 暂时不检查 API Key，使用后端配置的 API Key
  // 如需使用前端配置的 API Key，可以在 SettingsView 中配置
  // const userApis = configStore.getUserApis
  // if (userApis.length === 0) {
  //   alert('请先配置 API Key')
  //   return
  // }

  if (isLoading.value) {
    // 停止分析
    isLoading.value = false
    debateLogs.value = []
    insight.value = ''
    xhsPreview.value = { title: '', content: '' }
    finalCopy.value = ''
    return
  }

  // 清空旧数据
  debateLogs.value = []
  xhsPreview.value = { title: '', content: '' }
  console.log('[HomeView] 🧹 已清空旧日志和预览数据，debateLogs长度:', debateLogs.value.length)
  console.log('[HomeView] 📊 当前store logs长度:', analysisStore.logs.length)

  try {
    console.log('[HomeView] 开始分析，议题:', topic.value, '辩论轮数:', debateRounds.value)
    
    await analysisStore.startAnalysis({
      topic: topic.value,
      debate_rounds: debateRounds.value
    })

    console.log('[HomeView] 分析已启动，等待SSE数据...')
  } catch (err) {
    console.error('[HomeView] 分析错误:', err)
    alert('分析失败: ' + err.message)
  }
}

// 监听分析日志变化 - 使用 storeToRefs 确保响应式
watch(storeLogs, (newLogs, oldLogs) => {
  const oldLength = (oldLogs && oldLogs.length) || 0
  const newLength = (newLogs && newLogs.length) || 0
  console.log(`[HomeView] ⚡ watch触发: ${oldLength} -> ${newLength} (新增 ${newLength - oldLength} 条)`)
  console.log('[HomeView] 当前debateLogs长度:', debateLogs.value.length)
  
  if (newLogs && newLogs.length > 0) {
    // 只处理新增的日志
    const startIndex = oldLength
    const newLogsToProcess = newLogs.slice(startIndex)
    
    if (newLogsToProcess.length > 0) {
      console.log('[HomeView] ✅ 处理新日志，数量:', newLogsToProcess.length)
      
      newLogsToProcess.forEach((log, index) => {
        const globalIndex = startIndex + index
        console.log(`[HomeView] 📝 处理日志 #${globalIndex}:`, {
          agent_name: log.agent_name,
          status: log.status,
          content_preview: (log.step_content || '').substring(0, 100),
          content_length: (log.step_content || '').length,
          has_model: !!log.model
        })
        
        // 添加辩论日志
        const roleMap = {
          'Moderator': 'moderator',
          'Crawler': 'system',
          'Reporter': 'system',
          'Analyst': 'analyst',
          'Debater': 'con',
          'Writer': 'writer',
          'System': 'system'
        }
        
        const role = roleMap[log.agent_name] || 'system'
        const logEntry = {
          role: role,
          name: log.agent_name,
          content: log.step_content || '',
          model: log.model || ''
        }
        
        console.log('[HomeView] ➕ 添加辩论日志:', logEntry.name, '到数组，当前长度:', debateLogs.value.length)
        debateLogs.value.push(logEntry)
        console.log('[HomeView] ✅ 添加后数组长度:', debateLogs.value.length, '最新条目:', debateLogs.value[debateLogs.value.length - 1])

        // 处理Writer输出，更新预览
        if (log.agent_name === 'Writer' && log.step_content) {
          console.log('[HomeView] ✍️ 处理Writer输出，更新预览，原始内容长度:', log.step_content.length)
          const content = log.step_content
          
          // 尝试解析 TITLE: 和 CONTENT: 格式
          if (content.includes('TITLE:') && content.includes('CONTENT:')) {
            const titleMatch = content.match(/TITLE:\s*(.+?)(?:\n|CONTENT:)/s)
            const contentMatch = content.match(/CONTENT:\s*(.+?)(?:\n\n|$)/s)
            
            if (titleMatch) {
              xhsPreview.value.title = titleMatch[1].trim()
              console.log('[HomeView] 📌 解析到标题:', xhsPreview.value.title)
            }
            if (contentMatch) {
              xhsPreview.value.content = contentMatch[1].trim()
              console.log('[HomeView] 📄 解析到内容，长度:', xhsPreview.value.content.length)
            } else if (content.includes('CONTENT:')) {
              // 如果只有 CONTENT: 标记，提取后面的内容
              const parts = content.split('CONTENT:')
              if (parts.length > 1) {
                xhsPreview.value.content = parts.slice(1).join('CONTENT:').trim()
                console.log('[HomeView] 🔧 使用split解析内容，长度:', xhsPreview.value.content.length)
              }
            }
          } else {
            // 如果没有格式标记，直接使用全部内容
            xhsPreview.value.content = content
            console.log('[HomeView] 📋 预览内容（无格式标记）长度:', content.length)
          }
        }
      })
    } else {
      console.log('[HomeView] ⚠️ 没有新日志需要处理')
    }
  } else {
    console.log('[HomeView] ⚠️ newLogs为空或长度为0')
  }
}, { deep: true, immediate: false })

// 监听最终文案变化
watch(() => analysisStore.finalCopy, (newCopy) => {
  console.log('[HomeView] 最终文案更新:', {
    has_title: !!newCopy.title,
    has_body: !!newCopy.body,
    title_length: (newCopy.title || '').length,
    body_length: (newCopy.body || '').length
  })
  
  if (newCopy && newCopy.body) {
    if (!xhsPreview.value.title && newCopy.title) {
      xhsPreview.value.title = newCopy.title
      console.log('[HomeView] 从finalCopy设置预览标题:', newCopy.title)
    }
    if (!xhsPreview.value.content && newCopy.body) {
      xhsPreview.value.content = newCopy.body
      console.log('[HomeView] 从finalCopy设置预览内容，长度:', newCopy.body.length)
    }
  }
}, { deep: true })

const copyToClipboard = async () => {
  try {
    const text = finalCopy.value || ''
    if (!text) {
      alert('暂无内容可复制')
      return
    }
    await navigator.clipboard.writeText(text)
    alert('已复制到剪贴板')
  } catch (err) {
    console.error('Copy failed:', err)
    alert('复制失败，请手动复制')
  }
}

onMounted(() => {
  refreshTrending()
})
</script>

<style scoped>
.debate-bubble {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>