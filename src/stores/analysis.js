import { defineStore } from "pinia";
import { api } from '../api';
import { useWorkflowStore } from './workflow';

export const useAnalysisStore = defineStore("analysis", {
    state: () => ({
        logs: [],
        finalCopy: { title: "", body: "" },
        isLoading: false,
        error: null,
        selectedPlatforms: [], // 选中的平台
    }),

    getters: {
        availablePlatforms: () => [
            { code: 'wb', name: '微博' },
            { code: 'bili', name: 'B站' },
            { code: 'xhs', name: '小红书' },
            { code: 'dy', name: '抖音' },
            { code: 'ks', name: '快手' },
            { code: 'tieba', name: '贴吧' },
            { code: 'zhihu', name: '知乎' },
        ],
    },

    actions: {
        setSelectedPlatforms(platforms) {
            this.selectedPlatforms = platforms;
        },

        async startAnalysis(payload) {
            this.logs = [];
            this.finalCopy = { title: "", body: "" };
            this.isLoading = true;
            this.error = null;

            // 如果选择了平台，添加到 payload
            const requestPayload = {
                ...payload,
                platforms: this.selectedPlatforms.length > 0 ? this.selectedPlatforms : payload.platforms,
            };

            // 启动工作流状态轮询
            const workflowStore = useWorkflowStore();
            workflowStore.startPolling();

            try {
                await api.analyze(requestPayload, (data) => {
                    this.logs.push(data);

                    // Update final copy if writer finished
                    if (data.agent_name === "Writer" && data.step_content) {
                        this.finalCopy = {
                            title: "生成文案",
                            body: data.step_content,
                        };
                    }

                    // 如果完成或出错，停止轮询
                    if (data.status === 'finished' || data.status === 'error') {
                        workflowStore.stopPolling();
                        workflowStore.fetchStatus(); // 最后更新一次状态
                    }
                });
            } catch (err) {
                console.error("startAnalysis error", err);
                this.error = err.message || "请求失败，请检查后端服务是否启动";
                workflowStore.stopPolling();
            } finally {
                this.isLoading = false;
            }
        },
    },
});