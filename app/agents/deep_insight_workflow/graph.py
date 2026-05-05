from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from app.core.config import settings

# Import Agent Nodes
from app.agents.deep_insight_workflow.crawler.node import crawler_agent_node
from app.agents.deep_insight_workflow.reporter.node import reporter_node
from app.agents.deep_insight_workflow.analyst.node import analyst_node
from app.agents.deep_insight_workflow.debater.node import debater_node
from app.agents.deep_insight_workflow.writer.node import writer_node
from app.agents.deep_insight_workflow.image_generator.node import image_generator_node
from app.agents.deep_insight_workflow.xhs_publisher.node import xiaohongshu_publisher_node

# --- 1. State Definition ---
class GraphState(TypedDict):
    urls: List[str]
    topic: str
    platforms: List[str]
    debate_rounds: int
    image_count: int
    crawler_data: List[Dict[str, Any]]
    platform_data: Dict[str, List[Dict[str, Any]]]
    news_content: str
    initial_analysis: str
    critique: Optional[str]
    revision_count: int
    final_copy: str
    image_urls: List[str]
    dataview_images: List[str]
    output_file: Optional[str]
    messages: List[str]
    debate_history: List[str]
    safety_blocked: bool
    safety_reason: Optional[str]
    xhs_publish_enabled: bool
    xhs_publish_result: Optional[Dict[str, Any]]

# --- 2. Conditional Logic ---
def should_continue(state: GraphState):
    critique = state.get("critique", "")
    revision_count = state.get("revision_count", 0)
    debate_rounds = state.get("debate_rounds", settings.DEBATE_MAX_ROUNDS)
    
    if isinstance(critique, list):
        critique = str(critique)
    elif critique is None:
        critique = ""
    
    max_rounds = min(debate_rounds, settings.DEBATE_MAX_ROUNDS)
    
    is_pass = "PASS" in critique.upper()
    if is_pass and len(critique.strip()) > 100:
        if not (critique.strip().upper().startswith("PASS") or critique.strip().upper().endswith("PASS")):
            is_pass = False

    if is_pass or revision_count >= max_rounds:
        return "writer"
    
    return "analyst"

# --- 3. Graph Construction ---
workflow = StateGraph(GraphState)

workflow.add_node("crawler_agent", crawler_agent_node)
workflow.add_node("reporter", reporter_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("debater", debater_node)
workflow.add_node("writer", writer_node)
workflow.add_node("image_generator", image_generator_node)
workflow.add_node("xhs_publisher", xiaohongshu_publisher_node)

workflow.set_entry_point("crawler_agent")

workflow.add_edge("crawler_agent", "reporter")
workflow.add_edge("reporter", "analyst")
workflow.add_edge("analyst", "debater")

workflow.add_conditional_edges(
    "debater",
    should_continue,
    {
        "analyst": "analyst",
        "writer": "writer"
    }
)

workflow.add_edge("writer", "image_generator")
workflow.add_edge("image_generator", "xhs_publisher")
workflow.add_edge("xhs_publisher", END)

app_graph = workflow.compile()
