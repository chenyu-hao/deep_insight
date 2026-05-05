from langchain_core.messages import SystemMessage, HumanMessage
from app.llm import get_agent_llm
from app.core.safety import with_safety_instruction, redact_political
from app.core.utils import extract_text_content
from app.prompts.workflow.reporter import REPORTER_PROMPT

async def reporter_node(state):
    print("--- REPORTER ---")
    if state.get("safety_blocked"):
        return {
            "news_content": "（内容已按安全策略隐藏）",
            "messages": ["Reporter: （内容已按安全策略隐藏）"],
        }
    topic = state["topic"]
    crawler_data = state.get("crawler_data", [])
    platform_data = state.get("platform_data", {})
    urls = state.get("urls", [])
    llm = get_agent_llm("reporter")
    
    content_text = ""
    if crawler_data:
        items_text = []
        for item in crawler_data[:20]:
            platform = item.get("platform", "unknown")
            title = item.get("title", "")
            content = item.get("content", "")
            author = item.get("author", {}).get("nickname", "Unknown")
            interactions = item.get("interactions", {})
            
            item_text = f"[平台: {platform}] 作者: {author}\n标题: {title}\n内容: {content}\n"
            item_text += f"互动数据: 点赞{interactions.get('liked_count', 0)}, "
            item_text += f"评论{interactions.get('comment_count', 0)}, "
            item_text += f"分享{interactions.get('share_count', 0)}\n"
            items_text.append(item_text)
        
        content_text = "\n---\n".join(items_text)
        platform_summary = ", ".join([f"{p}({len(platform_data.get(p, []))}条)" for p in platform_data.keys()])
        source_info = f"多平台社交媒体数据 ({platform_summary})"
    elif urls:
        content_text = f"URLs provided: {urls}"
        source_info = "Provided URLs"
    else:
        content_text = "No content provided. Please simulate based on topic."
        source_info = "Simulation"

    messages = [
        SystemMessage(content=with_safety_instruction(REPORTER_PROMPT)),
        HumanMessage(
            content=f"主题: {redact_political(topic)}. 来源: {source_info}.\n\n内容:\n{content_text}\n\n请总结核心事实。"
        ),
    ]
    response = await llm.ainvoke(messages)
    content = redact_political(extract_text_content(response.content))
    return {
        "news_content": content,
        "messages": [f"Reporter: {content}"]
    }
