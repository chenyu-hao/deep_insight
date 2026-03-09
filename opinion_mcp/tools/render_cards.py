"""
MCP 卡片渲染工具

提供 generate_topic_cards 工具供 OpenClaw 调用:
- 根据已完成的分析结果，调用独立渲染服务生成数据卡片 PNG
- 返回本地文件路径列表，供后续发布流程使用
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from opinion_mcp.services.card_render_client import card_render_client
from opinion_mcp.services.job_manager import job_manager
from opinion_mcp.schemas import JobStatus


async def generate_topic_cards(
    job_id: Optional[str] = None,
    card_types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    为指定分析任务生成数据卡片图片

    Args:
        job_id: 分析任务 ID，留空则使用最近完成的任务
        card_types: 指定要生成的卡片类型，留空则生成所有可用卡片
                    可选: title, insight, debate_timeline, trend, radar, key_findings, platform_heat

    Returns:
        包含生成结果的字典:
        - success: bool
        - cards: { type: file_path }
        - message: str
    """
    # 1. 检查渲染服务
    is_healthy = await card_render_client.health_check()
    if not is_healthy:
        return {
            "success": False,
            "cards": {},
            "message": "❌ 渲染服务未启动。请先在 renderer/ 目录执行: npm run build && npm start",
        }

    # 2. 获取分析结果
    if job_id:
        job = job_manager.get_job(job_id)
    else:
        job = job_manager.get_latest_completed_job()
        if job:
            job_id = job.job_id

    if not job:
        return {
            "success": False,
            "cards": {},
            "message": "❌ 未找到已完成的分析任务" + (f" (job_id={job_id})" if job_id else ""),
        }

    if job.status != JobStatus.COMPLETED:
        return {
            "success": False,
            "cards": {},
            "message": f"❌ 任务 {job_id} 尚未完成 (当前状态: {job.status})",
        }

    result = job.result
    if not result:
        return {
            "success": False,
            "cards": {},
            "message": f"❌ 任务 {job_id} 没有可用的分析结果",
        }

    # 3. 从 AnalysisResult 合成各卡片的 payload
    #    AnalysisResult 实际字段: summary(str), insight(str), title(str),
    #    subtitle(str), copywriting, cards(旧URL), ai_images, platform_stats(dict),
    #    platforms_analyzed(list)
    topic = getattr(result, "title", "") or (job.topic if hasattr(job, "topic") else "舆情分析")

    card_payloads: Dict[str, Dict[str, Any]] = {}

    # title 卡 — 固定可渲染
    card_payloads["title"] = {
        "topic": topic,
        "subtitle": getattr(result, "subtitle", ""),
        "theme": "cool",
    }

    # insight 卡 — 需要 insight 文本
    insight_text = getattr(result, "insight", "") or getattr(result, "summary", "")
    if insight_text:
        stats = getattr(result, "platform_stats", {}) or {}
        card_payloads["insight"] = {
            "conclusion": insight_text,
            "coverage": {
                "platforms": len(getattr(result, "platforms_analyzed", []) or []),
                "debateRounds": getattr(job, "debate_rounds", 2),
                "growth": sum(stats.values()) if stats else 0,
                "controversy": "中",
            },
        }

    # platform_heat 卡 — 需要 platform_stats
    pstats = getattr(result, "platform_stats", {}) or {}
    if pstats:
        total = sum(pstats.values()) or 1
        platforms_list = [
            {"name": k, "value": v, "percentage": round(v / total * 100, 1)}
            for k, v in sorted(pstats.items(), key=lambda x: x[1], reverse=True)
        ]
        card_payloads["platform_heat"] = {"platforms": platforms_list}

    # radar 卡 — 从 platform_stats 派生
    if pstats:
        max_val = max(pstats.values()) or 1
        axes = [
            {"label": k, "value": round(v / max_val * 100)}
            for k, v in list(pstats.items())[:6]
        ]
        card_payloads["radar"] = {"axes": axes, "legend": [topic]}

    # key_findings 卡 — 从 summary/insight 文本拆句
    summary_text = getattr(result, "summary", "")
    if summary_text:
        import re
        sentences = [s.strip() for s in re.split(r'[。！？\n]', summary_text) if len(s.strip()) > 4]
        if sentences:
            card_payloads["key_findings"] = {
                "findings": [{"text": s} for s in sentences[:5]],
            }

    # debate_timeline / trend — 这些需要结构化数据，AnalysisResult 中没有原生字段
    # 如果 result 碰巧是 dict 并且含有对应键，则尝试取出
    if isinstance(result, dict):
        for key in ("debate_timeline", "debate", "trend"):
            val = result.get(key)
            if isinstance(val, dict) and val:
                target = "debate_timeline" if key in ("debate_timeline", "debate") else key
                card_payloads[target] = val

    # 4. 渲染
    prefix = f"{job_id}_" if job_id else ""

    if card_types:
        # 选择性渲染 — 仅渲染指定且有 payload 的类型
        to_render = {ct: card_payloads.get(ct) for ct in card_types}
    else:
        to_render = card_payloads

    rendered: Dict[str, Optional[str]] = {}
    for ct, payload in to_render.items():
        if not payload:
            logger.warning(f"[generate_topic_cards] 跳过 {ct}: 当前分析结果中无对应数据")
            continue
        path = await card_render_client.render_card(ct, payload, f"{prefix}{ct}.png")
        rendered[ct] = path

    success_cards = {k: v for k, v in rendered.items() if v}
    failed_cards = [k for k, v in rendered.items() if not v]

    # 5. 回写到 job.result.cards，使 publish/validate 能消费本地 PNG
    if success_cards and job.result is not None:
        from opinion_mcp.schemas import AnalysisCards
        if job.result.cards is None:
            job.result.cards = AnalysisCards()
        cards_obj = job.result.cards
        # 映射: renderer card type → AnalysisCards field
        field_map = {
            "title": "title_card",
            "debate_timeline": "debate_timeline",
            "trend": "trend_analysis",
            "radar": "platform_radar",
        }
        for ct, path in success_cards.items():
            field = field_map.get(ct)
            if field:
                setattr(cards_obj, field, path)

    msg_parts = [f"✅ 成功生成 {len(success_cards)} 张卡片"]
    if failed_cards:
        msg_parts.append(f"⚠️ {len(failed_cards)} 张失败: {', '.join(failed_cards)}")

    return {
        "success": len(success_cards) > 0,
        "cards": success_cards,
        "failed": failed_cards,
        "message": "；".join(msg_parts),
    }
