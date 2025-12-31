<template>
  <div class="bg-white shadow-sm rounded-xl p-4 border border-slate-100">
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-lg font-semibold">配置管理</h2>
      <button @click="fetchConfig" :disabled="loading"
        class="text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50">
        {{ loading ? '加载中...' : '刷新' }}
      </button>
    </div>

    <div v-if="error" class="mb-3 text-sm text-red-600 bg-red-50 p-2 rounded border border-red-100">
      {{ error }}
    </div>

    <div v-if="config" class="space-y-4">
      <!-- 辩论轮数 -->
      <div>
        <label class="block text-sm text-slate-600 mb-1">最大辩论轮数</label>
        <div class="flex items-center space-x-2">
          <input v-model.number="localConfig.debate_max_rounds" type="number" min="1" max="10"
            class="flex-1 rounded-lg border border-slate-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <button @click="updateDebateRounds" :disabled="saving"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>

      <!-- 默认平台 -->
      <div>
        <label class="block text-sm text-slate-600 mb-1">默认平台</label>
        <div class="flex flex-wrap gap-2 mb-2">
          <label v-for="platform in availablePlatforms" :key="platform.code"
            class="flex items-center space-x-1 px-2 py-1 rounded border border-slate-200 hover:bg-slate-50 cursor-pointer">
            <input type="checkbox" 
              :value="platform.code"
              v-model="localConfig.default_platforms"
              class="rounded border-slate-300 text-blue-600" />
            <span class="text-sm">{{ platform.name }}</span>
          </label>
        </div>
        <button @click="updateDefaultPlatforms" :disabled="saving"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>

      <!-- 爬虫限制 -->
      <div>
        <label class="block text-sm text-slate-600 mb-2">爬虫限制（每平台）</label>
        <div class="space-y-2 max-h-48 overflow-y-auto">
          <div v-for="platform in availablePlatforms" :key="platform.code"
            class="flex items-center space-x-2 p-2 bg-slate-50 rounded">
            <span class="text-sm font-medium w-16">{{ platform.name }}</span>
            <input v-model.number="localConfig.crawler_limits[platform.code].max_items" 
              type="number" min="1" placeholder="最大数量"
              class="w-20 rounded border border-slate-200 px-2 py-1 text-sm" />
            <span class="text-xs text-slate-500">条</span>
            <input v-model.number="localConfig.crawler_limits[platform.code].max_comments" 
              type="number" min="0" placeholder="评论数"
              class="w-20 rounded border border-slate-200 px-2 py-1 text-sm" />
            <span class="text-xs text-slate-500">评论</span>
          </div>
        </div>
        <button @click="updateCrawlerLimits" :disabled="saving"
          class="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>

    <div v-else-if="loading" class="text-center text-slate-400 py-4">
      加载配置中...
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useConfigStore } from '../stores/config';
import { useAnalysisStore } from '../stores/analysis';

const configStore = useConfigStore();
const analysisStore = useAnalysisStore();

const availablePlatforms = computed(() => analysisStore.availablePlatforms);
const config = computed(() => configStore.config);
const loading = computed(() => configStore.loading);
const error = computed(() => configStore.error);
const saving = ref(false);

const localConfig = ref({
  debate_max_rounds: 4,
  default_platforms: [],
  crawler_limits: {},
});

// 初始化本地配置
const initLocalConfig = () => {
  if (config.value) {
    localConfig.value = {
      debate_max_rounds: config.value.debate_max_rounds,
      default_platforms: [...config.value.default_platforms],
      crawler_limits: JSON.parse(JSON.stringify(config.value.crawler_limits)),
    };
  }
};

watch(config, initLocalConfig, { immediate: true });

const fetchConfig = async () => {
  await configStore.fetchConfig();
};

const updateDebateRounds = async () => {
  saving.value = true;
  try {
    await configStore.updateConfig({
      debate_max_rounds: localConfig.value.debate_max_rounds,
    });
    alert('配置已更新');
  } catch (err) {
    alert('更新失败: ' + err.message);
  } finally {
    saving.value = false;
  }
};

const updateDefaultPlatforms = async () => {
  saving.value = true;
  try {
    await configStore.updateConfig({
      default_platforms: localConfig.value.default_platforms,
    });
    alert('配置已更新');
  } catch (err) {
    alert('更新失败: ' + err.message);
  } finally {
    saving.value = false;
  }
};

const updateCrawlerLimits = async () => {
  saving.value = true;
  try {
    await configStore.updateConfig({
      crawler_limits: localConfig.value.crawler_limits,
    });
    alert('配置已更新');
  } catch (err) {
    alert('更新失败: ' + err.message);
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  fetchConfig();
});
</script>
