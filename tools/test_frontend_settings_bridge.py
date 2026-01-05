"""
Test script: verify frontend settings arrive in backend and keys can call vendors.

What it does:
1) Calls backend `GET /api/user-settings` to confirm settings are readable via HTTP.
2) For each configured providerKey (supported), performs a minimal LLM call using backend code
   (reads `cache/user_settings.json` and/or `.env`).

Notes:
- This script does NOT print API keys; only prints last 4 chars for presence checks.
- Running vendor calls will consume quota and requires internet access.
"""

from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Tuple

import httpx


SUPPORTED_PROVIDER_KEYS = ["deepseek", "gemini", "doubao", "kimi", "zhipu", "openai"]


def _mask_key(k: str) -> str:
    k = (k or "").strip()
    if not k:
        return "(empty)"
    return f"...{k[-4:]}" if len(k) >= 4 else "***"


def fetch_user_settings(base_url: str) -> dict:
    url = base_url.rstrip("/") + "/user-settings"
    with httpx.Client(timeout=15.0) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.json()


def collect_provider_keys(user_settings: dict) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for it in (user_settings.get("llm_apis") or []):
        if not isinstance(it, dict):
            continue
        pk = (it.get("providerKey") or "").strip().lower()
        if pk not in SUPPORTED_PROVIDER_KEYS:
            continue
        raw = (it.get("key") or "").strip()
        if not raw:
            continue
        # Mirror backend splitting rules (comma/newline/semicolon).
        normalized = raw.replace("\r\n", "\n").replace("\r", "\n").replace(";", ",").replace("\n", ",")
        keys = [x.strip() for x in normalized.split(",") if x.strip()]
        if not keys:
            continue
        out.setdefault(pk, [])
        out[pk].extend(keys)
    # de-dup preserving order
    for pk, keys in list(out.items()):
        seen = set()
        deduped: List[str] = []
        for k in keys:
            if k in seen:
                continue
            seen.add(k)
            deduped.append(k)
        out[pk] = deduped
    return out


def test_llm_calls(provider_keys: List[str], dry_run: bool) -> List[Tuple[str, bool, str]]:
    """
    Import backend and do a minimal call per provider.
    Returns list of (providerKey, ok, message).
    """
    if dry_run:
        return [(pk, True, "dry-run") for pk in provider_keys]

    # Import backend modules only when needed.
    from langchain_core.messages import HumanMessage
    from app.config import settings
    from app.llm import get_llm

    mapping = {
        "deepseek": ("deepseek", settings.DEEPSEEK_MODEL),
        "gemini": ("gemini", settings.GEMINI_MODEL),
        "doubao": ("doubao", settings.DOUBAO_MODEL),
        "kimi": ("moonshot", settings.MOONSHOT_MODEL),
        "zhipu": ("zhipu", settings.ZHIPU_MODEL),
        "openai": ("openai", settings.OPENAI_MODEL),
    }

    results: List[Tuple[str, bool, str]] = []
    for pk in provider_keys:
        provider, model = mapping[pk]
        try:
            llm = get_llm(provider, model)
            resp = llm.invoke([HumanMessage(content="Reply with exactly: pong")])
            text = getattr(resp, "content", "")
            preview = (str(text) or "").strip().replace("\n", " ")[:80]
            results.append((pk, True, preview or "ok"))
        except Exception as e:
            results.append((pk, False, str(e)[:200]))
    return results


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--backend", default="http://127.0.0.1:8000/api", help="Backend base url, default: %(default)s")
    p.add_argument("--dry-run", action="store_true", help="Do not call vendors; only check HTTP settings")
    args = p.parse_args(argv)

    print(f"[1/3] Fetching user settings from {args.backend!r} ...")
    settings_json = fetch_user_settings(args.backend)

    volc = settings_json.get("volcengine") or {}
    volc_ak = (volc.get("access_key") or "").strip()
    volc_sk = (volc.get("secret_key") or "").strip()

    print("[2/3] Found settings:")
    providers = collect_provider_keys(settings_json)
    if not providers:
        print("  - llm_apis: (none)")
    else:
        for pk, keys in providers.items():
            print(f"  - {pk}: {len(keys)} key(s): " + ", ".join(_mask_key(k) for k in keys[:3]) + (" ..." if len(keys) > 3 else ""))

    print(f"  - jimeng(volcengine) AK: {_mask_key(volc_ak)}  SK: {_mask_key(volc_sk)} (image generation uses jimeng only)")
    overrides = settings_json.get("agent_llm_overrides") or {}
    if overrides:
        print("  - agent_llm_overrides:")
        for k, v in overrides.items():
            print(f"      {k}: {v}")

    to_test = [pk for pk in SUPPORTED_PROVIDER_KEYS if pk in providers]
    if not to_test:
        print("[3/3] No supported providers configured in llm_apis; skip vendor calls.")
        return 0

    print(f"[3/3] Testing vendor calls for: {', '.join(to_test)}")
    results = test_llm_calls(to_test, dry_run=args.dry_run)
    ok = True
    for pk, success, msg in results:
        status = "OK" if success else "FAIL"
        print(f"  - {pk}: {status} :: {msg}")
        ok = ok and success

    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

