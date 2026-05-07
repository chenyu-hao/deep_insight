<template>
  <div class="h-full overflow-auto p-4 animate-fade-in space-y-5">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-extrabold" :class="isDark ? 'text-white' : 'text-slate-800'">热榜选题</h1>
        <p class="text-sm mt-1" :class="isDark ? 'text-slate-400' : 'text-slate-500'">跨平台热度追踪 · 热点快速推演</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="refreshData({ forceRefresh: true })"
          class="px-4 py-2 rounded-lg border text-xs font-bold transition flex items-center gap-1"
          :class="isDark ? 'border-slate-600 text-slate-300 hover:bg-slate-800' : 'border-slate-200 text-slate-600 hover:bg-slate-50'">
          <RefreshCw class="w-3 h-3" :class="{ 'animate-spin': loading }" />
          {{ loading ? '刷新中' : '刷新' }}
        </button>
      </div>
    </div>

    <!-- Platform Filter Tabs -->
    <div class="flex gap-2 flex-wrap">
      <button v-for="p in platformList" :key="p.id" @click="selectPlatform(p.id)"
        class="px-4 py-2 rounded-lg text-xs font-bold transition-all border"
        :class="selectedPlatform === p.id
          ? (isDark ? 'bg-brand-500/20 border-brand-500 text-brand-400' : 'bg-brand-50 border-brand-500 text-brand-600')
          : (isDark ? 'border-slate-600 text-slate-400 hover:border-slate-500' : 'border-slate-200 text-slate-500 hover:border-slate-300')">
        {{ p.name }}
      </button>
    </div>

    <!-- Search -->
    <div class="relative">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" :class="isDark ? 'text-slate-500' : 'text-slate-400'" />
      <input v-model="searchQuery" type="text" placeholder="搜索话题..."
        class="w-full pl-10 pr-4 py-2.5 rounded-lg border text-sm outline-none transition"
        :class="isDark ? 'bg-slate-800 border-slate-700 text-slate-200 placeholder-slate-500 focus:border-brand-500' : 'bg-white border-slate-200 text-slate-700 placeholder-slate-400 focus:border-brand-500'" />
    </div>

    <!-- Content -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-2 border-brand-500 border-t-transparent"></div>
    </div>

    <div v-else-if="filteredTopics.length === 0" class="text-center py-20">
      <div class="text-4xl mb-3 opacity-30">📭</div>
      <p class="text-sm" :class="isDark ? 'text-slate-500' : 'text-slate-400'">暂无数据，点击刷新加载</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
      <div v-for="(topic, idx) in filteredTopics" :key="idx"
        @click="selectTopic(topic)"
        class="card-hover rounded-xl p-4 border cursor-pointer transition-all"
        :class="[
          selectedTopic?.id === topic.id
            ? (isDark ? 'bg-brand-500/10 border-brand-500' : 'bg-brand-50 border-brand-500')
            : (isDark ? 'bg-slate-800 border-slate-700 hover:border-slate-600' : 'bg-white border-slate-100 hover:border-brand-200')
        ]">
        <div class="flex items-start justify-between gap-3 mb-2">
          <span class="text-xs font-black px-2.5 py-1 rounded-lg shrink-0"
            :class="idx === 0
              ? 'bg-gradient-to-br from-amber-400 to-orange-500 text-white'
              : idx === 1
              ? 'bg-gradient-to-br from-slate-300 to-slate-500 text-white'
              : idx === 2
              ? 'bg-gradient-to-br from-amber-200 to-orange-300 text-amber-900'
              : (isDark ? 'bg-slate-700 text-slate-300' : 'bg-slate-100 text-slate-600')">
            #{{ idx + 1 }}
          </span>
          <span v-if="topic.platform" class="text-[10px] font-bold px-2 py-0.5 rounded"
            :class="isDark ? 'bg-slate-700 text-slate-400' : 'bg-slate-100 text-slate-500'">
            {{ topic.platform }}
          </span>
        </div>
        <h3 class="font-bold text-sm leading-snug mb-1 line-clamp-2"
          :class="isDark ? 'text-slate-200' : 'text-slate-800'">
          {{ topic.title }}
        </h3>
        <p v-if="topic.description" class="text-xs line-clamp-1 mb-2"
          :class="isDark ? 'text-slate-500' : 'text-slate-400'">
          {{ topic.description }}
        </p>
        <div class="flex items-center justify-between text-xs"
          :class="isDark ? 'text-slate-500' : 'text-slate-400'">
          <span class="font-bold text-orange-500">🔥 {{ topic.heat_display || '-' }}</span>
        </div>
      </div>
    </div>

    <!-- Detail Drawer Overlay -->
    <Teleport to="body">
      <div v-if="selectedTopic" class="fixed inset-0 z-50 flex justify-end">
        <div class="absolute inset-0 bg-black/40" @click="selectedTopic = null"></div>
        <div class="relative w-full max-w-md h-full overflow-y-auto custom-scrollbar p-6 animate-fade-in"
          :class="isDark ? 'bg-slate-900' : 'bg-white'">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-bold" :class="isDark ? 'text-white' : 'text-slate-800'">热点解读</h2>
            <button @click="selectedTopic = null" class="p-1.5 rounded-lg transition"
              :class="isDark ? 'hover:bg-slate-800 text-slate-400' : 'hover:bg-slate-100 text-slate-500'">
              <X class="w-5 h-5" />
            </button>
          </div>

          <h3 class="font-bold text-base mb-3" :class="isDark ? 'text-slate-200' : 'text-slate-700'">
            {{ selectedTopic.title }}
          </h3>

          <div v-if="interpreting" class="flex items-center gap-2 py-8 justify-center"
            :class="isDark ? 'text-slate-400' : 'text-slate-500'">
            <Loader2 class="w-4 h-4 animate-spin" />
            <span class="text-sm">AI 解读中...</span>
          </div>

          <div v-else-if="interpretError" class="text-sm py-4 text-red-500">
            {{ interpretError }}
          </div>

          <div v-else-if="topicInsight" class="space-y-4">
            <div class="flex gap-2 flex-wrap">
              <span class="text-xs font-bold px-2 py-0.5 rounded-full border"
                :class="isDark ? 'border-slate-600 text-slate-300 bg-slate-800' : 'border-slate-200 text-slate-600 bg-slate-50'">
                {{ topicInsight.lifecycle_stage || '未知阶段' }}
              </span>
              <span v-if="topicInsight.confidence != null" class="text-xs font-bold px-2 py-0.5 rounded-full border"
                :class="isDark ? 'border-slate-600 text-slate-300 bg-slate-800' : 'border-slate-200 text-slate-600 bg-slate-50'">
                置信度 {{ Math.round(topicInsight.confidence * 100) }}%
              </span>
            </div>
            <p class="text-sm whitespace-pre-line" :class="isDark ? 'text-slate-300' : 'text-slate-600'">
              {{ topicInsight.diffusion_summary || topicInsight.content || '无解读内容' }}
            </p>
          </div>

          <div v-else class="text-center py-8 text-sm" :class="isDark ? 'text-slate-500' : 'text-slate-400'">
            点击下方按钮获取 AI 解读
          </div>

          <div class="mt-6 space-y-3">
            <button @click="fetchTopicInsight" :disabled="interpreting"
              class="w-full py-2.5 rounded-lg text-white font-bold text-sm transition flex items-center justify-center gap-2"
              :class="interpreting ? 'bg-slate-400' : 'gradient-brand hover:opacity-90'">
              <Sparkles class="w-4 h-4" />
              {{ interpreting ? '解读中...' : 'AI 解读' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, RefreshCw, X, Loader2, Sparkles } from 'lucide-vue-next'
import { useConfigStore } from '@/stores/config'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()
const configStore = useConfigStore()
const isDark = computed(() => configStore.isDarkMode)

const loading = ref(false)
const searchQuery = ref('')
const selectedPlatform = ref('all')
const topics = ref([])
const selectedTopic = ref(null)
const interpreting = ref(false)
const topicInsight = ref(null)
const interpretError = ref('')

const platformList = [
  { id: 'all', name: '全榜' },
  { id: 'weibo', name: '微博' },
  { id: 'bilibili', name: 'B站' },
  { id: 'douyin', name: '抖音' },
  { id: 'baidu', name: '百度' },
  { id: 'tieba', name: '贴吧' },
  { id: 'kuaishou', name: '快手' },
  { id: 'zhihu', name: '知乎' },
  { id: 'hn', name: 'Hacker News' },
]

function parseHeatValue(raw) {
  if (!raw) return { score: 0, display: '-' }
  const text = String(raw).trim()
  const numMatch = text.match(/([\d,.]+)\s*(亿|万)?/)
  let score = 0
  if (numMatch) {
    const num = parseFloat(numMatch[1].replace(/,/g, '')) || 0
    const unit = numMatch[2] || ''
    if (unit === '亿') score = num * 1e8
    else if (unit === '万') score = num * 1e4
    else score = num
  }
  const playMatch = text.match(/([\d,.]+)\s*次播放/)
  if (playMatch) score = parseFloat(playMatch[1].replace(/,/g, '')) || score
  return { score, display: text }
}

function selectPlatform(id) {
  selectedPlatform.value = id
}

const filteredTopics = computed(() => {
  let result = Array.isArray(topics.value) ? [...topics.value] : []
  if (selectedPlatform.value !== 'all') {
    const pid = selectedPlatform.value
    result = result.filter(t => {
      const pids = Array.isArray(t.platform_ids) ? t.platform_ids : []
      return pids.includes(pid)
    })
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(t => (t.title || '').toLowerCase().includes(q) || (t.description || '').toLowerCase().includes(q))
  }
  return result
})

async function refreshData({ forceRefresh = false } = {}) {
  if (loading.value) return
  loading.value = true
  try {
    const res = await fetch('http://127.0.0.1:8000/api/hot-news/collect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ platforms: ['all'], force_refresh: forceRefresh }),
    })
    const data = await res.json()

    if (data.news_list && Array.isArray(data.news_list)) {
      topics.value = data.news_list.map((news, idx) => {
        const heatDisplay = news.hot_value || ''
        const heat = parseHeatValue(heatDisplay)
        const evidenceList = Array.isArray(news.evidence) ? news.evidence : []
        const platformsData = Array.isArray(news.platforms_data) ? news.platforms_data : []
        const platformIds = Array.isArray(news.platform_ids)
          ? news.platform_ids
          : [...new Set([
              ...platformsData.map(x => x && x.platform_id).filter(Boolean),
              ...evidenceList.map(x => x && x.platform_id).filter(Boolean),
            ])]
        const keywords = Array.isArray(news.keywords) ? news.keywords : []

        return {
          id: news.id || `${news.source_id || 'news'}-${news.rank || idx}`,
          title: news.title || `话题 #${idx + 1}`,
          description: keywords.length ? `关键词：${keywords.slice(0, 6).join(' / ')}` : '',
          platform: news.platform || '多平台对齐',
          heat_score: Number.isFinite(news.hot_score) ? news.hot_score : heat.score,
          heat_display: heatDisplay || heat.display,
          rank: news.rank || (idx + 1),
          growth: typeof news.growth === 'number' ? news.growth : 0,
          is_new: Boolean(news.is_new),
          hot_score_delta: typeof news.hot_score_delta === 'number' ? news.hot_score_delta : 0,
          platform_ids: platformIds,
          evidence: evidenceList,
          platforms_data: platformsData,
          keywords,
          timestamp: news.timestamp || data.collection_time,
        }
      })
    } else {
      topics.value = []
    }
  } catch (e) {
    console.error('Failed to fetch hot news:', e)
    topics.value = []
  } finally {
    loading.value = false
  }
}

function selectTopic(topic) {
  selectedTopic.value = topic
  topicInsight.value = null
  interpretError.value = ''
  fetchTopicInsight()
}

async function fetchTopicInsight() {
  const topic = selectedTopic.value
  if (!topic) return
  interpreting.value = true
  interpretError.value = ''
  try {
    const body = {
      id: topic.id,
      title: topic.title,
      collection_time: topic.timestamp,
      hot_value: topic.heat_display,
      hot_score: topic.heat_score,
      growth: topic.growth,
      hot_score_delta: topic.hot_score_delta,
      is_new: topic.is_new,
      platforms_data: topic.platforms_data || [],
      evidence: topic.evidence || [],
    }
    const resp = await fetch('http://127.0.0.1:8000/api/hot-news/interpret', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    const data = await resp.json()
    if (!data || data.success === false) {
      interpretError.value = (data && data.diffusion_summary) ? data.diffusion_summary : '解读生成失败'
      topicInsight.value = null
    } else {
      topicInsight.value = data
    }
  } catch (e) {
    interpretError.value = e?.message || '解读生成失败'
    topicInsight.value = null
  } finally {
    interpreting.value = false
  }
}

function renderMarkdown(text) { return text ? md.render(text) : '' }

onMounted(() => refreshData())
</script>
