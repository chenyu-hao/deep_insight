import { defineStore } from 'pinia';
import { api } from '../api';

export const useWorkflowStore = defineStore('workflow', {
    state: () => ({
        status: {
            running: false,
            current_step: null,
            progress: 0,
            started_at: null,
            topic: null,
        },
        pollingInterval: null,
    }),

    actions: {
        async fetchStatus() {
            try {
                this.status = await api.getWorkflowStatus();
            } catch (err) {
                console.error('Failed to fetch workflow status:', err);
            }
        },

        startPolling(interval = 2000) {
            this.stopPolling();
            this.pollingInterval = setInterval(() => {
                this.fetchStatus();
            }, interval);
        },

        stopPolling() {
            if (this.pollingInterval) {
                clearInterval(this.pollingInterval);
                this.pollingInterval = null;
            }
        },
    },
});