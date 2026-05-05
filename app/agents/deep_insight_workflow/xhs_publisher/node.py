from app.core.config import settings
from app.services.social.xiaohongshu_publisher import xiaohongshu_publisher

async def xiaohongshu_publisher_node(state):
    print("--- XHS PUBLISHER ---")
    
    auto_publish = settings.XHS_MCP_CONFIG.get("auto_publish", False)
    state_enabled = state.get("xhs_publish_enabled", False)
    
    if not (auto_publish or state_enabled):
        print("[XHS] Auto-publish disabled, skipping.")
        return {
            "xhs_publish_result": None,
            "messages": ["XHS Publisher: Skipped (auto-publish disabled)."]
        }

    if state.get("safety_blocked"):
        return {
            "xhs_publish_result": None,
            "messages": ["XHS Publisher: Skipped (safety blocked)."]
        }
        
    final_copy = state.get("final_copy", "")
    image_urls = state.get("image_urls", [])
    
    if not final_copy or not image_urls:
        print("[XHS] Missing content or images, skipping.")
        return {
            "xhs_publish_result": {"success": False, "error": "Missing content or images"},
            "messages": ["XHS Publisher: Skipped (missing content/images)."]
        }
        
    title = ""
    content = ""
    
    lines = final_copy.split('\n')
    is_content = False
    content_lines = []
    
    for line in lines:
        if line.strip().startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
        elif line.strip().startswith("CONTENT:"):
            content_lines.append(line.replace("CONTENT:", "").strip())
            is_content = True
        elif is_content:
            content_lines.append(line)
            
    content = "\n".join(content_lines).strip()
    
    if not title:
        title = state["topic"]
    if not content:
        content = final_copy
        
    print(f"[XHS] Publishing: {title} with {len(image_urls)} images")
    
    status = await xiaohongshu_publisher.get_status()
    if not status["mcp_available"] or not status["login_status"]:
        msg = f"XHS Publisher: Failed - {status['message']}"
        print(f"[XHS] {msg}")
        return {
            "xhs_publish_result": {"success": False, "error": status['message']},
            "messages": [msg]
        }

    result = await xiaohongshu_publisher.publish_content(
        title=title,
        content=content,
        images=image_urls
    )
    
    msg = f"XHS Publisher: {result.get('message', 'Unknown status')}"
    if result.get("success"):
        print("[XHS] Publish success!")
    else:
        print(f"[XHS] Publish failed: {result.get('error')}")
        
    return {
        "xhs_publish_result": result,
        "messages": [msg]
    }
