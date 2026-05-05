import re
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage
from app.llm import get_agent_llm
from app.core.utils import extract_text_content
from app.prompts.workflow.translator import TRANSLATOR_PROMPT

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ASCII_LETTER_RE = re.compile(r"[A-Za-z]")

def contains_cjk(text: str) -> bool:
    return bool(text and _CJK_RE.search(text))

def contains_ascii_letters(text: str) -> bool:
    return bool(text and _ASCII_LETTER_RE.search(text))

async def translate_topic_to_english_search_query(topic: str) -> Optional[str]:
    """Translate a Chinese topic into concise English search keywords."""
    if not topic:
        return None

    translator_llm = None
    try:
        translator_llm = get_agent_llm("translator")
    except Exception:
        translator_llm = None

    if translator_llm is None:
        return None

    try:
        resp = await translator_llm.ainvoke(
            [
                SystemMessage(content=TRANSLATOR_PROMPT),
                HumanMessage(content=topic),
            ]
        )
        english = extract_text_content(getattr(resp, "content", "")).strip()
        english = re.sub(r"\s+", " ", english).strip()
        english = re.sub(r"(?i)^(english|translation)\s*:\s*", "", english).strip()

        if not english:
            return None
        if contains_cjk(english):
            return None
        if not contains_ascii_letters(english):
            return None

        if len(english) > 200:
            english = english[:200].rsplit(" ", 1)[0].strip() or english[:200]
        return english
    except Exception:
        return None
