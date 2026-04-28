"""
MCP 发布验证工具

提供发布前的验证功能:
- validate_publish: 验证发布条件是否满足

Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
"""

import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import httpx
from loguru import logger

from opinion_mcp.services.job_manager import job_manager
from opinion_mcp.utils.url_validator import validate_urls, URLValidationResult


# XHS-MCP 服务配置
XHS_MCP_URL = "http://localhost:18060"
XHS_MCP_TIMEOUT = 5.0  # 秒


@dataclass
class ImageValidationDetail:
    """单个图片的验证详情"""
    url: str
    valid: bool
    status_code: Optional[int] = None
    error: Optional[str] = None


@dataclass
class ValidatePublishResult:
    """
    发布验证结果
    
    Property 5: Validation Result Completeness
    For any call to `validate_publish`, the result SHALL contain:
    - xhs_service_ok (boolean)
    - images_valid (count)
    - images_invalid (count)
    - image_details (list with status for each image)
    - can_publish (boolean)
    """
    xhs_service_ok: bool
    images_valid: int
    images_invalid: int
    image_details: List[Dict[str, Any]]
    can_publish: bool
    suggestions: List[str]
    job_id: Optional[str] = None
    error: Optional[str] = None


async def check_xhs_service() -> tuple[bool, Optional[str]]:
    """
    检查 XHS-MCP 服务是否可用
    
    Returns:
        Tuple[bool, Optional[str]]: (是否可用, 错误信息)
    """
    try:
        async with httpx.AsyncClient(timeout=XHS_MCP_TIMEOUT) as client:
            response = await client.get(f"{XHS_MCP_URL}/mcp")
            
            if response.status_code == 200:
                return True, None
            else:
                return False, f"XHS-MCP 服务返回状态码 {response.status_code}"
                
    except httpx.ConnectError:
        return False, "无法连接到 XHS-MCP 服务 (端口 18060)"
    except httpx.TimeoutException:
        return False, "XHS-MCP 服务响应超时"
    except Exception as e:
        return False, f"检查 XHS-MCP 服务时出错: {str(e)}"


def convert_validation_results(results: List[URLValidationResult]) -> List[Dict[str, Any]]:
    """将 URLValidationResult 转换为字典列表"""
    return [
        {
            "url": r.url,
            "valid": r.valid,
            "status_code": r.status_code,
            "error": r.error,
        }
        for r in results
    ]


async def validate_publish(
    job_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    验证发布条件是否满足
    
    检查内容:
    1. XHS-MCP 服务是否可用
    2. 任务是否存在且已完成
    3. 图片 URL 是否有效
    
    Args:
        job_id: 任务 ID，留空则使用最近完成的任务
        
    Returns:
        Dict 包含验证结果:
        - xhs_service_ok: bool - XHS-MCP 服务是否可用
        - images_valid: int - 有效图片数量
        - images_invalid: int - 无效图片数量
        - image_details: List[Dict] - 每个图片的验证详情
        - can_publish: bool - 是否可以发布
        - suggestions: List[str] - 修复建议
        - job_id: str - 任务 ID
        - error: str - 错误信息（如果有）
    """
    logger.info(f"[validate_publish] 开始验证: job_id={job_id}")
    
    suggestions: List[str] = []
    
    # 1. 检查 XHS-MCP 服务
    xhs_ok, xhs_error = await check_xhs_service()
    if not xhs_ok:
        suggestions.append(f"启动 XHS-MCP 服务: {xhs_error}")
        logger.warning(f"[validate_publish] XHS-MCP 服务不可用: {xhs_error}")
    
    # 2. 获取任务
    if job_id:
        job = job_manager.get_job(job_id)
    else:
        job = job_manager.get_latest_completed_job()
        if job:
            job_id = job.job_id
    
    if not job:
        error_msg = "任务不存在" if job_id else "没有已完成的任务"
        return asdict(ValidatePublishResult(
            xhs_service_ok=xhs_ok,
            images_valid=0,
            images_invalid=0,
            image_details=[],
            can_publish=False,
            suggestions=suggestions + [error_msg],
            job_id=job_id,
            error=error_msg,
        ))
    
    # 3. 检查任务状态
    if job.is_running:
        return asdict(ValidatePublishResult(
            xhs_service_ok=xhs_ok,
            images_valid=0,
            images_invalid=0,
            image_details=[],
            can_publish=False,
            suggestions=suggestions + ["等待任务完成"],
            job_id=job_id,
            error="任务仍在运行中",
        ))
    
    if job.is_failed:
        return asdict(ValidatePublishResult(
            xhs_service_ok=xhs_ok,
            images_valid=0,
            images_invalid=0,
            image_details=[],
            can_publish=False,
            suggestions=suggestions + ["重新运行分析任务"],
            job_id=job_id,
            error=f"任务失败: {job.error_message}",
        ))
    
    # 4. 收集所有图片 URL
    result = job.result
    if not result:
        return asdict(ValidatePublishResult(
            xhs_service_ok=xhs_ok,
            images_valid=0,
            images_invalid=0,
            image_details=[],
            can_publish=False,
            suggestions=suggestions + ["任务没有结果数据"],
            job_id=job_id,
            error="任务没有结果数据",
        ))
    
    image_urls: List[str] = []
    local_files: List[str] = []
    
    # 收集数据卡片图片（可能是 URL 也可能是本地路径）
    if result.cards:
        cards = result.cards
        for card_path in [cards.title_card, cards.debate_timeline, cards.trend_analysis, cards.platform_radar]:
            if card_path:
                if os.path.isfile(card_path):
                    local_files.append(card_path)
                else:
                    image_urls.append(card_path)
    
    # 收集 AI 生成图片
    if result.ai_images:
        image_urls.extend(result.ai_images)
    
    if not image_urls and not local_files:
        return asdict(ValidatePublishResult(
            xhs_service_ok=xhs_ok,
            images_valid=0,
            images_invalid=0,
            image_details=[],
            can_publish=False,
            suggestions=suggestions + ["没有可发布的图片，请先生成 AI 配图或运行 generate_topic_cards"],
            job_id=job_id,
            error="没有图片",
        ))
    
    # 5. 验证远程图片 URL
    image_details: List[Dict[str, Any]] = []
    valid_count = len(local_files)  # 本地文件视为有效
    invalid_count = 0
    
    # 本地文件直接标记为有效
    for lf in local_files:
        image_details.append({"url": lf, "valid": True, "status_code": None, "error": None})
    
    # 远程 URL 需要 HTTP 验证
    if image_urls:
        logger.info(f"[validate_publish] 验证 {len(image_urls)} 个远程图片 URL")
        validation_results = await validate_urls(image_urls, timeout=10.0, concurrency=5)
        
        remote_valid = sum(1 for r in validation_results if r.valid)
        remote_invalid = len(validation_results) - remote_valid
        valid_count += remote_valid
        invalid_count += remote_invalid
        
        image_details.extend(convert_validation_results(validation_results))
        
        if remote_invalid > 0:
            suggestions.append(f"{remote_invalid} 个远程图片 URL 无效，可能需要重新生成")
            for r in validation_results:
                if not r.valid:
                    logger.warning(f"[validate_publish] 无效图片: {r.url} - {r.error}")
    
    # 6. 判断是否可以发布
    can_publish = xhs_ok and valid_count > 0
    
    if not can_publish and valid_count == 0:
        suggestions.append("所有图片都无效，请重新生成图片")
    
    logger.info(f"[validate_publish] 验证完成: xhs_ok={xhs_ok}, valid={valid_count}, invalid={invalid_count}, can_publish={can_publish}")
    
    return asdict(ValidatePublishResult(
        xhs_service_ok=xhs_ok,
        images_valid=valid_count,
        images_invalid=invalid_count,
        image_details=image_details,
        can_publish=can_publish,
        suggestions=suggestions,
        job_id=job_id,
        error=None,
    ))


# ============================================================
# 导出工具函数
# ============================================================

__all__ = [
    "validate_publish",
    "ValidatePublishResult",
]
