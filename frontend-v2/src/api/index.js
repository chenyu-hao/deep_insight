/**
 * API 服务
 * 统一管理所有后端接口调用
 */

const API_BASE_URL = "http://127.0.0.1:8000/api";

let currentAbortController = null;

async function request(url, options = {}) {
    console.log(`[API] Request: ${options.method || 'GET'} ${url}`, options.body ? JSON.parse(options.body) : '');
    
    const response = await fetch(`${API_BASE_URL}${url}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
    });

    if (!response.ok) {
        const error = await response
            .json()
            .catch(() => ({ detail: response.statusText }));
        console.error(`[API] Error response:`, error);
        
        if (Array.isArray(error.detail)) {
            const errorMessages = error.detail.map(err => {
                const loc = err.loc ? err.loc.join(' -> ') : 'unknown';
                return `${loc}: ${err.msg} (type: ${err.type})`;
            }).join('\n');
            console.error('[API] Validation errors:\n', errorMessages);
            throw new Error(`Validation failed:\n${errorMessages}`);
        }
        
        throw new Error(
            error.detail || `HTTP error! status: ${response.status}`
        );
    }

    const data = await response.json();
    console.log(`[API] Response:`, data);
    return data;
}

async function streamRequest(url, options = {}, onMessage) {
    console.log("[API] 开始SSE请求:", url, options);

    currentAbortController = new AbortController();
    const signal = currentAbortController.signal;

    const response = await fetch(`${API_BASE_URL}${url}`, {
        ...options,
        signal,
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
    });

    console.log("[API] SSE响应状态:", response.status, response.ok);

    if (!response.ok || !response.body) {
        const errorText = await response.text().catch(() => "Unknown error");
        console.error("[API] SSE响应错误:", response.status, errorText);
        throw new Error(
            `Network response was not ok: ${response.status} ${errorText}`
        );
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let eventCount = 0;

    console.log("[API] 开始读取SSE流");

    while (true) {
        const { value, done } = await reader.read();
        if (done) {
            console.log("[API] SSE流读取完成，共处理", eventCount, "个事件");
            currentAbortController = null;
            break;
        }

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";

        for (const part of parts) {
            if (!part.trim()) continue;

            if (!part.startsWith("data: ")) {
                console.log("[API] 跳过非data行:", part.substring(0, 50));
                continue;
            }

            const jsonStr = part.replace(/^data: /, "");
            try {
                const data = JSON.parse(jsonStr);
                eventCount++;
                console.log(`[API] 解析SSE事件 #${eventCount}:`, {
                    agent_name: data.agent_name,
                    status: data.status,
                    content_length: (data.step_content || "").length,
                });
                onMessage(data);
            } catch (e) {
                console.warn(
                    "[API] JSON解析错误:",
                    e,
                    "原始数据:",
                    jsonStr.substring(0, 100)
                );
            }
        }
    }
}

export const api = {
    abortAnalysis() {
        if (currentAbortController) {
            console.log("[API] 取消 SSE 请求");
            currentAbortController.abort();
            currentAbortController = null;
            return true;
        }
        console.log("[API] 没有活跃的 SSE 请求可取消");
        return false;
    },

    async analyze(payload, onMessage) {
        return streamRequest(
            "/analyze", {
            method: "POST",
            body: JSON.stringify(payload),
        },
            onMessage
        );
    },

    async getConfig() {
        return request("/config");
    },

    async updateConfig(config) {
        return request("/config", {
            method: "PUT",
            body: JSON.stringify(config),
        });
    },

    async getUserSettings() {
        return request("/user-settings");
    },

    async updateUserSettings(payload) {
        return request("/user-settings", {
            method: "PUT",
            body: JSON.stringify(payload),
        });
    },

    async getOutputFiles(limit = 20, offset = 0) {
        return request(`/outputs?limit=${limit}&offset=${offset}`);
    },

    async getOutputFile(filename) {
        return request(`/outputs/${encodeURIComponent(filename)}`);
    },

    async getHotNews(limit = 10, source = "hot", forceRefresh = false) {
        const params = new URLSearchParams({
            limit: String(limit),
            source,
            force_refresh: String(forceRefresh),
        });
        return request(`/hotnews?${params.toString()}`);
    },

    async getWorkflowStatus() {
        return request("/workflow/status");
    },

    async generateContrastData(payload) {
        return request("/generate-data/contrast", {
            method: "POST",
            body: JSON.stringify(payload),
        });
    },

    async generateSentimentData(payload) {
        return request("/generate-data/sentiment", {
            method: "POST",
            body: JSON.stringify(payload),
        });
    },

    async generateKeywordsData(payload) {
        return request("/generate-data/keywords", {
            method: "POST",
            body: JSON.stringify(payload),
        });
    },

    async getHotNewsTrending(payload = {}) {
        return request("/hot-news/collect", {
            method: "POST",
            body: JSON.stringify({
                platforms: payload.platforms || ["all"],
                force_refresh: payload.force_refresh || false,
            }),
        });
    },

    async getXhsStatus() {
        return request("/xhs/status");
    },

    async publishToXhs(payload) {
        return request("/xhs/publish", {
            method: "POST",
            body: JSON.stringify(payload),
        });
    },

    async getModels() {
        return request("/models");
    },

    async validateModel(payload) {
        return request("/validate-model", {
            method: "POST",
            body: JSON.stringify(payload),
        });
    },
};
