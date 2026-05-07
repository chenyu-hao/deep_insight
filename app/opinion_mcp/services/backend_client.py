"""
后端 API 客户�?

封装�?FastAPI 后端�?HTTP 调用，包括：
- /api/analyze (SSE 流式)
- /api/workflow/status
- /api/hotnews
- /api/xhs/publish
- /api/user-settings
"""

import json
from typing import Any, AsyncGenerator, Dict, List, Optional
from datetime import datetime

import httpx
from loguru import logger

from app.opinion_mcp.config import config


class BackendClient:
    """后端 API 客户�?""
    
    def __init__(self, base_url: Optional[str] = None):
        """初始化客户端
        
        Args:
            base_url: 后端服务地址，默认使用配置中�?BACKEND_URL
        """
        self.base_url = (base_url or config.BACKEND_URL).rstrip("/")
        logger.info(f"[BackendClient] 初始化，后端地址: {self.base_url}")
    
    # ============================================================
    # 2.2 调用 /api/analyze (SSE 流式)
    # ============================================================
    
    async def call_analyze_api(
        self,
        topic: str,
        platforms: Optional[List[str]] = None,
        debate_rounds: int = 2,
        image_count: int = 2,
        urls: Optional[List[str]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """调用后端分析 API (SSE 流式)
        
        Args:
            topic: 要分析的话题
            platforms: 要爬取的平台列表，留空则使用默认平台
            debate_rounds: 辩论轮数 (1-5)
            image_count: AI 配图数量 (0-9)，默�?2 �?
            urls: 额外�?URL 列表
            
        Yields:
            SSE 事件数据，包�?agent_name, step_content, status 等字�?
        """
        url = f"{self.base_url}/api/analyze"
        
        # 构建请求�?
        payload = {
            "topic": topic,
            "platforms": platforms or [],
            "debate_rounds": debate_rounds,
            "image_count": image_count,
            "urls": urls or []
        }
        
        logger.info(f"[BackendClient] 调用分析 API: topic={topic}, platforms={platforms}, debate_rounds={debate_rounds}, image_count={image_count}")
        
        try:
            # 使用无超时的客户端，因为分析可能需要很长时�?
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        logger.error(f"[BackendClient] 分析 API 返回错误: {response.status_code} - {error_text}")
                        yield {
                            "agent_name": "System",
                            "step_content": f"API 错误: {response.status_code}",
                            "status": "error"
                        }
                        return
                    
                    # 解析 SSE �?
                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line:
                            continue
                        
                        # SSE 格式: "data: {...}"
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                logger.debug(f"[BackendClient] SSE 事件: {data.get('agent_name')} - {data.get('status')}")
                                yield data
                            except json.JSONDecodeError as e:
                                logger.warning(f"[BackendClient] SSE JSON 解析失败: {e}, line={line}")
                                continue
                        
        except httpx.ConnectError as e:
            logger.error(f"[BackendClient] 连接后端失败: {e}")
            yield {
                "agent_name": "System",
                "step_content": f"无法连接后端服务: {self.base_url}",
                "status": "error"
            }
        except Exception as e:
            logger.exception(f"[BackendClient] 分析 API 调用异常: {e}")
            yield {
                "agent_name": "System",
                "step_content": f"分析过程出错: {str(e)}",
                "status": "error"
            }
    
    # ============================================================
    # 2.3 调用 /api/workflow/status
    # ============================================================
    
    async def get_workflow_status(self) -> Dict[str, Any]:
        """获取当前工作流状�?
        
        Returns:
            工作流状态信息，包含:
            - running: bool - 是否正在运行
            - current_step: str - 当前步骤
            - topic: str - 当前话题
            - started_at: str - 开始时�?
            - progress: int - 进度百分�?
        """
        url = f"{self.base_url}/api/workflow/status"
        
        try:
            async with httpx.AsyncClient(timeout=config.HOTNEWS_TIMEOUT) as client:
                response = await client.get(url)
                
                if response.status_code != 200:
                    logger.error(f"[BackendClient] 获取工作流状态失�? {response.status_code}")
                    return {
                        "success": False,
                        "running": False,
                        "error": f"API 返回 {response.status_code}"
                    }
                
                data = response.json()
                logger.debug(f"[BackendClient] 工作流状�? running={data.get('running')}, step={data.get('current_step')}")
                return {
                    "success": True,
                    **data
                }
                
        except httpx.ConnectError as e:
            logger.error(f"[BackendClient] 连接后端失败: {e}")
            return {
                "success": False,
                "running": False,
                "error": f"无法连接后端服务: {self.base_url}"
            }
        except Exception as e:
            logger.exception(f"[BackendClient] 获取工作流状态异�? {e}")
            return {
                "success": False,
                "running": False,
                "error": str(e)
            }
    
    # ============================================================
    # 2.4 调用 /api/hotnews
    # ============================================================
    
    async def get_hot_news(
        self,
        limit: int = 20,
        source: str = "hot",
        force_refresh: bool = False,
        include_hn: bool = True
    ) -> Dict[str, Any]:
        """获取热榜数据
        
        Args:
            limit: 返回条数上限 (1-100)
            source: 数据�?("hot"=TopHub 全榜, "all"=所有榜�?
            force_refresh: 是否强制刷新缓存
            include_hn: 是否包含 Hacker News
            
        Returns:
            热榜数据，包�?
            - success: bool
            - items: List[Dict] - 热榜条目
            - total: int - 总条�?
            - from_cache: bool - 是否来自缓存
            - collection_time: str - 采集时间
        """
        url = f"{self.base_url}/api/hotnews"
        params = {
            "limit": min(max(1, limit), config.HOTNEWS_MAX_LIMIT),
            "source": source,
            "force_refresh": str(force_refresh).lower()
        }
        
        logger.info(f"[BackendClient] 获取热榜: limit={limit}, source={source}, force_refresh={force_refresh}")
        
        try:
            async with httpx.AsyncClient(timeout=config.HOTNEWS_TIMEOUT) as client:
                response = await client.get(url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"[BackendClient] 获取热榜失败: {response.status_code}")
                    return {
                        "success": False,
                        "items": [],
                        "total": 0,
                        "error": f"API 返回 {response.status_code}"
                    }
                
                data = response.json()
                
                # 如果需要包�?HN，额外请�?HN 数据
                if include_hn:
                    hn_data = await self._get_hn_news(limit=30)
                    if hn_data.get("success") and hn_data.get("items"):
                        # 合并 HN 数据到结果中
                        hn_items = hn_data.get("items", [])
                        for item in hn_items:
                            item["source"] = "Hacker News"
                            item["platform"] = "hn"
                        data["items"] = data.get("items", []) + hn_items
                        data["total"] = len(data["items"])
                
                logger.info(f"[BackendClient] 热榜获取成功: {data.get('total', 0)} �?)
                return {
                    "success": True,
                    **data
                }
                
        except httpx.ConnectError as e:
            logger.error(f"[BackendClient] 连接后端失败: {e}")
            return {
                "success": False,
                "items": [],
                "total": 0,
                "error": f"无法连接后端服务: {self.base_url}"
            }
        except Exception as e:
            logger.exception(f"[BackendClient] 获取热榜异常: {e}")
            return {
                "success": False,
                "items": [],
                "total": 0,
                "error": str(e)
            }
    
    async def _get_hn_news(self, limit: int = 30, story_type: str = "top") -> Dict[str, Any]:
        """获取 Hacker News 热榜数据（内部方法）
        
        Args:
            limit: 返回条数
            story_type: 故事类型 ("top", "best", "new")
            
        Returns:
            HN 热榜数据
        """
        url = f"{self.base_url}/api/hotnews/hn"
        params = {
            "limit": limit,
            "story_type": story_type
        }
        
        try:
            async with httpx.AsyncClient(timeout=config.HOTNEWS_TIMEOUT) as client:
                response = await client.get(url, params=params)
                
                if response.status_code != 200:
                    return {"success": False, "items": []}
                
                return {"success": True, **response.json()}
                
        except Exception as e:
            logger.warning(f"[BackendClient] 获取 HN 热榜失败: {e}")
            return {"success": False, "items": []}
    
    # ============================================================
    # 2.5 调用 /api/xhs/publish
    # ============================================================
    
    async def publish_xhs(
        self,
        title: str,
        content: str,
        images: List[str],
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """发布内容到小红书
        
        Args:
            title: 标题
            content: 正文内容
            images: 图片列表（本地路径或 HTTP URL�?
            tags: 话题标签列表（不�?前缀�?
            
        Returns:
            发布结果，包�?
            - success: bool
            - message: str
            - data: Optional[Dict] - 发布成功时的额外数据
        """
        url = f"{self.base_url}/api/xhs/publish"
        
        payload = {
            "title": title,
            "content": content,
            "images": images,
            "tags": tags or []
        }
        
        logger.info(f"[BackendClient] 发布到小红书: title={title[:20]}..., images={len(images)}�?)
        
        try:
            async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                data = response.json()
                
                if response.status_code != 200:
                    logger.error(f"[BackendClient] 小红书发布失�? {response.status_code} - {data}")
                    return {
                        "success": False,
                        "message": data.get("message") or f"API 返回 {response.status_code}",
                        "data": None
                    }
                
                logger.info(f"[BackendClient] 小红书发布结�? success={data.get('success')}")
                return data
                
        except httpx.ConnectError as e:
            logger.error(f"[BackendClient] 连接后端失败: {e}")
            return {
                "success": False,
                "message": f"无法连接后端服务: {self.base_url}",
                "data": None
            }
        except Exception as e:
            logger.exception(f"[BackendClient] 小红书发布异�? {e}")
            return {
                "success": False,
                "message": str(e),
                "data": None
            }
    
    # ============================================================
    # 2.6 调用 /api/user-settings
    # ============================================================
    
    async def get_user_settings(self) -> Dict[str, Any]:
        """获取用户设置
        
        Returns:
            用户设置，包�?
            - success: bool
            - llm_apis: List[Dict] - LLM API 配置列表
            - volcengine: Optional[Dict] - 火山引擎配置
            - agent_llm_overrides: Dict - Agent LLM 覆盖配置
        """
        url = f"{self.base_url}/api/user-settings"
        
        try:
            async with httpx.AsyncClient(timeout=config.HOTNEWS_TIMEOUT) as client:
                response = await client.get(url)
                
                if response.status_code != 200:
                    logger.error(f"[BackendClient] 获取用户设置失败: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"API 返回 {response.status_code}"
                    }
                
                data = response.json()
                logger.debug(f"[BackendClient] 用户设置获取成功")
                
                # 转换�?MCP 需要的格式
                return {
                    "success": True,
                    "default_platforms": config.DEFAULT_PLATFORMS,
                    "image_count": config.DEFAULT_IMAGE_COUNT,
                    "debate_rounds": config.DEFAULT_DEBATE_ROUNDS,
                    "available_platforms": config.AVAILABLE_PLATFORMS,
                    "llm_apis": data.get("llm_apis", []),
                    "volcengine": data.get("volcengine"),
                    "agent_llm_overrides": data.get("agent_llm_overrides", {})
                }
                
        except httpx.ConnectError as e:
            logger.error(f"[BackendClient] 连接后端失败: {e}")
            return {
                "success": False,
                "error": f"无法连接后端服务: {self.base_url}"
            }
        except Exception as e:
            logger.exception(f"[BackendClient] 获取用户设置异常: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================================
    # 健康检�?
    # ============================================================
    
    async def health_check(self) -> bool:
        """检查后端服务是否可�?
        
        Returns:
            True 如果后端服务可用，否�?False
        """
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/workflow/status")
                return response.status_code == 200
        except Exception:
            return False


# 导出单例实例
backend_client = BackendClient()
