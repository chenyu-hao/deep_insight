<template>
  <aside
    class="fixed left-0 top-0 h-full z-50 flex flex-col transition-all duration-300 border-r"
    :class="[
      collapsed ? 'w-16' : 'w-56',
      isDark ? 'bg-slate-900 border-slate-700' : 'bg-white border-slate-200'
    ]"
  >
    <router-link to="/home" class="flex items-center gap-3 px-4 h-16 border-b shrink-0"
      :class="isDark ? 'border-slate-700' : 'border-slate-100'"
    >
      <div class="w-8 h-8 rounded-lg gradient-brand flex items-center justify-center text-white font-bold text-sm shrink-0">
        H
      </div>
      <transition name="fade-slide">
        <span v-if="!collapsed" class="font-bold text-base transition-colors whitespace-nowrap"
          :class="isDark ? 'text-white' : 'text-slate-800'"
        >
          狩辩 <span class="text-gradient-brand font-medium">HuntDebate</span>
        </span>
      </transition>
    </router-link>

    <nav class="flex-1 overflow-y-auto py-3 px-2 space-y-1">
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group relative"
        :class="[
          isActive(item.to)
            ? (isDark ? 'bg-brand-500/15 text-brand-400' : 'bg-brand-50 text-brand-600')
            : (isDark ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-800' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50')
        ]"
        :title="item.label"
      >
        <component :is="item.icon" :class="['w-5 h-5 shrink-0', isActive(item.to) ? '' : '']" />
        <transition name="fade-slide">
          <span v-if="!collapsed" class="whitespace-nowrap">{{ item.label }}</span>
        </transition>
        <div v-if="isActive(item.to)" class="absolute right-0 top-1/2 -translate-y-1/2 w-0.5 h-6 rounded-full"
          :class="isDark ? 'bg-brand-400' : 'bg-brand-500'"
        />
      </router-link>
    </nav>

    <div class="border-t px-3 py-2 space-y-1 shrink-0"
      :class="isDark ? 'border-slate-700' : 'border-slate-100'"
    >
      <router-link
        to="/settings"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200"
        :class="[
          isActive('/settings')
            ? (isDark ? 'bg-brand-500/15 text-brand-400' : 'bg-brand-50 text-brand-600')
            : (isDark ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-800' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50')
        ]"
        title="设置"
      >
        <Settings class="w-5 h-5 shrink-0" />
        <transition name="fade-slide">
          <span v-if="!collapsed" class="whitespace-nowrap">设置</span>
        </transition>
      </router-link>

      <button
        @click="$emit('toggle-collapse')"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 w-full"
        :class="isDark ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-800' : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'"
      >
        <component :is="collapsed ? PanelRight : PanelLeft" class="w-5 h-5 shrink-0" />
        <transition name="fade-slide">
          <span v-if="!collapsed" class="whitespace-nowrap text-xs">收起菜单</span>
        </transition>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useConfigStore } from '@/stores/config'
import { Search, TrendingUp, BarChart3, Settings, PanelLeft, PanelRight } from 'lucide-vue-next'

defineEmits(['toggle-collapse'])

const props = defineProps({
  collapsed: { type: Boolean, default: false }
})

const route = useRoute()
const configStore = useConfigStore()
const isDark = computed(() => configStore.isDarkMode)

const navItems = [
  { to: '/home', label: '舆情推演', icon: Search },
  { to: '/hot', label: '热榜选题', icon: TrendingUp },
  { to: '/data', label: '数据洞察', icon: BarChart3 },
]

function isActive(path) {
  return route.path === path
}
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.2s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}
</style>
