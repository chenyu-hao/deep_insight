from langchain_core.messages import SystemMessage, HumanMessage
from app.llm import get_agent_llm
from app.core.safety import with_safety_instruction, redact_political
from app.core.utils import extract_text_content
from app.core.config import settings
from app.prompts.workflow.debater import DEBATER_PROMPT

async def debater_node(state):
    print("--- DEBATER ---")
    if state.get("safety_blocked"):
        content = "（内容已按安全策略隐藏）"
        history = state.get("debate_history", [])
        history.append(f"### Debater\n{content}\n")
        return {
            "critique": content,
            "messages": [f"Debater: {content}"],
            "debate_history": history,
        }
    analysis = state["initial_analysis"]
    topic = state["topic"]
    news_content = state["news_content"]
    revision_count = state.get("revision_count", 0)
    debate_rounds = state.get("debate_rounds", settings.DEBATE_MAX_ROUNDS)
    llm = get_agent_llm("debater")
    
    prompt_suffix = ""
    if revision_count + 1 < debate_rounds:
        prompt_suffix = f"\n\n当前是第 {revision_count + 1} 轮辩论（目标总轮数: {debate_rounds}）。请尽可能提出尖锐的改进建议，除非分析已经完美到无可挑剔，否则不要回复 PASS。"
    else:
        prompt_suffix = f"\n\n当前是最后一轮辩论。如果分析已经足够好，可以回复 PASS。"

    messages = [
        SystemMessage(content=with_safety_instruction(DEBATER_PROMPT)),
        HumanMessage(
            content=redact_political(
                f"主题: {topic}\n\n新闻事实: {news_content}\n\n分析师观点: {analysis}{prompt_suffix}\n\n请根据事实审查该分析。"
            )
        ),
    ]
    response = await llm.ainvoke(messages)
    content = redact_political(extract_text_content(response.content))
    
    history = state.get("debate_history", [])
    history.append(f"### Debater (Critique Round {revision_count + 1})\n{content}\n")
    
    return {
        "critique": content,
        "messages": [f"Debater: {content}"],
        "debate_history": history
    }
