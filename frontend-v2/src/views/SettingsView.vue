<template>
  <div class="h-full overflow-auto p-4 animate-fade-in space-y-6">
    <div>
      <h1 class="text-2xl font-extrabold" :class="isDark ? 'text-white' : 'text-slate-800'">设置</h1>
      <p class="text-sm mt-1" :class="isDark ? 'text-slate-400' : 'text-slate-500'">API 配置 · 平台选择 · 模型管理</p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 p-1 rounded-xl w-fit"
      :class="isDark ? 'bg-slate-800' : 'bg-slate-100'">
      <button v-for="tab in settingTabs" :key="tab.id" @click="activeTab = tab.id"
        class="px-4 py-2 rounded-lg text-xs font-bold transition-all"
        :class="activeTab === tab.id
          ? (isDark ? 'bg-brand-500 text-white shadow' : 'bg-white text-brand-600 shadow-sm')
          : (isDark ? 'text-slate-400 hover:text-slate-200' : 'text-slate-500 hover:text-slate-700')">
        <component :is="tab.icon" class="w-3.5 h-3.5 inline mr-1" />
        {{ tab.name }}
      </button>
    </div>

    <!-- Platform Selection -->
    <div v-if="activeTab === 'platforms'" class="rounded-xl border p-6"
      :class="isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'">
      <h3 class="text-sm font-bold mb-1" :class="isDark ? 'text-slate-200' : 'text-slate-700'">数据源平台选择</h3>
      <p class="text-xs mb-4" :class="isDark ? 'text-slate-500' : 'text-slate-400'">选择要爬取数据的平台（未选择则默认爬取所有平台）</p>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        <label v-for="p in availablePlatforms" :key="p.code"
          class="flex items-center gap-2 p-3 rounded-lg border-2 cursor-pointer transition"
          :class="selectedPlatforms.includes(p.code)
            ? (isDark ? 'border-brand-500 bg-brand-500/10' : 'border-brand-500 bg-brand-50')
            : (isDark ? 'border-slate-700 hover:border-slate-600' : 'border-slate-200 hover:border-slate-300')">
          <input type="checkbox" :value="p.code" v-model="selectedPlatforms" @change="savePlatformSelection"
            class="rounded text-brand-500 focus:ring-brand-500" />
          <span class="text-sm font-medium" :class="isDark ? 'text-slate-300' : 'text-slate-600'">{{ p.name }}</span>
        </label>
      </div>
      <p class="text-xs mt-3" :class="isDark ? 'text-slate-500' : 'text-slate-400'">
        已选择: {{ selectedPlatforms.length === 0 ? '全部平台（默认）' : selectedPlatforms.join('、') }}
      </p>
    </div>

    <!-- API Configuration -->
    <div v-if="activeTab === 'api'" class="rounded-xl border p-6"
      :class="isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-sm font-bold" :class="isDark ? 'text-slate-200' : 'text-slate-700'">API 接口配置</h3>
          <p class="text-xs mt-0.5" :class="isDark ? 'text-slate-500' : 'text-slate-400'">已配置 {{ userApis.length }} 个模型</p>
        </div>
        <div class="flex gap-2">
          <button @click="clearAllSettings"
            class="px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1"
            :class="isDark ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20' : 'bg-red-50 text-red-600 hover:bg-red-100'">
            <Trash2 class="w-3 h-3" />清除缓存
          </button>
          <button @click="openEditModal()"
            class="px-4 py-1.5 rounded-lg text-white text-xs font-bold gradient-brand hover:opacity-90 transition flex items-center gap-1">
            <Plus class="w-3 h-3" />添加 API
          </button>
        </div>
      </div>

      <div v-if="userApis.length === 0" class="text-center py-12 border-2 border-dashed rounded-xl"
        :class="isDark ? 'border-slate-700 text-slate-500' : 'border-slate-200 text-slate-400'">
        <Server class="w-10 h-10 mx-auto mb-2 opacity-40" />
        <p class="text-xs">暂无配置的 API 接口</p>
        <p class="text-[10px] mt-1 opacity-60">当前使用后端环境变量中的 API Key</p>
      </div>

      <div v-else class="space-y-2">
        <div v-for="api in userApis" :key="api.id"
          class="flex items-center justify-between p-3 rounded-lg border animate-fade-in"
          :class="isDark ? 'border-slate-700 bg-slate-900/50' : 'border-slate-100 bg-slate-50'">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-8 h-8 rounded-full gradient-brand flex items-center justify-center text-white text-xs font-bold shrink-0">
              {{ (api.provider || '').substring(0, 2).toUpperCase() }}
            </div>
            <div class="min-w-0">
              <p class="text-sm font-bold truncate" :class="isDark ? 'text-slate-200' : 'text-slate-700'">
                {{ api.provider }}
                <span v-if="api.model" class="font-normal" :class="isDark ? 'text-slate-400' : 'text-slate-500'"> · {{ api.model }}</span>
              </p>
              <p class="text-xs font-mono truncate" :class="isDark ? 'text-slate-500' : 'text-slate-400'">
                ...{{ (api.key || '').slice(-4) }}
              </p>
            </div>
          </div>
          <div class="flex gap-1 shrink-0">
            <button @click="openEditModal(api.id)" class="p-1.5 rounded transition"
              :class="isDark ? 'text-slate-400 hover:text-brand-400 hover:bg-slate-800' : 'text-slate-400 hover:text-brand-600 hover:bg-slate-100'">
              <Edit2 class="w-3.5 h-3.5" />
            </button>
            <button @click="removeApi(api.id)" class="p-1.5 rounded transition"
              :class="isDark ? 'text-slate-400 hover:text-red-400 hover:bg-slate-800' : 'text-slate-400 hover:text-red-500 hover:bg-slate-100'">
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Model Management -->
    <div v-if="activeTab === 'models'" class="rounded-xl border p-6"
      :class="isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-sm font-bold" :class="isDark ? 'text-slate-200' : 'text-slate-700'">Agent 模型绑定</h3>
        <button @click="saveAgentOverrides"
          class="px-4 py-1.5 rounded-lg text-white text-xs font-bold gradient-brand hover:opacity-90 transition flex items-center gap-1">
          <Save class="w-3 h-3" />保存绑定
        </button>
      </div>
      <p class="text-xs mb-4" :class="isDark ? 'text-slate-500' : 'text-slate-400'">
        为每个 Agent 选择 API；未选择则使用后端默认配置。
      </p>

      <div v-if="userApis.length === 0" class="p-3 rounded-lg border text-xs flex items-center gap-2"
        :class="isDark ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' : 'bg-amber-50 border-amber-200 text-amber-700'">
        <AlertTriangle class="w-3.5 h-3.5" />
        <span>请先在「API 配置」中添加 API Key</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
        <div v-for="a in agentList" :key="a.key"
          class="p-3 rounded-lg border transition"
          :class="isDark ? 'border-slate-700 hover:border-slate-600' : 'border-slate-200 hover:border-slate-300'">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-8 h-8 rounded-full gradient-brand flex items-center justify-center text-white text-xs font-bold shrink-0">
              {{ a.name.substring(0, 2).toUpperCase() }}
            </div>
            <div class="min-w-0">
              <p class="text-sm font-bold" :class="isDark ? 'text-slate-200' : 'text-slate-700'">{{ a.name }}</p>
              <p class="text-[10px] truncate" :class="isDark ? 'text-slate-500' : 'text-slate-400'">{{ a.desc }}</p>
            </div>
          </div>
          <select v-model="agentOverrides[a.key].apiId"
            class="w-full px-2.5 py-1.5 rounded border text-xs outline-none transition"
            :class="isDark ? 'bg-slate-900 border-slate-600 text-slate-200 focus:border-brand-500' : 'bg-white border-slate-200 text-slate-700 focus:border-brand-500'">
            <option value="">后端默认</option>
            <option v-for="api in userApis" :key="api.id" :value="api.id">
              {{ api.provider }}{{ api.model ? ' - ' + api.model : '' }} (...{{ (api.key || '').slice(-4) }})
            </option>
          </select>
        </div>
      </div>
      <p v-if="agentOverridesSaved" class="mt-3 p-2.5 rounded-lg text-xs flex items-center gap-2"
        :class="isDark ? 'bg-green-500/10 text-green-400' : 'bg-green-50 text-green-700'">
        <Check class="w-3.5 h-3.5" />Agent 绑定已保存
      </p>
    </div>

    <!-- Add/Edit API Modal -->
    <Teleport to="body">
      <div v-if="showApiModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showApiModal = false">
        <div class="w-full max-w-md mx-4 rounded-xl p-6 animate-fade-in"
          :class="isDark ? 'bg-slate-800' : 'bg-white'">
          <h3 class="text-lg font-bold mb-4" :class="isDark ? 'text-white' : 'text-slate-800'">
            {{ editingApiId ? '编辑 API' : '添加 API' }}
          </h3>

          <div class="space-y-3">
            <div>
              <label class="text-xs font-bold block mb-1" :class="isDark ? 'text-slate-400' : 'text-slate-600'">提供商</label>
              <select v-model="apiForm.provider"
                class="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                :class="isDark ? 'bg-slate-900 border-slate-600 text-slate-200' : 'bg-white border-slate-200 text-slate-700'">
                <option value="">选择提供商</option>
                <option value="deepseek">DeepSeek</option>
                <option value="gemini">Gemini</option>
                <option value="openai">OpenAI</option>
                <option value="doubao">豆包 (Doubao)</option>
                <option value="zhipu">智谱 (Zhipu)</option>
                <option value="minimax">MiniMax</option>
                <option value="moonshot">Moonshot (Kimi)</option>
              </select>
            </div>

            <div>
              <label class="text-xs font-bold block mb-1" :class="isDark ? 'text-slate-400' : 'text-slate-600'">API Key</label>
              <input v-model="apiForm.key" type="password"
                class="w-full px-3 py-2 rounded-lg border text-sm outline-none font-mono"
                :class="isDark ? 'bg-slate-900 border-slate-600 text-slate-200' : 'bg-white border-slate-200 text-slate-700'"
                placeholder="sk-..." />
            </div>

            <div>
              <label class="text-xs font-bold block mb-1" :class="isDark ? 'text-slate-400' : 'text-slate-600'">模型名称 (可选)</label>
              <input v-model="apiForm.model"
                class="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                :class="isDark ? 'bg-slate-900 border-slate-600 text-slate-200' : 'bg-white border-slate-200 text-slate-700'"
                placeholder="留空使用默认" />
            </div>
          </div>

          <div class="flex gap-2 mt-5">
            <button @click="showApiModal = false" class="flex-1 px-4 py-2 rounded-lg border text-sm font-bold transition"
              :class="isDark ? 'border-slate-600 text-slate-300 hover:bg-slate-700' : 'border-slate-200 text-slate-500 hover:bg-slate-50'">
              取消
            </button>
            <button @click="saveApi" :disabled="!apiForm.provider || !apiForm.key"
              class="flex-1 px-4 py-2 rounded-lg text-white text-sm font-bold gradient-brand hover:opacity-90 transition disabled:opacity-50">
              {{ editingApiId ? '更新' : '添加' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'
import { useConfigStore } from '@/stores/config'
import { Globe, Server, Cpu, Plus, Trash2, Edit2, Save, Check, AlertTriangle } from 'lucide-vue-next'
import { api } from '@/api'

const analysisStore = useAnalysisStore()
const configStore = useConfigStore()
const isDark = computed(() => configStore.isDarkMode)

const activeTab = ref('platforms')
const selectedPlatforms = ref([])
const userApis = ref([])
const showApiModal = ref(false)
const editingApiId = ref(null)
const agentOverrides = reactive({})
const agentOverridesSaved = ref(false)

const settingTabs = [
  { id: 'platforms', name: '平台选择', icon: Globe },
  { id: 'api', name: 'API 配置', icon: Server },
  { id: 'models', name: '模型绑定', icon: Cpu },
]

const availablePlatforms = [
  { code: 'wb', name: '微博' },
  { code: 'bili', name: 'B站' },
  { code: 'xhs', name: '小红书' },
  { code: 'dy', name: '抖音' },
  { code: 'ks', name: '快手' },
  { code: 'tieba', name: '贴吧' },
  { code: 'zhihu', name: '知乎' },
  { code: 'hn', name: 'Hacker News' },
]

const agentList = [
  { key: 'crawler', name: '数据爬取', desc: '多平台数据采集' },
  { key: 'reporter', name: '事实提取', desc: '结构化报告生成' },
  { key: 'analyst', name: '舆情分析', desc: '深度洞察分析' },
  { key: 'debater', name: '智能辩论', desc: '多角度辩证推理' },
  { key: 'writer', name: '文案生成', desc: '爆款内容创作' },
  { key: 'image_gen', name: '配图生成', desc: 'AI 图文匹配' },
]

const apiForm = reactive({
  provider: '',
  key: '',
  model: '',
})

function savePlatformSelection() {
  analysisStore.setSelectedPlatforms(selectedPlatforms.value)
}

function openEditModal(apiId = null) {
  editingApiId.value = apiId
  if (apiId) {
    const existing = userApis.value.find(a => a.id === apiId)
    if (existing) {
      apiForm.provider = existing.provider
      apiForm.key = existing.key
      apiForm.model = existing.model || ''
    }
  } else {
    apiForm.provider = ''
    apiForm.key = ''
    apiForm.model = ''
  }
  showApiModal.value = true
}

function saveApi() {
  if (!apiForm.provider || !apiForm.key) return
  if (editingApiId.value) {
    const idx = userApis.value.findIndex(a => a.id === editingApiId.value)
    if (idx >= 0) {
      userApis.value[idx] = {
        ...userApis.value[idx],
        provider: apiForm.provider,
        key: apiForm.key,
        model: apiForm.model || null,
      }
    }
  } else {
    userApis.value.push({
      id: 'api_' + Date.now(),
      provider: apiForm.provider,
      key: apiForm.key,
      model: apiForm.model || null,
      providerKey: apiForm.provider,
    })
  }
  configStore.saveUserApis(userApis.value)
  showApiModal.value = false
  editingApiId.value = null
}

function removeApi(apiId) {
  userApis.value = userApis.value.filter(a => a.id !== apiId)
  configStore.saveUserApis(userApis.value)
}

function clearAllSettings() {
  if (confirm('确定要清除所有 API 配置吗？')) {
    userApis.value = []
    configStore.saveUserApis([])
    Object.keys(agentOverrides).forEach(k => { agentOverrides[k] = { apiId: '' } })
    saveAgentOverrides()
    localStorage.removeItem('huntdebate_agent_overrides')
  }
}

function saveAgentOverrides() {
  const data = {}
  Object.entries(agentOverrides).forEach(([key, val]) => { data[key] = val.apiId || null })
  localStorage.setItem('huntdebate_agent_overrides', JSON.stringify(data))
  agentOverridesSaved.value = true
  setTimeout(() => { agentOverridesSaved.value = false }, 2000)
}

onMounted(() => {
  selectedPlatforms.value = analysisStore.selectedPlatforms.length > 0 ? [...analysisStore.selectedPlatforms] : []
  userApis.value = configStore.getUserApis || []

  agentList.forEach(a => {
    agentOverrides[a.key] = { apiId: '' }
  })
  const saved = localStorage.getItem('huntdebate_agent_overrides')
  if (saved) {
    try {
      const data = JSON.parse(saved)
      Object.entries(data).forEach(([key, val]) => {
        if (agentOverrides[key]) agentOverrides[key].apiId = val || ''
      })
    } catch (e) {}
  }
})
</script>
