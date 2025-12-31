/**
 * API 服务
 * 统一管理所有后端接口调用
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api';

/**
 * 通用请求函数
 */
async function request(url, options = {}) {
    const response = await fetch(`${API_BASE_URL}${url}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
}

/**
 * 流式请求（SSE）
 */
async function streamRequest(url, options = {}, onMessage) {
    const response = await fetch(`${API_BASE_URL}${url}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    });

    if (!response.ok || !response.body) {
        throw new Error('Network response was not ok');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';

        for (const part of parts) {
            if (!part.startsWith('data: ')) continue;
            const jsonStr = part.replace(/^data: /, '');
            try {
                const data = JSON.parse(jsonStr);
                onMessage(data);
            } catch (e) {
                console.warn('Parse error', e, part);
            }
        }
    }
}

export const api = {
    /**
     * 执行完整工作流分析
     * @param {Object} payload - { topic, urls?, platforms? }
     * @param {Function} onMessage - SSE 消息回调
     */
    async analyze(payload, onMessage) {
        return streamRequest('/analyze', {
            method: 'POST',
            body: JSON.stringify(payload),
        }, onMessage);
    },

    /**
     * 获取配置
     */
    async getConfig() {
        return request('/config');
    },

    /**
     * 更新配置
     * @param {Object} config - 部分配置更新
     */
    async updateConfig(config) {
        return request('/config', {
            method: 'PUT',
            body: JSON.stringify(config),
        });
    },

    /**
     * 获取历史输出文件列表
     * @param {number} limit - 数量限制
     * @param {number} offset - 偏移量
     */
    async getOutputFiles(limit = 20, offset = 0) {
        return request(`/outputs?limit=${limit}&offset=${offset}`);
    },

    /**
     * 获取指定输出文件内容
     * @param {string} filename - 文件名
     */
    async getOutputFile(filename) {
        return request(`/outputs/${encodeURIComponent(filename)}`);
    },

    /**
     * 获取工作流状态
     */
    async getWorkflowStatus() {
        return request('/workflow/status');
    },
};