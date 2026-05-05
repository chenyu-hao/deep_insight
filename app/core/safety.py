import re
from typing import Dict, Any
from app.core.config import settings

_POLITICAL_RE = re.compile(
    r"("
    # CN
    r"习近平|中共|共产党|国安|外交部|国务院|人大|政协|政府|政党|"
    r"总统|总理|首相|国会|参议院|众议院|白宫|克里姆林宫|联合国|北约|"
    r"选举|大选|政变|制裁|战争|袭击|空袭|导弹|军队|入侵|"
    r"台湾|台独|香港|乌克兰|俄罗斯|以色列|巴勒斯坦|哈马斯|"
    r"特朗普|拜登|普京|泽连斯基|内塔尼亚胡|马杜罗|"
    # EN
    r"Trump|Biden|Putin|Zelensky|Maduro|Netanyahu|"
    r"White\s+House|Kremlin|United\s+Nations|UN\b|NATO\b|"
    r"election|president|prime\s+minister|government|parliament|congress|senate|"
    r"sanction|strike|airstrike|missile|troops|invasion|war"
    r")",
    flags=re.IGNORECASE,
)

def safety_cfg() -> Dict[str, Any]:
    cfg = getattr(settings, "WORKFLOW_CONTENT_SAFETY", None) or {}
    return {
        "redact_politics": bool(cfg.get("redact_politics", True)),
        "block_political_topics": bool(cfg.get("block_political_topics", True)),
        "redaction_token": str(cfg.get("redaction_token", "【已脱敏】")),
    }

def looks_political(text: str) -> bool:
    if not text:
        return False
    return bool(_POLITICAL_RE.search(text))

def redact_political(text: str) -> str:
    """Best-effort redaction to remove political signals from text."""
    if not text:
        return text
    cfg = safety_cfg()
    if not cfg["redact_politics"]:
        return text
    token = cfg["redaction_token"]

    matches = list(_POLITICAL_RE.finditer(text))
    if len(matches) >= 6:
        return "（内容涉及敏感政治话题，已按后台安全策略隐藏）"
    return _POLITICAL_RE.sub(token, text)

def with_safety_instruction(base_prompt: str) -> str:
    cfg = safety_cfg()
    if not cfg["redact_politics"]:
        return base_prompt
    return (
        base_prompt
        + "\n\n"
        + "【安全要求】输出中不得出现政治敏感信号（人物/国家机构/战争选举等具体指称）。"
        + "如不可避免，请使用抽象替代（如“某国”“某政府部门”“某领导人”），避免点名与敏感词。"
    )
