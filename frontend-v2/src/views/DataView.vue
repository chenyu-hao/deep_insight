<template>
  <div class="h-full overflow-auto p-4 animate-fade-in space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-extrabold" :class="isDark ? 'text-white' : 'text-slate-800'">数据洞察</h1>
      <p class="text-sm mt-1" :class="isDark ? 'text-slate-400' : 'text-slate-500'">多维数据可视化 · AI推理结果展示</p>
    </div>

    <!-- Locked State -->
    <div v-if="!dataUnlocked" class="rounded-xl p-8 border text-center"
      :class="isDark ? 'bg-slate-800/50 border-slate-700' : 'bg-brand-50/50 border-brand-200'">
      <Lock class="w-12 h-12 mx-auto mb-3 text-brand-500" />
      <h3 class="text-lg font-bold mb-2" :class="isDark ? 'text-white' : 'text-slate-800'">数据尚未生成</h3>
      <p class="text-sm mb-4" :class="isDark ? 'text-slate-400' : 'text-slate-500'">
        请先在「舆情推演」页面启动分析，系统将基于辩论结果自动生成数据洞察。
      </p>
      <router-link to="/home" class="inline-block px-5 py-2 rounded-lg text-white text-sm font-bold gradient-brand hover:opacity-90 transition">
        前往推演
      </router-link>
    </div>

    <!-- Data Content -->
    <div v-else>
      <!-- Tabs -->
      <div class="flex gap-1 p-1 rounded-xl mb-5 w-fit"
        :class="isDark ? 'bg-slate-800' : 'bg-slate-100'">
        <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
          class="px-4 py-2 rounded-lg text-xs font-bold transition-all"
          :class="activeTab === tab.id
            ? (isDark ? 'bg-brand-500 text-white shadow' : 'bg-white text-brand-600 shadow-sm')
            : (isDark ? 'text-slate-400 hover:text-slate-200' : 'text-slate-500 hover:text-slate-700')">
          {{ tab.name }}
        </button>
      </div>

      <!-- Tab Content -->
      <!-- 总览 -->
      <div v-if="activeTab === 'overview'" class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div v-for="stat in statsCards" :key="stat.label" class="rounded-xl p-5 border"
          :class="isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'">
          <div class="text-xs font-bold mb-1" :class="isDark ? 'text-slate-400' : 'text-slate-500'">{{ stat.label }}</div>
          <div class="text-2xl font-extrabold" :class="stat.color">{{ stat.value }}</div>
        </div>
      </div>

      <!-- Insight Card -->
      <div class="rounded-xl p-5 border mb-6"
        :class="isDark ? 'bg-slate-800 border-slate-700 border-l-4 border-l-yellow-500' : 'bg-white border-slate-100 border-l-4 border-l-yellow-500'">
        <h3 class="text-sm font-bold mb-2 flex items-center gap-2" :class="isDark ? 'text-slate-200' : 'text-slate-700'">
          <Lightbulb class="w-4 h-4 text-yellow-500" />核心洞察
        </h3>
        <p class="text-sm leading-relaxed" :class="isDark ? 'text-slate-300' : 'text-slate-600'">
          {{ insightCardData.conclusion || '暂无洞察' }}
        </p>
      </div>

      <!-- Charts Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <!-- Radar Chart -->
        <div class="rounded-xl p-5 border"
          :class="isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'">
          <h3 class="text-sm font-bold mb-3" :class="isDark ? 'text-slate-200' : 'text-slate-700'">平台覆盖雷达图</h3>
          <div class="h-64 relative">
            <canvas ref="radarCanvasRef"></canvas>
          </div>
        </div>

        <!-- Trend Chart -->
        <div class="rounded-xl p-5 border"
          :class="isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'">
          <h3 class="text-sm font-bold mb-3" :class="isDark ? 'text-slate-200' : 'text-slate-700'">
            热度趋势
            <span class="ml-2 text-xs font-normal px-2 py-0.5 rounded"
              :class="isDark ? 'bg-slate-700 text-slate-400' : 'bg-slate-100 text-slate-500'">
              {{ trendChartData.stage }} {{ trendChartData.growth > 0 ? '+' : '' }}{{ trendChartData.growth }}%
            </span>
          </h3>
          <div class="h-64 relative">
            <canvas ref="trendCanvasRef"></canvas>
          </div>
        </div>

        <!-- Platform Heat Bar -->
        <div class="rounded-xl p-5 border"
          :class="isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'">
          <h3 class="text-sm font-bold mb-3" :class="isDark ? 'text-slate-200' : 'text-slate-700'">平台热度分布</h3>
          <div class="space-y-3">
            <div v-for="item in platformHeatData" :key="item.name" class="flex items-center gap-3">
              <span class="text-xs w-16 text-right shrink-0" :class="isDark ? 'text-slate-400' : 'text-slate-500'">{{ item.name }}</span>
              <div class="flex-1 h-5 rounded-full overflow-hidden" :class="isDark ? 'bg-slate-700' : 'bg-slate-100'">
                <div class="h-full rounded-full gradient-brand transition-all duration-700" :style="{ width: item.percent + '%' }"></div>
              </div>
              <span class="text-xs font-bold w-10" :class="isDark ? 'text-slate-300' : 'text-slate-600'">{{ item.value }}</span>
            </div>
          </div>
        </div>

        <!-- Debate Timeline -->
        <div class="rounded-xl p-5 border"
          :class="isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'">
          <h3 class="text-sm font-bold mb-3" :class="isDark ? 'text-slate-200' : 'text-slate-700'">辩论时间线</h3>
          <div class="space-y-3 max-h-64 overflow-y-auto custom-scrollbar">
            <div v-for="item in debateTimelineData" :key="'t-' + item.round"
              class="flex gap-3 p-3 rounded-lg border text-xs"
              :class="isDark ? 'border-slate-700 bg-slate-900/50' : 'border-slate-100 bg-slate-50'">
              <span class="w-6 h-6 rounded-full gradient-brand text-white flex items-center justify-center text-[10px] font-bold shrink-0">{{ item.round }}</span>
              <div>
                <p class="font-bold" :class="isDark ? 'text-slate-200' : 'text-slate-700'">{{ item.title }}</p>
                <p class="mt-0.5" :class="isDark ? 'text-slate-400' : 'text-slate-500'">{{ item.insightPreview }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { Lock, Lightbulb } from 'lucide-vue-next'
import { useAnalysisStore } from '@/stores/analysis'
import { useConfigStore } from '@/stores/config'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const analysisStore = useAnalysisStore()
const configStore = useConfigStore()
const isDark = computed(() => configStore.isDarkMode)
const { dataUnlocked, insightCardData, radarChartData, debateTimelineData, trendChartData, platformStats } = storeToRefs(analysisStore)

const activeTab = ref('overview')
const tabs = [
  { id: 'overview', name: '总览' },
  { id: 'charts', name: '图表分析' },
]

const radarCanvasRef = ref(null)
const trendCanvasRef = ref(null)
let radarChart = null
let trendChart = null

const statsCards = computed(() => {
  const insights = insightCardData.value
  return [
    { label: '覆盖平台', value: insights.coverage.platforms, color: 'text-brand-500' },
    { label: '辩论轮数', value: insights.coverage.debateRounds, color: 'text-purple-500' },
    { label: '争议程度', value: insights.coverage.controversy, color: 'text-orange-500' },
  ]
})

const platformHeatData = computed(() => {
  const stats = platformStats.value || {}
  const max = Math.max(...Object.values(stats), 1)
  const nameMap = { wb: '微博', bili: 'B站', xhs: '小红书', dy: '抖音', ks: '快手', tieba: '贴吧', zhihu: '知乎', hn: 'HN' }
  return Object.entries(stats).map(([code, count]) => ({
    name: nameMap[code] || code,
    value: count,
    percent: Math.round((count / max) * 100)
  }))
})

function renderRadarChart() {
  if (!radarCanvasRef.value || !radarChartData.value || !radarChartData.value.labels.length) return
  if (radarChart) radarChart.destroy()
  const ctx = radarCanvasRef.value.getContext('2d')
  const isDarkMode = isDark.value
  radarChart = new Chart(ctx, {
    type: 'radar',
    data: radarChartData.value,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          ticks: { display: false },
          grid: { color: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(203, 213, 225, 0.5)' },
          pointLabels: { color: isDarkMode ? '#94a3b8' : '#64748b', font: { size: 11 } },
        }
      },
      plugins: { legend: { display: false } },
    },
  })
}

function renderTrendChart() {
  if (!trendCanvasRef.value || !trendChartData.value || !trendChartData.value.curve) return
  if (trendChart) trendChart.destroy()
  const ctx = trendCanvasRef.value.getContext('2d')
  const isDarkMode = isDark.value
  const curve = trendChartData.value.curve
  trendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['起', '承', '转', '辩', '论', '结', '定'],
      datasets: [{
        label: '热度',
        data: curve,
        borderColor: '#06b6d4',
        backgroundColor: 'rgba(6, 182, 212, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: '#06b6d4',
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          min: 0,
          max: 100,
          ticks: { display: false },
          grid: { color: isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(203, 213, 225, 0.5)' },
        },
        x: {
          grid: { display: false },
          ticks: { color: isDarkMode ? '#94a3b8' : '#64748b', font: { size: 10 } },
        },
      },
      plugins: { legend: { display: false } },
    },
  })
}

watch(dataUnlocked, (unlocked) => {
  if (unlocked) {
    nextTick(() => {
      renderRadarChart()
      renderTrendChart()
    })
  }
})

watch(isDark, () => {
  nextTick(() => {
    renderRadarChart()
    renderTrendChart()
  })
})
</script>
