"""
卡片渲染服务客户�?

调用独立�?Node.js 渲染服务 (frontend/renderer/) 生成数据卡片 PNG 图片�?
渲染服务默认运行�?http://localhost:3001�?

使用方式:
    from app.opinion_mcp.services.card_render_client import card_render_client

    # 渲染单张卡片
    result = await card_render_client.render_card("title", {...})

    # 批量渲染整个分析结果
    paths = await card_render_client.render_all_cards(analysis_result)
"""

import base64
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger


# 渲染服务地址
RENDERER_URL = os.getenv("CARD_RENDERER_URL", "http://localhost:3001")
RENDER_TIMEOUT = int(os.getenv("CARD_RENDER_TIMEOUT", "30"))

# 输出目录
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "outputs" / "cards"


class CardRenderClient:
    """卡片渲染服务 HTTP 客户�?""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or RENDERER_URL).rstrip("/")
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[CardRender] 初始化，渲染服务: {self.base_url}")

    async def health_check(self) -> bool:
        """检查渲染服务是否可�?""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/healthz")
                return resp.status_code == 200
        except Exception:
            return False

    async def list_types(self) -> List[str]:
        """列出可用的卡片类�?""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/types")
                if resp.status_code == 200:
                    return resp.json().get("types", [])
        except Exception as e:
            logger.warning(f"[CardRender] 无法获取卡片类型: {e}")
        return []

    async def render_card(
        self,
        card_type: str,
        payload: Dict[str, Any],
        filename: Optional[str] = None,
    ) -> Optional[str]:
        """
        渲染单张卡片并保存到本地

        Args:
            card_type: 卡片类型 (title / insight / debate_timeline / trend / radar / key_findings / platform_heat)
            payload: 渲染数据
            filename: 输出文件�?(不含路径)，默�?{card_type}.png

        Returns:
            本地文件路径 (str)，失败返�?None
        """
        url = f"{self.base_url}/render/{card_type}"
        try:
            async with httpx.AsyncClient(timeout=RENDER_TIMEOUT) as client:
                resp = await client.post(url, json=payload)

                if resp.status_code != 200:
                    logger.error(f"[CardRender] 渲染 {card_type} 失败: {resp.status_code} {resp.text}")
                    return None

                data = resp.json()
                if not data.get("success"):
                    logger.error(f"[CardRender] 渲染 {card_type} 返回错误: {data.get('error')}")
                    return None

                # 解析 data URL �?�?PNG 文件
                image_data_url: str = data["image_data_url"]
                # data:image/png;base64,xxxxxx
                b64 = image_data_url.split(",", 1)[1] if "," in image_data_url else image_data_url
                png_bytes = base64.b64decode(b64)

                out_name = filename or f"{card_type}.png"
                out_path = self.output_dir / out_name
                out_path.write_bytes(png_bytes)
                logger.info(f"[CardRender] �?{card_type} �?{out_path} ({len(png_bytes)} bytes)")
                return str(out_path)

        except httpx.ConnectError:
            logger.error(f"[CardRender] 无法连接渲染服务 {self.base_url}，请确认 renderer 已启�?)
            return None
        except Exception as e:
            logger.exception(f"[CardRender] 渲染 {card_type} 异常: {e}")
            return None

    async def render_all_cards(
        self,
        analysis_result: Dict[str, Any],
        topic: str = "",
        job_id: str = "",
    ) -> Dict[str, Optional[str]]:
        """
        根据分析结果批量渲染所有卡�?

        Args:
            analysis_result: 完整的分析结�?dict (来自 workflow)
            topic: 话题�?
            job_id: 任务 ID (用于文件名前缀)

        Returns:
            { card_type: local_path_or_none }
        """
        prefix = f"{job_id}_" if job_id else ""
        results: Dict[str, Optional[str]] = {}

        # 1. Title card
        title_payload = {
            "topic": topic or analysis_result.get("topic", "舆情分析"),
            "subtitle": analysis_result.get("subtitle", ""),
            "theme": analysis_result.get("theme", "tech"),
        }
        results["title"] = await self.render_card("title", title_payload, f"{prefix}title.png")

        # 2. Insight card
        insight = analysis_result.get("insight") or {}
        if insight:
            results["insight"] = await self.render_card("insight", insight, f"{prefix}insight.png")

        # 3. Debate timeline
        debate = analysis_result.get("debate_timeline") or analysis_result.get("debate") or {}
        if debate:
            results["debate_timeline"] = await self.render_card("debate_timeline", debate, f"{prefix}debate_timeline.png")

        # 4. Trend chart
        trend = analysis_result.get("trend") or {}
        if trend:
            results["trend"] = await self.render_card("trend", trend, f"{prefix}trend.png")

        # 5. Radar
        radar = analysis_result.get("radar") or analysis_result.get("platform_radar") or {}
        if radar:
            results["radar"] = await self.render_card("radar", radar, f"{prefix}radar.png")

        # 6. Key findings
        findings = analysis_result.get("key_findings") or {}
        if findings:
            results["key_findings"] = await self.render_card("key_findings", findings, f"{prefix}key_findings.png")

        # 7. Platform heat
        heat = analysis_result.get("platform_heat") or {}
        if heat:
            results["platform_heat"] = await self.render_card("platform_heat", heat, f"{prefix}platform_heat.png")

        rendered = {k: v for k, v in results.items() if v}
        logger.info(f"[CardRender] 批量渲染完成: {len(rendered)}/{len(results)} 张卡�?)
        return results


# 单例
card_render_client = CardRenderClient()
