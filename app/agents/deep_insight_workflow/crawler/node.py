from app.core.safety import looks_political, safety_cfg, redact_political
from app.services.crawler.crawler_router_service import crawler_router_service
from app.agents.deep_insight_workflow.translator.node import translate_topic_to_english_search_query, contains_cjk, contains_ascii_letters

async def crawler_agent_node(state):
    """Crawler Agent: Crawls multiple platforms for the given topic"""
    print("--- CRAWLER AGENT ---")
    topic = state["topic"]
    platforms = state.get("platforms", [])

    cfg = safety_cfg()
    if cfg["block_political_topics"] and looks_political(topic):
        safe_msg = "安全模式已开启：检测到敏感政治话题，工作流已自动停止生成内容。"
        print(f"[SAFETY] Blocked political topic: {topic!r}")
        return {
            "crawler_data": [],
            "platform_data": {},
            "news_content": "（内容已按安全策略隐藏）",
            "initial_analysis": "（内容已按安全策略隐藏）",
            "final_copy": "TITLE: 内容已隐藏\nCONTENT: 该话题涉及敏感政治内容，已按后台安全策略停止生成。",
            "image_urls": [],
            "messages": [safe_msg],
            "debate_history": [],
            "safety_blocked": True,
            "safety_reason": "politics",
        }
    
    print(f"[CRAWLER] 接收到的平台参数: {platforms} (类型: {type(platforms)})")
    
    if not platforms:
        print("[CRAWLER] 未指定平台，使用所有支持的平台")
        platforms = ["xhs", "dy", "bili", "wb", "zhihu", "tieba", "ks"]
    else:
        print(f"[CRAWLER] 使用用户选择的平台: {platforms}")
    
    valid_platforms = []
    invalid_platforms = []
    for p in platforms:
        normalized = crawler_router_service.normalize_platform(p)
        if normalized in crawler_router_service.supported_platforms:
            valid_platforms.append(normalized)
        else:
            invalid_platforms.append(p)
    if invalid_platforms:
        print(f"[CRAWLER] 这些平台不支持/被过滤: {invalid_platforms}")
    if not valid_platforms:
        print(f"[CRAWLER] 警告: 所有平台都被过滤，使用默认平台")
        valid_platforms = ["xhs", "dy", "bili"]

    foreign_platforms = {"hn", "reddit"}
    needs_foreign_translation = (
        any(p in foreign_platforms for p in valid_platforms)
        and contains_cjk(topic)
        and not contains_ascii_letters(topic)
    )
    foreign_topic = topic
    if needs_foreign_translation:
        translated = await translate_topic_to_english_search_query(topic)
        if translated:
            foreign_topic = translated
            print(f"[CRAWLER] 检测到中文话题，已翻译用于外网平台检索: {foreign_topic}")
        else:
            print("[CRAWLER] 检测到中文话题，但翻译失败，将使用原话题尝试外网检索")
    
    print(f"[CRAWLER] Crawling topic '{topic}' on platforms: {valid_platforms}")
    
    from app.agents.deep_insight_workflow.status import workflow_status
    
    try:
        platform_data = {}
        total_platforms = len(valid_platforms)
        
        for idx, platform in enumerate(valid_platforms):
            platform_name_map = {
                "wb": "微博",
                "bili": "B站",
                "xhs": "小红书",
                "dy": "抖音",
                "ks": "快手",
                "tieba": "贴吧",
                "zhihu": "知乎",
                "hn": "Hacker News",
                "reddit": "Reddit",
            }
            platform_display = platform_name_map.get(platform, platform)
            await workflow_status.update_step("crawler_agent", current_platform=platform_display)
            print(f"[CRAWLER] 正在爬取平台: {platform_display} ({idx+1}/{total_platforms})")
            
            try:
                platform_keywords = foreign_topic if platform in foreign_platforms else topic
                items = await crawler_router_service.crawl_platform(
                    platform=platform,
                    keywords=platform_keywords,
                    max_items=15,
                    timeout=180,
                )
                platform_data[platform] = items
                print(f"[CRAWLER] 平台 {platform_display} 爬取完成，获得 {len(items)} 条数据")
            except Exception as e:
                print(f"[警告] 平台 {platform_display} 爬取出错: {str(e)}")
                platform_data[platform] = []
        
        await workflow_status.update_step("crawler_agent", current_platform=None)
        
        all_data = []
        for platform, items in platform_data.items():
            all_data.extend(items)
        
        seen_ids = set()
        unique_data = []
        for item in all_data:
            content_id = item.get("content_id", "")
            if content_id and content_id not in seen_ids:
                seen_ids.add(content_id)
                unique_data.append(item)
        
        msg = f"爬虫完成：从 {len(platform_data)} 个平台共获取 {len(unique_data)} 条去重数据。"
        if not unique_data:
            msg = f"爬虫完成：话题『{topic}』未获取到数据。"
        
        print(f"[SUCCESS] Crawler completed: {len(unique_data)} items from {len(platform_data)} platforms")
        
        return {
            "crawler_data": unique_data,
            "platform_data": platform_data,
            "messages": [redact_political(msg)]
        }
        
    except Exception as e:
        error_msg = f"Crawler Agent: Error during crawling - {str(e)}"
        print(f"[ERROR] {error_msg}")
        return {
            "crawler_data": [],
            "platform_data": {},
            "messages": [error_msg]
        }
