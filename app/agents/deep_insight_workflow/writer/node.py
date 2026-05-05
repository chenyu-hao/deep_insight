import os
import re
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from app.llm import get_agent_llm
from app.core.safety import with_safety_instruction, redact_political
from app.core.utils import extract_text_content
from app.prompts.workflow.writer import WRITER_PROMPT

async def writer_node(state):
    print("--- WRITER ---")
    if state.get("safety_blocked"):
        content = "TITLE: 内容已隐藏\nCONTENT: 该话题涉及敏感政治内容，已按后台安全策略停止生成。"
        return {
            "final_copy": content,
            "output_file": None,
            "messages": [f"Writer: {content}"],
        }
    analysis = state["initial_analysis"]
    topic = state["topic"]
    news_content = state.get("news_content", "")
    platform_data = state.get("platform_data", {})
    llm = get_agent_llm("writer")

    platform_stats = []
    for p, items in platform_data.items():
        if items:
            platform_stats.append(f"{p}: {len(items)}条")
    platform_stats_str = ", ".join(platform_stats) if platform_stats else "无具体数据"
    
    evidence = news_content
    
    input_text = (
        f"输入：\n"
        f"- 热点话题：{topic}\n"
        f"- 关键信息/证据：{evidence}\n"
        f"- 平台分布/热度对比：{platform_stats_str}\n"
        f"- 时间范围：{datetime.now().strftime('%Y-%m-%d')}\n"
    )
    
    messages = [
        SystemMessage(content=with_safety_instruction(WRITER_PROMPT)),
        HumanMessage(content=redact_political(input_text)),
    ]
    response = await llm.ainvoke(messages)
    content = redact_political(extract_text_content(response.content))
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_topic = re.sub(r'[\\/*?:"<>|]', "", redact_political(topic))[:20]
    filename = f"{timestamp}_{safe_topic}.md"
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    
    debate_history = "\n".join(state.get("debate_history", []))
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# {redact_political(topic)}\n\n")
        f.write("## 最终文案\n\n")
        f.write(content)
        f.write("\n\n---\n\n")
        f.write("## 辩论过程记录\n\n")
        f.write(debate_history)
        
    return {
        "final_copy": content,
        "output_file": file_path,
        "messages": [f"Writer: {content}"]
    }
