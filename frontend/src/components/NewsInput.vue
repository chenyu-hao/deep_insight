<template>
  <div class="bg-white shadow-sm rounded-xl p-4 border border-slate-100">
    <h2 class="text-lg font-semibold mb-3">输入主题</h2>
    
    <label class="block text-sm text-slate-600 mb-1">主题</label>
    <input v-model="topic"
      class="w-full rounded-lg border border-slate-200 px-3 py-2 mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
      placeholder="例如：全球 AI 监管格局" />

    <label class="block text-sm text-slate-600 mb-2">选择平台（可选，不选则使用默认平台）</label>
    <div class="grid grid-cols-2 gap-2 mb-3">
      <label v-for="platform in availablePlatforms" :key="platform.code"
        class="flex items-center space-x-2 p-2 rounded-lg border border-slate-200 hover:bg-slate-50 cursor-pointer">
        <input type="checkbox" 
          :value="platform.code"
          v-model="selectedPlatforms"
          class="rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
        <span class="text-sm">{{ platform.name }}</span>
      </label>
    </div>

    <button @click="onStart" :disabled="isLoading"
      class="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-lg py-2 font-semibold transition disabled:opacity-60">
      {{ isLoading ? '分析中...' : '开始分析' }}
    </button>

    <div v-if="error" class="mt-3 text-sm text-red-600 bg-red-50 p-2 rounded border border-red-100">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue';
import { useAnalysisStore } from '../stores/analysis';

const store = useAnalysisStore();
const topic = ref('');

// 从 store 加载已保存的平台选择（store 初始化时会从 localStorage 恢复）
const selectedPlatforms = ref(store.selectedPlatforms.length > 0 ? [...store.selectedPlatforms] : []);

const availablePlatforms = computed(() => store.availablePlatforms);
const isLoading = computed(() => store.isLoading);
const error = computed(() => store.error);

// 同步选中的平台到 store（只在用户主动更改时）
watch(selectedPlatforms, (platforms) => {
  store.setSelectedPlatforms(platforms);
}, { deep: true });

// 组件挂载时，确保从 store 同步（防止 store 在其他地方被更新）
onMounted(() => {
  // 确保从 store 同步最新的平台选择
  if (store.selectedPlatforms && store.selectedPlatforms.length > 0) {
    selectedPlatforms.value = [...store.selectedPlatforms];
  } else {
    // 如果 store 中没有，尝试从 localStorage 加载并同步到 store
    const saved = localStorage.getItem('grandchart_selected_platforms');
    if (saved) {
      try {
        const platforms = JSON.parse(saved);
        if (platforms && platforms.length > 0) {
          store.setSelectedPlatforms(platforms);
          selectedPlatforms.value = [...platforms];
        }
      } catch (e) {
        console.error('Failed to load platform selection:', e);
      }
    }
  }
});

const onStart = async () => {
  await store.startAnalysis({ topic: topic.value });
};
</script>
