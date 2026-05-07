<template>
  <div class="bg-white shadow-sm rounded-xl p-4 border border-slate-100">
    <h2 class="text-lg font-semibold mb-3">工作流状态</h2>

    <div v-if="status.running" class="space-y-3">
      <!-- 运行中 -->
      <div class="p-3 bg-blue-50 rounded-lg border border-blue-200">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-blue-800">运行中</span>
          <span class="text-xs text-blue-600">{{ status.current_step }}</span>
        </div>
        
        <div class="mb-2">
          <div class="flex items-center justify-between text-xs text-slate-600 mb-1">
            <span>进度</span>
            <span>{{ status.progress }}%</span>
          </div>
          <div class="w-full bg-slate-200 rounded-full h-2">
            <div class="bg-blue-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: status.progress + '%' }"></div>
          </div>
        </div>

        <div v-if="status.topic" class="text-sm text-slate-700">
          <span class="font-medium">主题：</span>{{ status.topic }}
        </div>
        <div v-if="status.started_at" class="text-xs text-slate-500 mt-1">
          开始时间：{{ formatDate(status.started_at) }}
        </div>
      </div>
    </div>

    <div v-else class="p-3 bg-slate-50 rounded-lg border border-slate-200">
      <div class="text-center text-slate-400 text-sm">
        当前没有运行的工作流
      </div>
    </div>

    <button @click="fetchStatus" :disabled="loading"
      class="mt-3 w-full px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-sm text-slate-700 disabled:opacity-50">
      {{ loading ? '刷新中...' : '刷新状态' }}
    </button>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useWorkflowStore } from '../stores/workflow';

const workflowStore = useWorkflowStore();

const status = computed(() => workflowStore.status);
const loading = ref(false);

const fetchStatus = async () => {
  loading.value = true;
  try {
    await workflowStore.fetchStatus();
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN');
};

onMounted(() => {
  fetchStatus();
  // 自动轮询（每2秒）
  workflowStore.startPolling(2000);
});

onUnmounted(() => {
  workflowStore.stopPolling();
});
</script>
