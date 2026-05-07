<template>
  <div class="min-h-screen flex transition-colors duration-300"
    :class="isDark ? 'bg-slate-950' : 'bg-slate-50'"
  >
    <Sidebar :collapsed="collapsed" @toggle-collapse="collapsed = !collapsed" />

    <div class="flex-1 flex flex-col transition-all duration-300"
      :style="{ marginLeft: collapsed ? '64px' : '224px' }"
    >
      <TopBar />

      <main class="h-0 flex-1 overflow-hidden">
        <router-view />
      </main>

      <footer class="border-t py-3 px-6 transition-colors duration-300"
        :class="isDark ? 'bg-slate-900/80 border-slate-700' : 'bg-white border-slate-200'"
      >
        <div class="flex items-center justify-between text-xs"
          :class="isDark ? 'text-slate-500' : 'text-slate-400'"
        >
          <span>狩辩 HuntDebate · Powered by Multi-Agent Debate + LangGraph</span>
          <span>© 2026 chenyuhao</span>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Sidebar from '@/components/Sidebar.vue'
import TopBar from '@/components/TopBar.vue'
import { useConfigStore } from '@/stores/config'

const collapsed = ref(false)
const configStore = useConfigStore()
const isDark = computed(() => configStore.isDarkMode)

onMounted(() => {
  configStore.initDarkMode()
})
</script>
