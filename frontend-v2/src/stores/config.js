import { defineStore } from 'pinia'
import { api } from '../api'

export const useConfigStore = defineStore('config', {
    state: () => ({
        config: null,
        loading: false,
        error: null,
        modelsByProvider: null,
        modelsCacheTime: null,
        darkMode: localStorage.getItem('huntdebate_dark_mode') === 'true',
    }),

    getters: {
        llmProviders: (state) => (state.config && state.config.llm_providers) || {},
        crawlerLimits: (state) => (state.config && state.config.crawler_limits) || {},
        debateMaxRounds: (state) => (state.config && state.config.debate_max_rounds) || 4,
        defaultPlatforms: (state) => (state.config && state.config.default_platforms) || [],
        isDarkMode: (state) => state.darkMode,
        getUserApis: () => {
            const saved = localStorage.getItem('huntdebate_user_apis')
            if (saved) {
                try {
                    return JSON.parse(saved)
                } catch (e) {
                    return []
                }
            }
            return []
        },
        getModelsForProvider: (state) => (providerKey) => {
            if (!state.modelsByProvider) return []
            return state.modelsByProvider[providerKey] || []
        },
        getDefaultModel: (state) => (providerKey) => {
            if (!state.modelsByProvider) return null
            const models = state.modelsByProvider[providerKey] || []
            const defaultModel = models.find(m => m.is_default)
            return defaultModel ? defaultModel.id : (models[0] ? models[0].id : null)
        },
    },

    actions: {
        async fetchConfig() {
            this.loading = true
            this.error = null
            try {
                this.config = await api.getConfig()
            } catch (err) {
                this.error = err.message
                console.error('Failed to fetch config:', err)
            } finally {
                this.loading = false
            }
        },

        async updateConfig(updates) {
            this.loading = true
            this.error = null
            try {
                const result = await api.updateConfig(updates)
                if (this.config) {
                    if (updates.debate_max_rounds !== undefined) {
                        this.config.debate_max_rounds = updates.debate_max_rounds
                    }
                    if (updates.crawler_limits) {
                        Object.assign(this.config.crawler_limits, updates.crawler_limits)
                    }
                    if (updates.default_platforms) {
                        this.config.default_platforms = updates.default_platforms
                    }
                }
                return result
            } catch (err) {
                this.error = err.message
                throw err
            } finally {
                this.loading = false
            }
        },

        saveUserApis(apis) {
            localStorage.setItem('huntdebate_user_apis', JSON.stringify(apis))
        },

        cacheModels(models) {
            this.modelsByProvider = models
            this.modelsCacheTime = Date.now()
            localStorage.setItem('huntdebate_models_cache', JSON.stringify({
                models,
                timestamp: this.modelsCacheTime
            }))
        },

        loadCachedModels() {
            const cached = localStorage.getItem('huntdebate_models_cache')
            if (cached) {
                try {
                    const { models, timestamp } = JSON.parse(cached)
                    const age = Date.now() - timestamp
                    const maxAge = 24 * 60 * 60 * 1000
                    if (age < maxAge) {
                        this.modelsByProvider = models
                        this.modelsCacheTime = timestamp
                        return true
                    }
                } catch (e) {
                    console.error('Failed to load cached models:', e)
                }
            }
            return false
        },

        async fetchModels(forceRefresh = false) {
            if (!forceRefresh && this.loadCachedModels()) {
                return this.modelsByProvider
            }
            try {
                const models = await api.getModels()
                this.cacheModels(models)
                return models
            } catch (err) {
                console.error('Failed to fetch models:', err)
                if (this.modelsByProvider) {
                    return this.modelsByProvider
                }
                throw err
            }
        },

        toggleDarkMode() {
            this.darkMode = !this.darkMode
            localStorage.setItem('huntdebate_dark_mode', this.darkMode.toString())
            this.applyDarkMode()
        },

        setDarkMode(value) {
            this.darkMode = value
            localStorage.setItem('huntdebate_dark_mode', value.toString())
            this.applyDarkMode()
        },

        applyDarkMode() {
            if (this.darkMode) {
                document.documentElement.classList.add('dark')
            } else {
                document.documentElement.classList.remove('dark')
            }
        },

        initDarkMode() {
            this.applyDarkMode()
        },
    },
})
