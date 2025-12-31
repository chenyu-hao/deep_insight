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
import { computed, ref, watch } from 'vue';
import { useAnalysisStore } from '../stores/analysis';

const store = useAnalysisStore();
const topic = ref('');
const selectedPlatforms = ref([]);

const availablePlatforms = computed(() => store.availablePlatforms);
const isLoading = computed(() => store.isLoading);
const error = computed(() => store.error);

// 同步选中的平台到 store
watch(selectedPlatforms, (platforms) => {
  store.setSelectedPlatforms(platforms);
}, { immediate: true });

const onStart = async () => {
  await store.startAnalysis({ topic: topic.value });
};
</script>
