import os
import re
from datetime import datetime
from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from app.llm import get_agent_llm
from app.config import settings
from app.services.crawler import UnifiedCrawler
from app.services.mock_crawler import MockCrawler

# --- Helper Function ---
def extract_text_content(content: Any) -> str:
    """Extract clean text content from LLM response which might be a list of dicts."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                # Extract 'text' field if available, ignoring 'extras'
                if "text" in item:
                    text_parts.append(item["text"])
            elif isinstance(item, str):
                text_parts.append(item)
            else:
                # Fallback for other types, but try to avoid raw dict stringification if possible
                text_parts.append(str(item))
        return "\n".join(text_parts)
    return str(content)

# --- 1. State Definition ---
class GraphState(TypedDict):
    urls: List[str]
    topic: str
    platforms: List[str] # Added platforms
    news_content: Optional[str]
    initial_analysis: Optional[str]
    critique: Optional[str]
    revision_count: int
    final_copy: Optional[str]
    messages: List[str] # Keep for SSE compatibility
    debate_history: List[str] # Track the debate process
    next: str # The next node to execute

# --- 2. LLM Setup ---
# LLMs are now retrieved via get_agent_llm() inside nodes or globally if preferred.

# --- 3. Prompts ---
REPORTER_PROMPT = """
你是一名资深新闻记者。
你的任务是阅读提供的新闻内容（如果缺少内容，请根据主题模拟阅读），并提取核心事实。
重点关注：谁（Who）、什么（What）、何时（When）、何地（Where）、为什么（Why）。
请用**中文**输出事实事件的简明摘要。
"""

ANALYST_PROMPT = """
你是一名舆论分析师。
你的任务是分析提供的新闻事实。
特别关注国内（中国）和国外媒体之间的叙事差异。
识别立场、情绪和任何隐藏的议程。
请一步步思考，并用**中文**输出你的分析。

重要提示：如果你收到反驳意见，请评估其是否与原始新闻主题相关。
如果反驳离题（产生幻觉），请忽略它并坚持原始事实。
"""

DEBATER_PROMPT = """
你是一名魔鬼代言人（反对派）。
你的任务是严格基于提供的**主题**和**新闻事实**来反驳分析师的观点。
1. **语境检查**：确保分析实际上与提供的主题相符。如果分析师在谈论其他内容，请指出来。
2. **脚踏实地**：不要产生新的话题或外部辩论的幻觉（例如，如果主题是“AI”，不要扯到“地平论”）。
3. **反驳**：寻找逻辑谬误、来源中缺失的事实或过度概括。
4. **裁决**：
    * 尽量不要在第一轮就轻易通过。试着找出至少一个可以改进的角度。
    * 只有当分析确实无懈可击且没有明显漏洞时，才回复 "PASS"。
    * 否则，请提供尖锐的**中文**反驳。
"""

WRITER_PROMPT = """
你是小红书的顶级内容创作者。
你的任务是将最终分析转化为一篇病毒式传播的帖子。
要求：
- 大量使用表情符号 🌟✨
- 使用口语化、引人入胜的语气。
- 结构清晰，分段明确。
- 创建一个朗朗上口、标题党式的标题。
- 关注“真相揭秘”或“幕后”角度。
- 请用**中文**撰写。
"""

SUPERVISOR_PROMPT = """
你是一个新闻分析团队的主管。
你的团队成员有：
1. reporter: 负责搜集新闻事实。
2. analyst: 负责分析新闻事实，产出深度观点。
3. debater: 负责反驳分析师的观点，指出漏洞。
4. writer: 负责将最终分析转化为小红书文案。

当前状态：
- 新闻内容 (news_content): {has_news}
- 初步分析 (initial_analysis): {has_analysis}
- 反驳意见 (critique): {has_critique}
- 修改次数 (revision_count): {revision_count} / {max_rounds}
- 最终文案 (final_copy): {has_final_copy}

决策规则：
1. 如果没有新闻内容 (news_content 为 NO)，必须先调用 'reporter'。
2. 如果有新闻内容 (YES) 但没有初步分析 (initial_analysis 为 NO)，调用 'analyst'。
3. 如果有初步分析 (YES) 但没有反驳意见 (critique 为 NO)，调用 'debater'。
4. 如果有反驳意见 (YES)：
    - 如果反驳意见包含 "PASS" (代表分析通过)，调用 'writer'。
    - 如果修改次数 (revision_count) 达到上限 {max_rounds}，调用 'writer'。
    - 否则，调用 'analyst' 进行修改。
5. 如果 writer 已经完成 (final_copy 为 YES)，回复 'FINISH'。

请只输出下一个工人的名字（'reporter', 'analyst', 'debater', 'writer', 'FINISH'），不要输出其他内容。
"""

# --- 4. Node Functions ---

async def supervisor_node(state: GraphState):
    print("--- SUPERVISOR ---")
    llm = get_agent_llm("supervisor")
    
    # Debug state
    news_len = len(state.get("news_content", "") or "")
    print(f"[DEBUG] State Check: news_content length={news_len}")
    
    has_news = f"YES (Length: {len(state.get('news_content', ''))})" if state.get("news_content") else "NO"
    has_analysis = "YES" if state.get("initial_analysis") else "NO"
    has_critique = state.get("critique", "NO")
    if has_critique and len(has_critique) > 50:
        has_critique = "YES (Content exists)"
    elif not has_critique:
        has_critique = "NO"
        
    has_final_copy = "YES" if state.get("final_copy") else "NO"
    
    prompt = SUPERVISOR_PROMPT.format(
        has_news=has_news,
        has_analysis=has_analysis,
        has_critique=has_critique,
        revision_count=state.get("revision_count", 0),
        max_rounds=settings.DEBATE_MAX_ROUNDS,
        has_final_copy=has_final_copy
    )
    
    print(f"[DEBUG] Supervisor Prompt:\n{prompt}") 
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="请决定下一步行动。")
    ]
    
    response = await llm.ainvoke(messages)
    next_step = extract_text_content(response.content).strip().replace("'", "").replace('"', "")
    
    # Fallback safety
    valid_steps = ["reporter", "analyst", "debater", "writer", "FINISH"]
    if next_step not in valid_steps:
        print(f"[WARN] Supervisor returned invalid step: {next_step}. Defaulting based on rules.")
        if not state.get("news_content"):
            next_step = "reporter"
        elif not state.get("initial_analysis"):
            next_step = "analyst"
        elif not state.get("critique"):
            next_step = "debater"
        else:
            next_step = "writer"
            
    # --- GUARD RAILS ---
    # Prevent infinite reporter loop
    if next_step == "reporter" and state.get("news_content"):
        print(f"[WARN] [GUARD] Supervisor chose 'reporter' but news_content exists. Overriding to 'analyst'.")
        next_step = "analyst"
        
    # Prevent infinite analyst loop (if analysis exists but no critique yet)
    if next_step == "analyst" and state.get("initial_analysis") and not state.get("critique"):
        print(f"[WARN] [GUARD] Supervisor chose 'analyst' but initial_analysis exists. Overriding to 'debater'.")
        next_step = "debater"
        
    # Prevent infinite writer loop
    if state.get("final_copy"):
        print(f"[INFO] [GUARD] Final copy exists. Forcing 'FINISH'.")
        next_step = "FINISH"
            
    print(f"[INFO] Supervisor decided: {next_step}")
    return {"next": next_step}

async def reporter_node(state: GraphState):
    print("--- REPORTER ---")
    topic = state["topic"]
    urls = state["urls"]
    platforms = state.get("platforms", ["wb"]) # Default to wb if not present
    llm = get_agent_llm("reporter")
    
    # Crawl content
    if settings.USE_MOCK_CRAWLER:
        print("[WARN] [SYSTEM] MOCK CRAWLER ACTIVE - Using fake data")
        crawler = MockCrawler()
    else:
        print("[INFO] [SYSTEM] REAL CRAWLER ACTIVE - Connecting to platforms")
        crawler = UnifiedCrawler()
        
    try:
        # Combine URLs and Topic for the crawler (which now supports search)
        crawl_inputs = urls.copy()
        if topic:
            crawl_inputs.append(topic)
            
        crawled_content = await crawler.crawl(crawl_inputs, platforms=platforms)
    except Exception as e:
        print(f"Error during crawling: {e}")
        crawled_content = ""

    if not crawled_content:
        return {
            "news_content": "",
            "messages": ["Reporter: No content found."]
        }

    messages = [
        SystemMessage(content=REPORTER_PROMPT),
        HumanMessage(content=f"主题: {topic}. \n\n抓取的内容:\n{crawled_content}\n\n请总结核心事实。")
    ]
    response = await llm.ainvoke(messages)
    content = extract_text_content(response.content)
    return {
        "news_content": content,
        "messages": [f"Reporter: {content}"]
    }

async def analyst_node(state: GraphState):
    print("--- ANALYST ---")
    news_content = state["news_content"]
    critique = state.get("critique")
    llm = get_agent_llm("analyst")
    
    prompt = f"新闻事实: {news_content}"
    if critique:
        prompt += f"\n\n需要解决的反对意见: {critique}"
        
    messages = [
        SystemMessage(content=ANALYST_PROMPT),
        HumanMessage(content=prompt)
    ]
    response = await llm.ainvoke(messages)
    content = extract_text_content(response.content)
    
    # Update history
    history = state.get("debate_history", [])
    history.append(f"### Analyst (Round {state.get('revision_count', 0) + 1})\n{content}\n")
    
    return {
        "initial_analysis": content,
        "critique": None, # Reset critique so Debater runs again if needed
        "revision_count": state.get("revision_count", 0) + 1 if critique else 0,
        "messages": [f"Analyst: {content}"],
        "debate_history": history
    }

async def debater_node(state: GraphState):
    print("--- DEBATER ---")
    analysis = state["initial_analysis"]
    topic = state["topic"]
    news_content = state["news_content"]
    revision_count = state.get("revision_count", 0)
    llm = get_agent_llm("debater")
    
    # Enforce strictness in the first round
    instruction = f"主题: {topic}\n\n新闻事实: {news_content}\n\n分析师观点: {analysis}\n\n请根据事实审查该分析。"
    if revision_count == 0:
        instruction += "\n\n重要提示：这是第一轮审查。你必须找出至少一个改进点或漏洞，**绝对不能**直接回复 PASS。"
    
    messages = [
        SystemMessage(content=DEBATER_PROMPT),
        HumanMessage(content=instruction)
    ]
    response = await llm.ainvoke(messages)
    content = extract_text_content(response.content)
    
    # Update history
    history = state.get("debate_history", [])
    history.append(f"### Debater (Critique)\n{content}\n")
    
    return {
        "critique": content,
        "messages": [f"Debater: {content}"],
        "debate_history": history
    }

async def writer_node(state: GraphState):
    print("--- WRITER ---")
    analysis = state["initial_analysis"]
    topic = state["topic"]
    llm = get_agent_llm("writer")
    
    messages = [
        SystemMessage(content=WRITER_PROMPT),
        HumanMessage(content=f"请将此分析转化为小红书帖子：\n{analysis}")
    ]
    response = await llm.ainvoke(messages)
    content = extract_text_content(response.content)
    
    # Save to Markdown file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Sanitize topic for filename
    safe_topic = re.sub(r'[\\/*?:"<>|]', "", topic)[:20] 
    filename = f"{timestamp}_{safe_topic}.md"
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    
    debate_history = "\n".join(state.get("debate_history", []))
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n")
        f.write("## 最终文案\n\n")
        f.write(content)
        f.write("\n\n---\n\n")
        f.write("## 辩论过程记录\n\n")
        f.write(debate_history)
        
    return {
        "final_copy": content,
        "messages": [f"Writer: {content}\n\nSystem: Document saved to {file_path}"]
    }

# --- 5. Conditional Logic ---
def should_continue(state: GraphState):
    critique = state.get("critique", "")
    revision_count = state.get("revision_count", 0)
    max_rounds = settings.DEBATE_MAX_ROUNDS

    if "PASS" in critique or revision_count >= max_rounds:
        return "writer"
    else:
        return "analyst"

# --- 6. Graph Construction ---

workflow = StateGraph(GraphState)

# workflow.add_node("supervisor", supervisor_node) # Removed Supervisor
workflow.add_node("reporter", reporter_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("debater", debater_node)
workflow.add_node("writer", writer_node)

workflow.set_entry_point("reporter")

workflow.add_edge("reporter", "analyst")
workflow.add_edge("analyst", "debater")

workflow.add_conditional_edges(
    "debater",
    should_continue,
    {
        "writer": "writer",
        "analyst": "analyst"
    }
)

workflow.add_edge("writer", END)

app_graph = workflow.compile()
