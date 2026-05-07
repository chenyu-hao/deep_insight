<template>
  <div class="h-full flex flex-col p-4 animate-fade-in">
    <!-- Workflow Stepper (compact) -->
    <div v-if="isLoading && workflowStatus.running" class="mb-3 shrink-0">
      <div class="rounded-lg p-3 border shadow-sm"
        :class="isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'">
        <div class="flex items-center gap-2 mb-2">
          <Activity class="w-3.5 h-3.5 text-brand-500" />
          <span class="text-xs font-bold" :class="isDark ? 'text-slate-200' : 'text-slate-700'">工作流</span>
          <span class="text-[10px] ml-auto font-bold text-brand-500">{{ displayProgress }}%</span>
          <span class="text-[10px]" :class="isDark ? 'text-slate-500' : 'text-slate-400'">{{ elapsedTime }}</span>
        </div>
        <div class="w-full h-1 rounded-full overflow-hidden mb-2"
          :class="isDark ? 'bg-slate-700' : 'bg-slate-100'">
          <div class="h-full rounded-full gradient-brand transition-all duration-500" :style="{ width: displayProgress + '%' }"></div>
        </div>
        <div class="grid grid-cols-6 gap-1.5">
          <div v-for="step in workflowSteps" :key="step.key"
            class="flex flex-col items-center gap-0.5 p-1.5 rounded-lg transition-all duration-300"
            :class="getStepStyle(step.key)">
            <component :is="step.icon" class="w-3.5 h-3.5" />
            <span class="text-[9px] font-bold leading-tight text-center">{{ step.name }}</span>
            <span v-if="step.key === 'crawler_agent' && workflowStatus.current_step === 'crawler_agent' && workflowStatus.current_platform"
              class="text-[7px] font-medium animate-pulse text-brand-400 line-clamp-1">
              {{ workflowStatus.current_platform }}
            </span>
          </div>
        </div>
        <div class="text-[10px]" :class="isDark ? 'text-slate-400' : 'text-slate-500'">{{ currentStepText }}</div>
      </div>
    </div>

    <!-- Main Two-Column Area (fills remaining height) -->
    <div class="flex-1 min-h-0 grid grid-cols-3 gap-4">
      <!-- Left: 2 cols -->
      <div class="col-span-2 flex flex-col gap-3 min-h-0">
        <!-- Search (compact) -->
        <div class="rounded-lg p-3 border shadow-sm shrink-0"
          :class="isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'">
          <div class="flex items-center gap-2">
            <div class="relative flex-1">
              <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5" :class="isDark ? 'text-slate-500' : 'text-slate-400'" />
              <input
                v-model="topic"
                type="text"
                class="w-full pl-8 pr-16 py-2 rounded-lg border text-xs font-medium outline-none"
                :class="isDark ? 'bg-slate-900 border-slate-600 text-slate-200 placeholder-slate-500 focus:border-brand-500' : 'bg-slate-50 border-slate-200 text-slate-800 placeholder-slate-400 focus:border-brand-500'"
                placeholder="输入议题..."
                @keyup.enter="handleStart"
              />
              <div class="absolute right-1.5 top-1/2 -translate-y-1/2 flex items-center gap-1">
                <input v-model.number="debateRounds" type="number" min="1" max="5" title="轮数"
                  class="w-8 text-center text-[10px] rounded border py-0.5 outline-none"
                  :class="isDark ? 'bg-slate-800 border-slate-600 text-slate-300' : 'bg-white border-slate-200 text-slate-600'" />
              </div>
            </div>
            <button @click="handleStart"
              class="px-4 py-2 rounded-lg text-white font-bold text-xs transition flex items-center gap-1.5 shadow whitespace-nowrap"
              :class="isLoading ? 'bg-red-500 hover:bg-red-600' : 'gradient-brand hover:opacity-90'">
              <Square v-if="isLoading" class="w-3.5 h-3.5" /><Zap v-else class="w-3.5 h-3.5" />
              {{ isLoading ? '停止' : '启动' }}
            </button>
          </div>
          <div v-if="trendingTopics.length" class="mt-2 flex items-center gap-1.5 text-[10px] flex-wrap">
            <span class="font-bold text-red-500 whitespace-nowrap"><Flame class="w-2.5 h-2.5 inline" /> {{ trendingDate }}</span>
            <button v-for="t in trendingTopics" :key="t.title" @click="topic = t.title"
              class="px-2 py-0.5 rounded-full border text-[10px] transition whitespace-nowrap"
              :class="isDark ? 'border-slate-600 text-slate-400 hover:border-brand-500' : 'border-slate-200 text-slate-500 hover:border-brand-300'">{{ t.short }}</button>
            <button @click="rotateTrending" class="p-0.5 rounded transition"
              :class="isDark ? 'text-slate-500 hover:text-slate-300' : 'text-slate-400 hover:text-slate-600'"><RefreshCw class="w-2.5 h-2.5" /></button>
          </div>
          <div v-if="error" class="mt-2 p-2 rounded text-[10px] bg-red-50 text-red-600 border border-red-100">{{ error }}</div>
        </div>

        <!-- Debate Bubbles (fills remaining left space) -->
        <div class="rounded-lg border shadow-sm flex flex-col flex-1 min-h-0 overflow-hidden"
          :class="isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'">
          <div class="px-3 py-2 border-b flex items-center justify-between shrink-0"
            :class="isDark ? 'border-slate-700 bg-slate-800/50' : 'border-slate-100 bg-slate-50/50'">
            <span class="text-xs font-bold flex items-center gap-1.5" :class="isDark ? 'text-slate-200' : 'text-slate-700'">
              <Cpu class="w-3.5 h-3.5 text-brand-500" />Multi-Agent Debate
            </span>
            <div class="flex items-center gap-1.5">
              <span v-if="currentRound > 0" class="text-[10px] font-bold px-1.5 py-0.5 rounded-full"
                :class="isDark ? 'bg-brand-500/20 text-brand-400' : 'bg-brand-500/10 text-brand-600'">第{{ currentRound }}轮</span>
              <span class="text-[10px]" :class="isDark ? 'text-slate-500' : 'text-slate-400'">{{ activeModel }}</span>
            </div>
          </div>
          <div ref="bubbleContainer" class="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2">
            <div v-if="debateLogs.length === 0" class="h-full flex flex-col items-center justify-center"
              :class="isDark ? 'text-slate-600' : 'text-slate-300'">
              <Cpu class="w-10 h-10 mb-2 opacity-50" />
              <p class="text-[10px]">等待指令启动...</p>
            </div>
            <div v-for="(log, idx) in debateLogs" :key="`log-${idx}-${log.name}`">
              <div v-if="log.roundLabel" class="text-[10px] font-bold text-center py-0.5 opacity-50"
                :class="isDark ? 'text-slate-500' : 'text-slate-400'">── {{ log.roundLabel }} ──</div>
              <div class="animate-fade-in p-2.5 rounded-lg border text-[11px] shadow-sm" :class="getBubbleStyle(log.role)">
                <div class="flex items-center gap-1.5 mb-1 pb-1 border-b" :class="isDark ? 'border-slate-700/50' : 'border-slate-200/50'">
                  <div class="w-4 h-4 rounded-full flex items-center justify-center text-[8px] font-bold shrink-0" :class="getRoleBadgeStyle(log.role)">{{ getRoleBadgeLabel(log.role) }}</div>
                  <span class="font-bold text-[11px]">{{ log.name }}</span>
                  <span v-if="log.model" class="ml-auto text-[8px] px-1 py-0.5 rounded" :class="isDark ? 'bg-slate-800 text-slate-500' : 'bg-slate-100 text-slate-400'">{{ log.model }}</span>
                </div>
                <div class="prose prose-xs max-w-none" :class="isDark ? 'text-slate-300' : 'text-slate-600'" v-html="renderMarkdown(log.content)"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Insight (compact, bottom of left) -->
        <div class="rounded-lg p-3 border shadow-sm shrink-0"
          :class="isDark ? 'bg-slate-800 border-l-2 border-l-amber-500 border-slate-700' : 'bg-white border-l-2 border-l-amber-500 border-slate-100'">
          <h3 class="text-xs font-bold mb-1.5 flex items-center gap-1.5" :class="isDark ? 'text-slate-200' : 'text-slate-700'">
            <Lightbulb class="w-3.5 h-3.5 text-amber-400" />核心洞察
          </h3>
          <div v-if="!insight" class="flex items-center justify-center py-3 text-[10px] italic"
            :class="isDark ? 'text-slate-500 border border-dashed border-slate-700 rounded' : 'text-slate-400 border border-dashed border-slate-200 rounded'">等待辩论结论产出...</div>
          <div v-else class="rounded p-3 text-xs leading-relaxed animate-fade-in"
            :class="isDark ? 'bg-gradient-to-br from-amber-500/8 to-yellow-500/5 text-slate-300 border border-amber-500/10' : 'bg-gradient-to-br from-amber-50 to-yellow-50 text-slate-700 border border-amber-100'">{{ insight }}</div>
        </div>
      </div>

      <!-- Right: 1 col (Copy Editor fills all) -->
      <div class="flex flex-col gap-3 min-h-0">
        <!-- Preview toggle button -->
        <button @click="showPhonePreview = !showPhonePreview"
          class="flex items-center justify-center gap-1.5 py-1.5 rounded-lg border text-[10px] font-bold transition shrink-0"
          :class="[
            showPhonePreview
              ? (isDark ? 'border-brand-500/50 text-brand-400 bg-brand-500/10' : 'border-brand-300 text-brand-600 bg-brand-50')
              : (isDark ? 'border-slate-700 text-slate-400 hover:bg-slate-800' : 'border-slate-200 text-slate-500 hover:bg-slate-50')
          ]">
          <Smartphone class="w-3 h-3" />{{ showPhonePreview ? '隐藏预览' : '查看预览' }}
        </button>

        <!-- Copy Editor (fills all right space) -->
        <div class="rounded-lg border shadow-sm flex flex-col flex-1 min-h-0 overflow-hidden"
          :class="isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'">
          <div class="px-3 py-2 border-b flex items-center justify-between shrink-0"
            :class="isDark ? 'border-slate-700 bg-slate-800/50' : 'border-slate-100 bg-slate-50/50'">
            <span class="text-xs font-bold flex items-center gap-1.5" :class="isDark ? 'text-slate-200' : 'text-slate-700'">
              <PenTool class="w-3.5 h-3.5 text-emerald-400" />文案编辑
            </span>
            <div class="flex items-center gap-1">
              <button @click="analysisStore.startEditing()" :disabled="!finalCopy"
                class="px-2 py-1 rounded text-[10px] font-bold bg-brand-500 text-white hover:bg-brand-600 transition disabled:opacity-50 flex items-center gap-1">
                <Edit class="w-2.5 h-2.5" />编辑
              </button>
              <button @click="copyToClipboard" :disabled="!finalCopy"
                class="px-2 py-1 rounded text-[10px] font-bold border transition"
                :class="isDark ? 'border-slate-600 text-slate-400 hover:bg-slate-700' : 'border-slate-200 text-slate-500 hover:bg-slate-50'">
                <Copy class="w-2.5 h-2.5" />复制
              </button>
            </div>
          </div>
          <div class="flex-1 flex flex-col min-h-0 overflow-y-auto custom-scrollbar p-3 space-y-2">
            <textarea :value="finalCopy" readonly
              class="w-full flex-1 min-h-[100px] p-2 rounded border text-[11px] resize-none font-mono outline-none"
              :class="isDark ? 'bg-slate-900 border-slate-700 text-slate-300' : 'bg-slate-50 border-slate-200 text-slate-600'"
              placeholder="等待文案生成..."></textarea>

            <!-- Edit Panel -->
            <div v-if="analysisStore.isEditing" class="space-y-2 p-2 rounded border shrink-0"
              :class="isDark ? 'border-slate-700 bg-slate-900' : 'border-slate-200 bg-slate-50'">
              <input :value="analysisStore.editableContent.title"
                @input="analysisStore.updateEditableContent('title', ($event.target).value)"
                class="w-full px-2 py-1.5 rounded border text-[11px] outline-none"
                :class="isDark ? 'bg-slate-800 border-slate-600 text-slate-200' : 'bg-white border-slate-200 text-slate-700'"
                placeholder="标题" />
              <div class="flex-1 min-h-0">
                <textarea :value="analysisStore.editableContent.body"
                  @input="analysisStore.updateEditableContent('body', ($event.target).value)"
                  class="w-full h-full min-h-[80px] px-2 py-1.5 rounded border text-[11px] resize-none outline-none"
                  :class="isDark ? 'bg-slate-800 border-slate-600 text-slate-200' : 'bg-white border-slate-200 text-slate-700'"
                  placeholder="正文"></textarea>
              </div>
              <div class="flex gap-1.5">
                <button @click="analysisStore.saveEditing()" class="flex-1 py-1 rounded text-[10px] font-bold bg-emerald-500 text-white hover:bg-emerald-600 transition">保存</button>
                <button @click="analysisStore.cancelEditing()" class="flex-1 py-1 rounded text-[10px] font-bold border transition"
                  :class="isDark ? 'border-slate-600 text-slate-400 hover:bg-slate-800' : 'border-slate-200 text-slate-500 hover:bg-slate-50'">取消</button>
              </div>
            </div>

            <!-- XHS Publish -->
            <div v-if="finalCopy" class="border-t pt-2 shrink-0" :class="isDark ? 'border-slate-700' : 'border-slate-100'">
              <div class="flex items-center justify-between gap-1.5">
                <div class="flex items-center gap-1 text-[9px]">
                  <template v-if="xhsStatus.loading"><Loader2 class="w-2 h-2 animate-spin" />检查...</template>
                  <template v-else-if="xhsStatus.mcp_available && xhsStatus.login_status"><Check class="w-2 h-2 text-green-500" /><span class="text-green-500">已连接</span></template>
                  <template v-else-if="xhsStatus.mcp_available && !xhsStatus.login_status"><AlertTriangle class="w-2 h-2 text-amber-500" /><span class="text-amber-500">需登录</span></template>
                  <template v-else><XCircle class="w-2 h-2" :class="isDark ? 'text-slate-500' : 'text-slate-400'" /><span :class="isDark ? 'text-slate-500' : 'text-slate-400'">未连接</span></template>
                </div>
                <button @click="publishToXhs" :disabled="!finalCopy || isPublishing || !xhsStatus.mcp_available || !xhsStatus.login_status"
                  class="px-2.5 py-1 rounded text-[10px] font-bold transition flex items-center gap-1 disabled:opacity-50"
                  :class="(!xhsStatus.mcp_available || !xhsStatus.login_status)
                    ? (isDark ? 'bg-slate-700 text-slate-400' : 'bg-slate-100 text-slate-400')
                    : 'bg-red-500 hover:bg-red-600 text-white'">
                  <Upload v-if="!isPublishing" class="w-2.5 h-2.5" /><Loader2 v-else class="w-2.5 h-2.5 animate-spin" />
                  {{ isPublishing ? '发布中' : '发布' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Phone Preview Overlay (slide-in from right) -->
    <Teleport to="body">
      <Transition name="preview-slide">
        <div v-if="showPhonePreview" class="fixed inset-0 z-50 flex justify-end">
          <div class="absolute inset-0 bg-black/30" @click="showPhonePreview = false"></div>
          <div class="relative h-full w-[480px] rounded-l-2xl border-l shadow-2xl overflow-y-auto custom-scrollbar p-6 animate-fade-in"
            :class="isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-sm font-bold flex items-center gap-2" :class="isDark ? 'text-slate-200' : 'text-slate-700'">
                <Smartphone class="w-4 h-4 text-purple-400" />实时预览
              </h3>
              <button @click="showPhonePreview = false" class="p-1.5 rounded-lg transition"
                :class="isDark ? 'hover:bg-slate-700 text-slate-400' : 'hover:bg-slate-100 text-slate-500'">
                <X class="w-4 h-4" />
              </button>
            </div>
            <div class="flex justify-center">
              <div class="phone-preview overflow-hidden bg-white w-full max-w-[360px] flex flex-col border-[6px] border-black rounded-3xl shadow-2xl" style="aspect-ratio: 9/16; max-height: 80vh;">
                <div class="h-8 bg-white flex items-center justify-between px-4 flex-shrink-0 select-none">
                  <span class="text-[10px] font-bold text-slate-900">09:41</span>
                  <div class="w-14 h-6 bg-black rounded-full relative">
                    <div class="w-1.5 h-1.5 bg-gray-700 rounded-full absolute right-3.5 top-1/2 -translate-y-1/2"></div>
                  </div>
                  <div></div>
                </div>
                <div class="flex-1 flex flex-col overflow-hidden bg-white border-t border-slate-100">
                  <div class="flex-1 bg-slate-100 relative overflow-hidden" @click="switchPhoneImage">
                    <div v-if="displayImages[currentDisplayIndex] === null"
                      class="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-brand-500 to-blue-600">
                      <div class="text-center text-white p-5">
                        <span class="text-5xl block mb-2">{{ analysisStore.titleEmoji }}</span>
                        <p class="font-bold text-base">{{ xhsPreview.title || '标题生成中...' }}</p>
                      </div>
                    </div>
                    <img v-else :src="displayImages[currentDisplayIndex]" class="absolute inset-0 w-full h-full object-cover" />
                    <div v-if="totalDisplayImages > 1" class="absolute bottom-1.5 left-1/2 -translate-x-1/2 flex gap-1">
                      <div v-for="(_, i) in displayImages" :key="i" class="w-1.5 h-1.5 rounded-full transition-all"
                        :class="currentDisplayIndex === i ? 'bg-white scale-125' : 'bg-white/50'" />
                    </div>
                  </div>
                  <div class="p-3 flex-1 overflow-y-auto custom-scrollbar">
                    <h4 class="font-bold text-xs text-slate-900 mb-1">{{ xhsPreview.title || '标题生成中...' }}</h4>
                    <div v-if="!xhsPreview.content" class="space-y-2">
                      <div class="h-2 bg-slate-100 rounded w-full animate-pulse"></div>
                      <div class="h-2 bg-slate-100 rounded w-5/6 animate-pulse"></div>
                      <div class="h-2 bg-slate-100 rounded w-3/4 animate-pulse"></div>
                    </div>
                    <div v-else class="text-xs text-slate-600 prose prose-sm max-w-none" v-html="renderMarkdown(xhsPreview.content)"></div>
                  </div>
                  <div class="px-3 py-2.5 border-t border-slate-100 flex items-center gap-4 text-[10px] text-slate-400 flex-shrink-0">
                    <Heart class="w-3 h-3" />57 <MessageCircle class="w-3 h-3" />44 <Star class="w-3 h-3" />15
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import {
  Search, Zap, Square, Flame, RefreshCw, Cpu, Lightbulb,
  Smartphone, Heart, MessageCircle, Star, PenTool, Copy, Edit,
  Activity, Database, FileText, Brain, MessageSquare, PenLine, ImageIcon,
  Bot, Loader2, Check, AlertTriangle, XCircle, Upload
} from 'lucide-vue-next'
import { useAnalysisStore } from '@/stores/analysis'
import { useConfigStore } from '@/stores/config'
import { useWorkflowStore } from '@/stores/workflow'
import { api } from '@/api'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()
const analysisStore = useAnalysisStore()
const configStore = useConfigStore()
const workflowStore = useWorkflowStore()
const isDark = computed(() => configStore.isDarkMode)

const { logs: storeLogs, isEditing, editableContent } = storeToRefs(analysisStore)
const { status: workflowStatus } = storeToRefs(workflowStore)

const topic = ref('')
const debateRounds = ref(2)
const isLoading = computed(() => analysisStore.isLoading)
const error = computed(() => analysisStore.error)
const debateLogs = ref([])
const insight = computed(() => analysisStore.insight)
const xhsPreview = ref({ title: '', content: '' })
const finalCopy = computed(() => analysisStore.finalCopy.title && analysisStore.finalCopy.body ? `${analysisStore.finalCopy.title}\n\n${analysisStore.finalCopy.body}` : '')
const activeModel = ref('')
const trendingDate = ref('')
const trendingTopics = ref([])
const hotItemsAll = ref([])
const hotWindowIndex = ref(0)
const currentDisplayIndex = ref(0)
const bubbleContainer = ref(null)
const maxStepIndex = ref(-1)
const maxProgress = ref(0)
const showPhonePreview = ref(false)
const currentRound = ref(0)

const displayImages = computed(() => {
  const allImages = [null, ...analysisStore.dataViewImages, ...analysisStore.imageUrls]
  if (analysisStore.isEditing || (editableContent.value.selectedImageIndices.length > 0 && editableContent.value.selectedImageIndices.length < allImages.length))
    return editableContent.value.imageOrder.filter(idx => editableContent.value.selectedImageIndices.includes(idx)).map(idx => allImages[idx])
  return allImages
})
const totalDisplayImages = computed(() => displayImages.value.length)
const displayProgress = computed(() => Math.max(workflowStatus.value.progress || 0, maxProgress.value))

watch(() => workflowStatus.value.progress, (v) => { if (v > maxProgress.value) maxProgress.value = v })
watch(() => workflowStatus.value.current_step, (s) => {
  if (!s) return
  const idx = workflowSteps.findIndex(st => st.key === s)
  if (idx > maxStepIndex.value) maxStepIndex.value = idx
})

const workflowSteps = [
  { key: 'crawler_agent', name: '数据爬取', icon: Database },
  { key: 'reporter', name: '事实提取', icon: FileText },
  { key: 'analyst', name: '舆情分析', icon: Brain },
  { key: 'debater', name: '智能辩论', icon: MessageSquare },
  { key: 'writer', name: '文案生成', icon: PenLine },
  { key: 'image_generator', name: '配图生成', icon: ImageIcon },
]

const currentStepText = computed(() => {
  const step = workflowSteps.find(s => s.key === workflowStatus.value.current_step)
  if (!step) return '准备中...'
  if (step.key === 'crawler_agent' && workflowStatus.value.current_platform) return `正在${step.name}: ${workflowStatus.value.current_platform}...`
  return `正在${step.name}...`
})

const elapsedTime = computed(() => {
  if (!workflowStatus.value.started_at) return ''
  const diff = Math.floor((Date.now() - new Date(workflowStatus.value.started_at)) / 1000)
  return diff < 60 ? `${diff}秒` : `${Math.floor(diff / 60)}分${diff % 60}秒`
})

function getStepStyle(stepKey) {
  const cs = workflowStatus.value.current_step; const p = workflowStatus.value.progress
  const si = workflowSteps.findIndex(s => s.key === stepKey)
  if (p === 100) return isDark.value ? 'text-green-400 bg-green-500/10' : 'text-green-600 bg-green-50'
  if (!cs) return isDark.value ? 'text-slate-500 bg-slate-800' : 'text-slate-400 bg-slate-50'
  const ci = workflowSteps.findIndex(s => s.key === cs)
  if (si === ci) return isDark.value ? 'text-brand-400 bg-brand-500/15 shadow ring-1 ring-brand-500/30' : 'text-brand-600 bg-brand-50 shadow ring-1 ring-brand-300'
  if (si < ci || si <= maxStepIndex.value) return isDark.value ? 'text-green-400 bg-green-500/10' : 'text-green-600 bg-green-50'
  return isDark.value ? 'text-slate-500 bg-slate-800' : 'text-slate-400 bg-slate-50'
}

function renderMarkdown(text) { return text ? md.render(text) : '' }

function getBubbleStyle(role) {
  if (isDark.value) {
    const m = { moderator: 'border border-amber-500/30 bg-amber-500/5', pro: 'border border-blue-500/30 bg-blue-500/5', con: 'border border-orange-500/30 bg-orange-500/5', analyst: 'border border-violet-500/30 bg-violet-500/5', system: 'border border-slate-600 bg-slate-800/50' }
    return m[role] || 'border border-slate-600 bg-slate-800/50'
  }
  const m = { moderator: 'border border-amber-200 bg-amber-50', pro: 'border border-blue-200 bg-blue-50', con: 'border border-orange-200 bg-orange-50', analyst: 'border border-violet-200 bg-violet-50', system: 'border border-slate-200 bg-slate-50' }
  return m[role] || 'border border-slate-200 bg-slate-50'
}

function getRoleBadgeStyle(role) {
  if (isDark.value) return { moderator: 'bg-amber-500/20 text-amber-400', pro: 'bg-blue-500/20 text-blue-400', con: 'bg-orange-500/20 text-orange-400', analyst: 'bg-violet-500/20 text-violet-400', system: 'bg-slate-600 text-slate-300' }[role] || 'bg-slate-600 text-slate-300'
  return { moderator: 'bg-amber-100 text-amber-700', pro: 'bg-blue-100 text-blue-700', con: 'bg-orange-100 text-orange-700', analyst: 'bg-violet-100 text-violet-700', system: 'bg-slate-100 text-slate-600' }[role] || 'bg-slate-100 text-slate-600'
}
function getRoleBadgeLabel(role) { return { moderator: 'M', pro: 'P', con: 'O', analyst: 'A', system: 'S' }[role] || 'S' }

function switchPhoneImage() { currentDisplayIndex.value = (currentDisplayIndex.value + 1) % totalDisplayImages.value }
function copyToClipboard() { navigator.clipboard.writeText(finalCopy.value).then(() => alert('已复制')).catch(() => {}) }
function shortenTitle(t, max = 14) { const c = String(t || '').trim(); return c.length <= max ? c : c.slice(0, max) + '…' }

async function refreshTrending() {
  try {
    const res = await api.getHotNews(8, 'hot', false)
    const items = (res && res.items) ? res.items : []
    if (items.length > 0) { hotItemsAll.value = items.slice(0, 12).map(i => ({ title: i.title || '', short: shortenTitle(i.title) })); setTrendingWindow(0); trendingDate.value = `${new Date(res.collection_time || Date.now()).getMonth() + 1}月${new Date(res.collection_time || Date.now()).getDate()}日`; return }
  } catch (e) { console.warn('获取热榜失败', e) }
  const today = new Date(); trendingDate.value = `${today.getMonth() + 1}月${today.getDate()}日`
  hotItemsAll.value = ['AI监管', '油价调整', '高考分数线', '星舰发射', 'DeepSeek', '新能源车'].map(t => ({ title: t, short: t }))
  setTrendingWindow(0)
}

function setTrendingWindow(start = 0) {
  const list = hotItemsAll.value || []; if (!list.length) { trendingTopics.value = []; return }
  const len = list.length, s = ((start % len) + len) % len
  trendingTopics.value = Array.from({ length: Math.min(3, len) }, (_, i) => list[(s + i) % len])
  hotWindowIndex.value = s
}
function rotateTrending() { if (!hotItemsAll.value.length) { refreshTrending(); return }; setTrendingWindow(hotWindowIndex.value + 3) }

async function handleStart() {
  if (isLoading.value) { analysisStore.stopAnalysis(); return }
  if (!topic.value.trim()) { alert('请输入议题！'); return }
  debateLogs.value = []; xhsPreview.value = { title: '', content: '' }; maxStepIndex.value = -1; maxProgress.value = 0; currentRound.value = 0
  analysisStore.setDataViewImages([])
  try { await analysisStore.startAnalysis({ topic: topic.value, debate_rounds: debateRounds.value }) } catch (err) { alert('分析失败: ' + err.message) }
}

let analystCount = 0
watch(storeLogs, (newLogs, oldLogs) => {
  if (!newLogs || !newLogs.length) return
  const startIdx = (oldLogs && oldLogs.length) || 0; const newOnes = newLogs.slice(startIdx); if (!newOnes.length) return
  newOnes.forEach(log => {
    const roleMap = { 'Moderator': 'moderator', 'Crawler': 'system', 'Analyst': 'analyst', 'Debater': 'con', 'Reporter': 'system' }
    const name = log.agent_name || 'System', role = roleMap[log.agent_name] || 'system', content = log.step_content || ''
    if (log.agent_name === 'Analyst') {
      analystCount++; currentRound.value = analystCount
      debateLogs.value.push({ name, role, content, model: log.model, roundLabel: `第 ${analystCount} 轮辩论` })
      if (log.model) activeModel.value = log.model
    } else if (log.agent_name === 'Debater') {
      const parts = content.split(/---\s*/).filter(Boolean)
      parts.forEach((part, i) => {
        const m = part.match(/^(Moderator|Proponent|Opponent):\s*/)
        if (m) { const r = m[1] === 'Moderator' ? 'moderator' : m[1] === 'Proponent' ? 'pro' : 'con'; debateLogs.value.push({ name: `${name} - ${m[1]}`, role: r, content: part.replace(m[0], ''), model: log.model }) }
        else if (i === 0) debateLogs.value.push({ name, role, content, model: log.model })
      })
    } else { debateLogs.value.push({ name, role, content, model: log.model || activeModel.value }); if (log.model) activeModel.value = log.model }
  })
  nextTick(() => { if (bubbleContainer.value) bubbleContainer.value.scrollTop = bubbleContainer.value.scrollHeight })
})

watch(() => analysisStore.finalCopy, (fc) => { if (fc) xhsPreview.value = { title: fc.title || '', content: fc.body || '' } }, { deep: true })

const xhsStatus = ref({ mcp_available: false, login_status: false, message: '', loading: false })
const isPublishing = ref(false)

async function checkXhsStatus() {
  xhsStatus.value.loading = true
  try { const res = await api.getXhsStatus(); xhsStatus.value = { mcp_available: res.mcp_available, login_status: res.login_status, message: res.message, loading: false } }
  catch (e) { xhsStatus.value = { mcp_available: false, login_status: false, message: '', loading: false } }
}

async function publishToXhs() {
  if (!finalCopy.value || isPublishing.value) return; isPublishing.value = true
  try { const r = await api.publishToXhs({ title: analysisStore.finalCopy.title, content: analysisStore.finalCopy.body, images: analysisStore.imageUrls || [] }); alert(r.success ? '发布成功！' : '发布失败: ' + (r.message || '')) }
  catch (e) { alert('发布失败: ' + e.message) }
  finally { isPublishing.value = false }
}

onMounted(() => { refreshTrending(); setTimeout(() => checkXhsStatus(), 500) })
</script>

<style scoped>
.preview-slide-enter-active,
.preview-slide-leave-active {
  transition: all 0.3s ease;
}
.preview-slide-enter-from,
.preview-slide-leave-to {
  opacity: 0;
}
.preview-slide-enter-from :deep(.relative.h-full),
.preview-slide-leave-to :deep(.relative.h-full) {
  transform: translateX(100%);
}
</style>
