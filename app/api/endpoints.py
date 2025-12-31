from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas import (
    NewsRequest, AgentState, ConfigResponse, ConfigUpdateRequest,
    OutputFileListResponse, OutputFileInfo, OutputFileContentResponse,
    WorkflowStatusResponse, LLMProviderConfig, CrawlerLimit
)
from app.services.workflow import app_graph
from app.services.workflow_status import workflow_status
from app.config import settings
from pathlib import Path
from datetime import datetime

router = APIRouter()

@router.post("/analyze")
async def analyze_news(request: NewsRequest):
    """执行完整的工作流分析（支持平台选择）"""
    print(f"[IN] Received request: Topic='{request.topic}', URLs={request.urls}, Platforms={request.platforms}")
    
    # 更新工作流状态
    await workflow_status.start_workflow(request.topic)
    
    async def event_generator():
        # Initial input for the graph
        initial_state = {
            "urls": request.urls, 
            "topic": request.topic, 
            "platforms": request.platforms or [],  # 支持根据勾选框选择平台
            "messages": [],
            "crawler_data": [],
            "platform_data": {}
        }
        
        # Stream the graph execution
        # LangGraph stream yields (node_name, state_update)
        try:
            async for event in app_graph.astream(initial_state):
                for node_name, state_update in event.items():
                    # 更新工作流状态
                    await workflow_status.update_step(node_name)
                    
                    # Construct AgentState
                    # In a real app, we might extract more specific content from state_update
                    # Here we just take the last message added
                    messages = state_update.get("messages", [])
                    content = str(messages[-1]) if messages else "Processing..."
                    
                    agent_state = AgentState(
                        agent_name=node_name.capitalize(),
                        step_content=content,
                        status="thinking"
                    )
                    
                    # Yield SSE format
                    yield f"data: {agent_state.model_dump_json()}\n\n"
            
            # 完成工作流
            await workflow_status.finish_workflow()
            
            # Final event
            final_state = AgentState(
                agent_name="System",
                step_content="Analysis Complete",
                status="finished"
            )
            yield f"data: {final_state.model_dump_json()}\n\n"
            
        except Exception as e:
            # 重置工作流状态
            await workflow_status.reset()
            
            error_state = AgentState(
                agent_name="System",
                step_content=f"Error: {str(e)}",
                status="error"
            )
            yield f"data: {error_state.model_dump_json()}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """获取当前配置"""
    # 转换 LLM 配置格式
    llm_providers = {
        "reporter": [LLMProviderConfig(**item) for item in settings.AGENT_CONFIG["reporter"]],
        "analyst": [LLMProviderConfig(**item) for item in settings.AGENT_CONFIG["analyst"]],
        "debater": [LLMProviderConfig(**item) for item in settings.AGENT_CONFIG["debater"]],
        "writer": [LLMProviderConfig(**item) for item in settings.AGENT_CONFIG["writer"]],
    }
    
    # 转换爬虫限制格式
    crawler_limits = {
        platform: CrawlerLimit(**limits)
        for platform, limits in settings.CRAWLER_LIMITS.items()
    }
    
    return ConfigResponse(
        llm_providers=llm_providers,
        crawler_limits=crawler_limits,
        debate_max_rounds=settings.DEBATE_MAX_ROUNDS,
        default_platforms=settings.DEFAULT_PLATFORMS
    )


@router.put("/config")
async def update_config(request: ConfigUpdateRequest):
    """更新配置（部分更新）"""
    updated_fields = []
    
    if request.debate_max_rounds is not None:
        if request.debate_max_rounds < 1:
            raise HTTPException(status_code=400, detail="debate_max_rounds 必须大于0")
        settings.DEBATE_MAX_ROUNDS = request.debate_max_rounds
        updated_fields.append("debate_max_rounds")
    
    if request.crawler_limits is not None:
        for platform, limits in request.crawler_limits.items():
            if platform in settings.CRAWLER_LIMITS:
                settings.CRAWLER_LIMITS[platform].update(limits.dict())
                updated_fields.append(f"crawler_limits.{platform}")
    
    if request.default_platforms is not None:
        # 验证平台是否有效
        valid_platforms = ["wb", "dy", "ks", "bili", "tieba", "zhihu", "xhs"]
        invalid = [p for p in request.default_platforms if p not in valid_platforms]
        if invalid:
            raise HTTPException(status_code=400, detail=f"无效的平台: {invalid}")
        settings.DEFAULT_PLATFORMS = request.default_platforms
        updated_fields.append("default_platforms")
    
    if not updated_fields:
        raise HTTPException(status_code=400, detail="没有提供要更新的字段")
    
    return {
        "success": True,
        "message": f"配置已更新: {', '.join(updated_fields)}",
        "updated_fields": updated_fields
    }


@router.get("/outputs", response_model=OutputFileListResponse)
async def get_output_files(limit: int = 20, offset: int = 0):
    """获取历史输出文件列表"""
    output_dir = Path("outputs")
    if not output_dir.exists():
        return OutputFileListResponse(files=[], total=0)
    
    # 获取所有 .md 文件
    md_files = list(output_dir.glob("*.md"))
    
    # 排除 TECH_DOC.md
    md_files = [f for f in md_files if f.name != "TECH_DOC.md"]
    
    # 按修改时间排序（最新的在前）
    md_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    # 分页
    total = len(md_files)
    paginated_files = md_files[offset:offset + limit]
    
    # 构建文件信息
    file_infos = []
    for file_path in paginated_files:
        stat = file_path.stat()
        # 从文件名提取主题和时间
        # 格式: YYYY-MM-DD_HH-MM-SS_主题.md
        parts = file_path.stem.split("_", 2)
        if len(parts) >= 3:
            topic = parts[2]
        else:
            topic = file_path.stem
        
        file_infos.append(OutputFileInfo(
            filename=file_path.name,
            topic=topic,
            created_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            size=stat.st_size
        ))
    
    return OutputFileListResponse(files=file_infos, total=total)


@router.get("/outputs/{filename}", response_model=OutputFileContentResponse)
async def get_output_file(filename: str):
    """获取指定输出文件的内容"""
    # 安全检查：防止路径遍历攻击
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="无效的文件名")
    
    file_path = Path("outputs") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="不是有效的文件")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        stat = file_path.stat()
        created_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        return OutputFileContentResponse(
            filename=filename,
            content=content,
            created_at=created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")


@router.get("/workflow/status", response_model=WorkflowStatusResponse)
async def get_workflow_status():
    """获取当前工作流状态"""
    status = await workflow_status.get_status()
    return WorkflowStatusResponse(**status)
