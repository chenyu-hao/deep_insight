from langchain_core.messages import SystemMessage, HumanMessage
from app.llm import get_agent_llm
from app.core.safety import with_safety_instruction, redact_political
from app.core.utils import extract_text_content
from app.prompts.workflow.analyst import ANALYST_PROMPT

async def analyst_node(state):
    print("--- ANALYST ---")
    if state.get("safety_blocked"):
        content = "（内容已按安全策略隐藏）"
        history = state.get("debate_history", [])
        history.append(f"### Analyst\n{content}\n")
        return {
            "initial_analysis": content,
            "messages": [f"Analyst: {content}"],
            "debate_history": history,
        }
    news_content = state["news_content"]
    critique = state.get("critique")
    llm = get_agent_llm("analyst")
    
    prompt = f"新闻事实: {news_content}"
    if critique:
        prompt += f"\n\n需要解决的反对意见: {critique}"
    
    current_revision_count = state.get("revision_count", 0)
    if critique:
        current_revision_count += 1
        
    messages = [
        SystemMessage(content=with_safety_instruction(ANALYST_PROMPT)),
        HumanMessage(content=redact_political(prompt)),
    ]
    response = await llm.ainvoke(messages)
    content = redact_political(extract_text_content(response.content))
    
    history = state.get("debate_history", [])
    history.append(f"### Analyst (Round {current_revision_count + 1})\n{content}\n")
    
    return {
        "initial_analysis": content,
        "revision_count": current_revision_count,
        "messages": [f"Analyst: {content}"],
        "debate_history": history
    }
