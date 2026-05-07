<template>
  <div class="bg-white shadow-sm rounded-xl p-4 border border-slate-100">
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-lg font-semibold">历史输出</h2>
      <button @click="fetchFiles" :disabled="loading"
        class="text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50">
        {{ loading ? '加载中...' : '刷新' }}
      </button>
    </div>

    <div v-if="error" class="mb-3 text-sm text-red-600 bg-red-50 p-2 rounded border border-red-100">
      {{ error }}
    </div>

    <div v-if="files.length > 0" class="space-y-2 max-h-96 overflow-y-auto">
      <div v-for="file in files" :key="file.filename"
        @click="loadFile(file.filename)"
        class="p-3 rounded-lg border border-slate-200 hover:bg-slate-50 cursor-pointer transition">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="font-medium text-sm text-slate-800 mb-1">{{ file.topic }}</div>
            <div class="text-xs text-slate-500">{{ formatDate(file.created_at) }}</div>
          </div>
          <div class="text-xs text-slate-400 ml-2">
            {{ formatSize(file.size) }}
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="loading" class="text-center text-slate-400 py-4">
      加载中...
    </div>

    <div v-else class="text-center text-slate-400 py-4">
      暂无历史文件
    </div>

    <!-- 分页 -->
    <div v-if="total > limit" class="mt-3 flex items-center justify-between text-sm">
      <span class="text-slate-600">共 {{ total }} 条</span>
      <div class="flex items-center space-x-2">
        <button @click="prevPage" :disabled="offset === 0"
          class="px-3 py-1 rounded border border-slate-200 hover:bg-slate-50 disabled:opacity-50">
          上一页
        </button>
        <span class="text-slate-600">{{ Math.floor(offset / limit) + 1 }} / {{ Math.ceil(total / limit) }}</span>
        <button @click="nextPage" :disabled="offset + limit >= total"
          class="px-3 py-1 rounded border border-slate-200 hover:bg-slate-50 disabled:opacity-50">
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useOutputsStore } from '../stores/outputs';

const outputsStore = useOutputsStore();
const limit = ref(20);
const offset = ref(0);

const files = computed(() => outputsStore.files);
const total = computed(() => outputsStore.total);
const loading = computed(() => outputsStore.loading);
const error = computed(() => outputsStore.error);

const fetchFiles = async () => {
  await outputsStore.fetchFiles(limit.value, offset.value);
};

const loadFile = async (filename) => {
  try {
    await outputsStore.fetchFileContent(filename);
    // 可以触发一个事件或使用 emit 来通知父组件显示文件内容
    // 这里先简单 alert
    alert(`已加载文件: ${filename}\n\n可以在控制台查看完整内容，或添加文件查看组件来展示。`);
  } catch (err) {
    alert('加载文件失败: ' + err.message);
  }
};

const prevPage = () => {
  if (offset.value > 0) {
    offset.value = Math.max(0, offset.value - limit.value);
    fetchFiles();
  }
};

const nextPage = () => {
  if (offset.value + limit.value < total.value) {
    offset.value += limit.value;
    fetchFiles();
  }
};

const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN');
};

const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

onMounted(() => {
  fetchFiles();
});
</script>
