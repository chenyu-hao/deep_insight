<template>
    <div class="min-h-screen p-6">
        <!-- 主工作区 -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
            <div class="col-span-1">
                <NewsInput />
            </div>
            <div class="col-span-1 lg:col-span-1">
                <ThinkingChain />
            </div>
            <div class="col-span-1">
                <XiaohongshuCard />
            </div>
        </div>

        <!-- 管理和状态区 -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div class="col-span-1">
                <WorkflowStatus />
            </div>
            <div class="col-span-1">
                <ConfigPanel />
            </div>
            <div class="col-span-1">
                <OutputFiles />
            </div>
        </div>
    </div>
</template>

<script setup>
import NewsInput from './components/NewsInput.vue';
import ThinkingChain from './components/ThinkingChain.vue';
import XiaohongshuCard from './components/XiaohongshuCard.vue';
import WorkflowStatus from './components/WorkflowStatus.vue';
import ConfigPanel from './components/ConfigPanel.vue';
import OutputFiles from './components/OutputFiles.vue';
</script>
