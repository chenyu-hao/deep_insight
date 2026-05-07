import { defineStore } from 'pinia';
import { api } from '../api';

export const useOutputsStore = defineStore('outputs', {
    state: () => ({
        files: [],
        total: 0,
        loading: false,
        error: null,
        currentFile: null,
    }),

    actions: {
        async fetchFiles(limit = 20, offset = 0) {
            this.loading = true;
            this.error = null;
            try {
                const result = await api.getOutputFiles(limit, offset);
                this.files = result.files;
                this.total = result.total;
            } catch (err) {
                this.error = err.message;
                console.error('Failed to fetch output files:', err);
            } finally {
                this.loading = false;
            }
        },

        async fetchFileContent(filename) {
            this.loading = true;
            this.error = null;
            try {
                this.currentFile = await api.getOutputFile(filename);
            } catch (err) {
                this.error = err.message;
                console.error('Failed to fetch file content:', err);
                throw err;
            } finally {
                this.loading = false;
            }
        },

        clearCurrentFile() {
            this.currentFile = null;
        },
    },
});