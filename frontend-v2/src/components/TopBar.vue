<template>
  <header
    class="h-16 flex items-center justify-between px-6 border-b transition-colors duration-300"
    :class="isDark ? 'bg-slate-900/90 border-slate-700 backdrop-blur-sm' : 'bg-white/90 border-slate-200 backdrop-blur-sm'"
  >
    <div class="flex items-center gap-3">
      <div class="text-sm font-medium"
        :class="isDark ? 'text-slate-400' : 'text-slate-500'"
      >
        <span :class="isDark ? 'text-slate-300' : 'text-slate-700'">{{ pageTitle }}</span>
      </div>

      <div v-if="workflowRunning" class="flex items-center gap-2 ml-4">
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
        </span>
        <span class="text-xs font-medium text-green-600">运行中</span>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <button
        @click="toggleTheme"
        class="p-2 rounded-lg transition-all duration-200"
        :class="isDark ? 'text-amber-400 hover:bg-slate-800' : 'text-slate-500 hover:bg-slate-100'"
        :title="isDark ? '浅色模式' : '深色模式'"
      >
        <Sun v-if="isDark" class="w-4.5 h-4.5" />
        <Moon v-else class="w-4.5 h-4.5" />
      </button>

      <a
        href="https://github.com"
        target="_blank"
        class="p-2 rounded-lg transition-all duration-200"
        :class="isDark ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-800' : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'"
        title="GitHub"
      >
        <Github class="w-4.5 h-4.5" />
      </a>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useConfigStore } from '@/stores/config'
import { useWorkflowStore } from '@/stores/workflow'
import { Sun, Moon, Github } from 'lucide-vue-next'

const route = useRoute()
const configStore = useConfigStore()
const workflowStore = useWorkflowStore()

const isDark = computed(() => configStore.isDarkMode)
const workflowRunning = computed(() => workflowStore.status.running)

const pageTitle = computed(() => {
  return (route.meta && route.meta.title) || '狩辩 HuntDebate'
})

function toggleTheme() {
  configStore.toggleDarkMode()
}
</script>
