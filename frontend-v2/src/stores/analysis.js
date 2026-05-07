import { defineStore } from "pinia"
import { api } from "../api"
import { useWorkflowStore } from "./workflow"

export const useAnalysisStore = defineStore("analysis", {
    state: () => {
        const loadPlatformsFromStorage = () => {
            const saved = localStorage.getItem("huntdebate_selected_platforms")
            if (saved) {
                try {
                    const platforms = JSON.parse(saved)
                    if (Array.isArray(platforms) && platforms.length > 0) {
                        return platforms
                    }
                } catch (e) {
                    console.error("Failed to load platform selection from localStorage:", e)
                }
            }
            return []
        }

        const loadResultsFromSession = () => {
            const saved = sessionStorage.getItem("huntdebate_analysis_results")
            if (saved) {
                try {
                    return JSON.parse(saved)
                } catch (e) {
                    console.error("Failed to load analysis results from sessionStorage:", e)
                }
            }
            return null
        }

        const cachedResults = loadResultsFromSession()

        return {
            logs: cachedResults?.logs || [],
            finalCopy: cachedResults?.finalCopy || { title: "", body: "" },
            isLoading: false,
            error: null,
            selectedPlatforms: loadPlatformsFromStorage(),
            insight: cachedResults?.insight || "",
            insightTitle: cachedResults?.insightTitle || "",
            insightSubtitle: cachedResults?.insightSubtitle || "",
            contrastData: cachedResults?.contrastData || null,
            dataUnlocked: cachedResults?.dataUnlocked || false,
            imageUrls: cachedResults?.imageUrls || [],
            dataViewImages: cachedResults?.dataViewImages || [],
            titleEmoji: cachedResults?.titleEmoji || "🤔",
            titleTheme: cachedResults?.titleTheme || "cool",
            platformStats: cachedResults?.platformStats || null,
            isEditing: false,
            editableContent: {
                title: cachedResults?.finalCopy?.title || "",
                body: cachedResults?.finalCopy?.body || "",
                selectedImageIndices: cachedResults?.selectedImageIndices || [0],
                imageOrder: cachedResults?.imageOrder || [0],
            },
            originalContent: null,
        }
    },

    getters: {
        availablePlatforms: () => [
            { code: "wb", name: "微博" },
            { code: "bili", name: "B站" },
            { code: "xhs", name: "小红书" },
            { code: "dy", name: "抖音" },
            { code: "ks", name: "快手" },
            { code: "tieba", name: "贴吧" },
            { code: "zhihu", name: "知乎" },
            { code: "hn", name: "Hacker News" },
        ],

        insightCardData: (state) => {
            if (state.dataUnlocked) {
                const debateRounds = state.logs.filter(log => log.agent_name === 'Analyst').length
                const critiqueCount = state.logs.filter(log => log.agent_name === 'Debater').length
                const controversy = critiqueCount > 3 ? '高' : critiqueCount > 1 ? '中' : '低'
                const platformCount = state.selectedPlatforms?.length || 0
                return {
                    conclusion: state.insight || '暂无洞察',
                    coverage: { platforms: platformCount, debateRounds, controversy },
                    keyFinding: extractKeyFinding(state.insight)
                }
            }
            return { conclusion: '暂无洞察', coverage: { platforms: 0, debateRounds: 0, controversy: '低' }, keyFinding: '' }
        },

        radarChartData: (state) => {
            const platforms = state.selectedPlatforms || []
            if (platforms.length === 0) {
                return { labels: [], datasets: [{ label: '平台覆盖', data: [], backgroundColor: 'rgba(6, 182, 212, 0.2)', borderColor: 'rgb(6, 182, 212)' }] }
            }
            const realStats = state.platformStats || {}
            const hasRealData = Object.keys(realStats).length > 0
            const maxCount = hasRealData ? Math.max(...Object.values(realStats), 1) : 1
            const platformData = platforms.map(p => {
                const platformName = platformNameMap[p] || p
                if (hasRealData) {
                    const count = realStats[p] || 0
                    const normalized = count > 0 ? 50 + (count / maxCount) * 50 : 50
                    return { name: platformName, value: Math.round(normalized) }
                } else {
                    return { name: platformName, value: 60 }
                }
            })
            return {
                labels: platformData.map(p => p.name),
                datasets: [{
                    label: '平台覆盖', data: platformData.map(p => p.value),
                    backgroundColor: 'rgba(6, 182, 212, 0.15)',
                    borderColor: 'rgb(6, 182, 212)', borderWidth: 2,
                    pointBackgroundColor: 'rgb(6, 182, 212)',
                    pointBorderColor: '#fff', pointBorderWidth: 2, pointRadius: 5,
                }]
            }
        },

        debateTimelineData: (state) => {
            return state.logs
                .filter(log => log.agent_name === 'Analyst')
                .map((log, index) => {
                    const content = log.step_content || ''
                    const titleMatch = content.match(/TITLE:\s*(.+?)(?=\s*(?:SUB:|INSIGHT:|SUMMARY:|$))/is)
                    const summaryMatch = content.match(/SUMMARY:\s*(.+?)(?=\s*(?:TITLE:|INSIGHT:|SUB:|$))/is)
                    const insightMatch = content.match(/INSIGHT:\s*(.+?)(?=\s*(?:TITLE:|SUMMARY:|$))/is)
                    const fullInsight = insightMatch ? insightMatch[1].trim() : ''
                    let summary = ''
                    if (summaryMatch) {
                        summary = summaryMatch[1].trim()
                    } else if (fullInsight) {
                        const firstSentence = fullInsight.match(/^[^。！？.!?]+[。！？.!?]/)
                        if (firstSentence) summary = firstSentence[0]
                        else summary = fullInsight.substring(0, 40)
                    }
                    return {
                        round: index + 1,
                        title: titleMatch ? titleMatch[1].trim() : '推理中...',
                        insight: fullInsight,
                        summary: summary,
                        insightPreview: fullInsight.substring(0, 80) + (fullInsight.length > 80 ? '...' : '')
                    }
                })
        },

        trendChartData: (state) => {
            const analystLogs = state.logs.filter(log => log.agent_name === 'Analyst')
            const debateRounds = analystLogs.length
            if (debateRounds === 0) return { stage: '待分析', growth: 0, curve: [0, 0, 0, 0, 0, 0, 0] }
            const heatKeywords = ['热议', '关注', '讨论', '争议', '热度', '爆发', '火爆', '刷屏']
            const roundHeat = analystLogs.map(log => {
                const content = log.step_content || ''
                let keywordCount = 0
                heatKeywords.forEach(keyword => {
                    const regex = new RegExp(keyword, 'gi')
                    const matches = content.match(regex)
                    if (matches) keywordCount += matches.length
                })
                const lengthScore = Math.min(content.length / 10, 50)
                const keywordScore = keywordCount * 10
                return Math.min(lengthScore + keywordScore, 100)
            })
            let curve = []
            if (debateRounds === 1) {
                const heat = roundHeat[0]
                curve = [heat * 0.3, heat * 0.5, heat * 0.7, heat, heat * 0.95, heat * 0.9, heat * 0.85]
            } else if (debateRounds === 2) {
                const [h1, h2] = roundHeat
                curve = [h1 * 0.5, h1, h1 * 1.1, (h1 + h2) / 2, h2, h2 * 0.95, h2 * 0.9]
            } else {
                curve = Array(7).fill(0).map((_, i) => {
                    const progress = i / 6
                    const index = Math.floor(progress * (debateRounds - 1))
                    const nextIndex = Math.min(index + 1, debateRounds - 1)
                    const localProgress = (progress * (debateRounds - 1)) - index
                    return Math.round(roundHeat[index] * (1 - localProgress) + roundHeat[nextIndex] * localProgress)
                })
            }
            const firstHeat = curve[0]
            const lastHeat = curve[curve.length - 1]
            const avgHeat = curve.reduce((a, b) => a + b, 0) / curve.length
            const growth = Math.round(((lastHeat - firstHeat) / Math.max(firstHeat, 1)) * 100)
            let stage = '扩散期'
            if (growth > 100) stage = '爆发期'
            else if (growth < -20) stage = '回落期'
            else if (avgHeat > 80) stage = '高热期'
            return { stage, growth, curve }
        }
    },

    actions: {
        setSelectedPlatforms(platforms) {
            this.selectedPlatforms = platforms
            if (platforms && platforms.length > 0) {
                localStorage.setItem("huntdebate_selected_platforms", JSON.stringify(platforms))
            } else {
                localStorage.removeItem("huntdebate_selected_platforms")
            }
        },

        saveResultsToSession() {
            const results = {
                logs: this.logs, finalCopy: this.finalCopy,
                insight: this.insight, insightTitle: this.insightTitle,
                insightSubtitle: this.insightSubtitle, contrastData: this.contrastData,
                dataUnlocked: this.dataUnlocked, imageUrls: this.imageUrls,
                dataViewImages: this.dataViewImages, titleEmoji: this.titleEmoji,
                titleTheme: this.titleTheme, platformStats: this.platformStats,
                selectedImageIndices: this.editableContent.selectedImageIndices,
                imageOrder: this.editableContent.imageOrder,
            }
            try {
                sessionStorage.setItem("huntdebate_analysis_results", JSON.stringify(results))
            } catch (e) {
                console.error("Failed to save analysis results to sessionStorage:", e)
            }
        },

        setDataViewImages(images) {
            this.dataViewImages = [...images]
            this.saveResultsToSession()
            if (this.finalCopy.title || this.finalCopy.body) {
                this.initEditableContent()
            }
        },

        startEditing() {
            this.isEditing = true
            this.originalContent = JSON.parse(JSON.stringify(this.editableContent))
        },

        updateEditableContent(field, value) {
            this.editableContent[field] = value
            this.saveEditDraft()
        },

        saveEditing() {
            this.isEditing = false
            this.finalCopy = { title: this.editableContent.title, body: this.editableContent.body }
            this.saveEditDraft()
            this.saveResultsToSession()
        },

        cancelEditing() {
            this.isEditing = false
            if (this.originalContent) {
                this.editableContent = JSON.parse(JSON.stringify(this.originalContent))
            }
        },

        saveEditDraft() {
            try {
                localStorage.setItem('huntdebate_edit_draft', JSON.stringify(this.editableContent))
            } catch (e) {
                console.error('Failed to save edit draft:', e)
            }
        },

        loadEditDraft() {
            try {
                const draft = localStorage.getItem('huntdebate_edit_draft')
                if (draft) {
                    const parsed = JSON.parse(draft)
                    this.editableContent = parsed
                }
            } catch (e) {
                console.error('Failed to load edit draft:', e)
            }
        },

        initEditableContent() {
            const totalImages = 1 + this.dataViewImages.length + this.imageUrls.length
            this.editableContent = {
                title: this.finalCopy.title,
                body: this.finalCopy.body,
                selectedImageIndices: Array.from({ length: totalImages }, (_, i) => i),
                imageOrder: Array.from({ length: totalImages }, (_, i) => i),
            }
            this.saveEditDraft()
        },

        stopAnalysis() {
            console.log('[AnalysisStore] 停止分析')
            const aborted = api.abortAnalysis()
            this.isLoading = false
            const workflowStore = useWorkflowStore()
            workflowStore.stopPolling()
            return aborted
        },

        async startAnalysis(payload) {
            this.logs = []
            this.finalCopy = { title: "", body: "" }
            this.insight = ""
            this.insightTitle = ""
            this.insightSubtitle = ""
            this.contrastData = null
            this.dataUnlocked = false
            this.imageUrls = []
            this.dataViewImages = []
            this.titleEmoji = "🤔"
            this.titleTheme = "cool"
            this.platformStats = null
            this.isLoading = true
            this.error = null
            this.editableContent = { title: "", body: "", selectedImageIndices: [0], imageOrder: [0] }
            this.originalContent = null
            this.isEditing = false

            try {
                localStorage.removeItem('huntdebate_edit_draft')
            } catch (e) { console.error('Failed to clear edit draft:', e) }
            try {
                sessionStorage.removeItem('huntdebate_analysis_results')
            } catch (e) { console.error('Failed to clear session results:', e) }

            const saved = localStorage.getItem("huntdebate_selected_platforms")
            if (saved) {
                try {
                    const platforms = JSON.parse(saved)
                    if (Array.isArray(platforms) && platforms.length > 0) {
                        this.selectedPlatforms = platforms
                    }
                } catch (e) { console.error("Failed to load platform selection:", e) }
            }

            const requestPayload = {
                ...payload,
                platforms: this.selectedPlatforms.length > 0 ? this.selectedPlatforms : payload.platforms || undefined,
            }

            const workflowStore = useWorkflowStore()
            workflowStore.startPolling()

            try {
                await api.analyze(requestPayload, (data) => {
                    this.logs = [...this.logs, data]

                    if (data.agent_name === "Crawler") {
                        if (data.platform_stats) {
                            this.platformStats = data.platform_stats
                            this.saveResultsToSession()
                        }
                    }

                    if (data.agent_name === "Analyst" && data.step_content) {
                        const content = data.step_content
                        if (content.includes("INSIGHT:")) {
                            const parts = content.split("INSIGHT:")
                            if (parts[1]) this.insight = parts[1].split("TITLE:")[0].trim()
                        } else {
                            this.insight = content
                        }
                        if (content.includes("TITLE:")) {
                            const parts = content.split("TITLE:")
                            if (parts[1]) this.insightTitle = parts[1].split("SUB:")[0].trim()
                        }
                        if (content.includes("SUB:")) {
                            const parts = content.split("SUB:")
                            if (parts[1]) this.insightSubtitle = parts[1].trim()
                        }
                        this.saveResultsToSession()
                    }

                    if (data.agent_name === "Writer" && data.step_content) {
                        let cleanContent = data.step_content.replace(/(?:^|\n)Writer:\s*/gi, '').trim()
                        let title = "生成文案"
                        let body = cleanContent

                        if (cleanContent.includes("TITLE:")) {
                            const titleMatch = cleanContent.match(/TITLE:\s*(.+?)(?=\s*(?:EMOJI:|THEME:|CONTENT:|$))/is)
                            if (titleMatch && titleMatch[1]) title = titleMatch[1].trim()

                            const emojiMatch = cleanContent.match(/EMOJI:\s*(.+?)(?=\s*(?:THEME:|CONTENT:|$))/is)
                            if (emojiMatch && emojiMatch[1]) this.titleEmoji = emojiMatch[1].trim()

                            const themeMatch = cleanContent.match(/THEME:\s*(warm|peach|sunset|cool|ocean|mint|sky|lavender|grape|forest|lime|alert|dark|cream)/i)
                            if (themeMatch && themeMatch[1]) this.titleTheme = themeMatch[1].toLowerCase()

                            const contentMatch = cleanContent.match(/CONTENT:\s*([\s\S]+)$/i)
                            if (contentMatch && contentMatch[1]) {
                                body = contentMatch[1].trim()
                            } else {
                                const themeBodyMatch = cleanContent.match(/THEME:\s*(?:warm|peach|sunset|cool|ocean|mint|sky|lavender|grape|forest|lime|alert|dark|cream)\s*([\s\S]+)$/i)
                                if (themeBodyMatch && themeBodyMatch[1]) {
                                    body = themeBodyMatch[1].trim()
                                } else {
                                    body = cleanContent
                                        .replace(/TITLE:\s*.+?(?=\s*(?:EMOJI:|THEME:|CONTENT:|$))/is, '')
                                        .replace(/EMOJI:\s*.+?(?=\s*(?:THEME:|CONTENT:|$))/is, '')
                                        .replace(/THEME:\s*(?:warm|peach|sunset|cool|ocean|mint|sky|lavender|grape|forest|lime|alert|dark|cream)/i, '')
                                        .trim()
                                }
                            }
                        }
                        this.finalCopy = { title, body }
                        this.initEditableContent()
                        this.saveResultsToSession()

                        setTimeout(() => {
                            window.dispatchEvent(new CustomEvent('generate-dataview-cards'))
                        }, 500)
                    }

                    if (data.agent_name === "Image Generator" && data.image_urls) {
                        this.imageUrls = data.image_urls
                        this.initEditableContent()
                        this.saveResultsToSession()
                    }

                    if (data.agent_name === "DataView Generator" && data.dataview_images) {
                        this.dataViewImages = data.dataview_images
                        if (this.finalCopy.title || this.finalCopy.body) {
                            this.initEditableContent()
                        }
                        this.saveResultsToSession()
                    }

                    if (data.status === "finished") {
                        this.dataUnlocked = true
                        this.saveResultsToSession()
                        workflowStore.stopPolling()
                        workflowStore.fetchStatus()
                    }

                    if (data.status === "error") {
                        workflowStore.stopPolling()
                        workflowStore.fetchStatus()
                    }
                })
            } catch (err) {
                console.error("startAnalysis error", err)
                this.error = err.message || "请求失败，请检查后端服务是否启动"
                workflowStore.stopPolling()
            } finally {
                this.isLoading = false
            }
        },
    },
})

function extractKeyFinding(insight) {
    if (!insight) return ''
    const match = insight.match(/背后是(.+?)。|反映了(.+?)。/)
    return match ? (match[1] || match[2]).trim() : ''
}

const platformNameMap = {
    wb: '微博', bili: 'B站', xhs: '小红书', dy: '抖音', ks: '快手',
    tieba: '贴吧', zhihu: '知乎', hn: 'Hacker News', baidu: '百度',
    kuaishou: '快手', weibo: '微博', bilibili: 'B站', douyin: '抖音'
}
