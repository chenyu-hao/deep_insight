import json
import time
import asyncio
import re
from typing import List, Optional, Dict, Any
from app.core.config import settings
from app.llm import get_agent_llm
from app.services.settings.user_settings import get_effective_volcengine_credentials, get_image_generation_count
from app.prompts.image_generator import IMAGE_PROMPT_GENERATOR_PROMPT_TEMPLATE, get_image_prompt_generator_prompt
from langchain_core.messages import SystemMessage, HumanMessage

try:
    # Optional dependency (may not exist in some dev envs)
    from volcengine.visual.VisualService import VisualService  # type: ignore
except Exception:  # pragma: no cover
    VisualService = None  # type: ignore

DEFAULT_REQ_KEY = "jimeng_t2i_v40"
MAX_IMAGES = 2  # 默认生成2张图片
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 1024
DEFAULT_STEPS = 30
DEFAULT_SCALE = 10.0
DEFAULT_STYLE = "小红书"

class ImageGeneratorService:
    def __init__(self):
        if VisualService is None:
            self.visual_service = None
            return
        self.visual_service = VisualService()
        # Host is stable; credentials may be provided via .env or frontend settings.
        self.visual_service.set_host("visual.volcengineapi.com")

    def _effective_cfg(self) -> Dict[str, Any]:
        """Combine defaults (backend-defined) + env/user credentials."""
        creds = get_effective_volcengine_credentials(
            env_access_key=settings.VOLC_ACCESS_KEY,
            env_secret_key=settings.VOLC_SECRET_KEY,
        )
        return {
            "access_key": creds.get("access_key", ""),
            "secret_key": creds.get("secret_key", ""),
            # Other generation parameters are intentionally backend-owned.
            "req_key": DEFAULT_REQ_KEY,
            "style": DEFAULT_STYLE,
            "width": DEFAULT_WIDTH,
            "height": DEFAULT_HEIGHT,
            "steps": DEFAULT_STEPS,
            "scale": DEFAULT_SCALE,
        }

    def _ensure_credentials(self) -> Dict[str, Any]:
        cfg = self._effective_cfg()
        if self.visual_service is None:
            return cfg
        if cfg.get("access_key") and cfg.get("secret_key"):
            ak = cfg["access_key"]
            print(f"[IMAGE] Debug: Using Volcengine AK: {ak[:6]}******{ak[-4:] if len(ak)>10 else ''}")
            self.visual_service.set_ak(ak)
            self.visual_service.set_sk(cfg["secret_key"])
        return cfg
        
    def _parse_prompts(self, raw: str) -> List[str]:
        raw = (raw or "").strip()
        if not raw:
            return []

        # 1) Prefer strict JSON
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                prompts = [str(x).strip() for x in data if str(x).strip()]
                return prompts
            if isinstance(data, dict):
                for key in ("prompts", "prompt_list", "images", "items"):
                    val = data.get(key)
                    if isinstance(val, list):
                        prompts = [str(x).strip() for x in val if str(x).strip()]
                        return prompts
        except Exception:
            pass

        # 2) Fallback: split lines, strip numbering/bullets
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        cleaned: List[str] = []
        for ln in lines:
            ln = re.sub(r"^[-*\u2022]\s+", "", ln)
            ln = re.sub(r"^\d+[.)、:]\s*", "", ln)
            if ln:
                cleaned.append(ln)
        return cleaned

    async def generate_image_prompts(self, content: str, insight: str = "", image_count: Optional[int] = None) -> List[str]:
        """Generate multiple single-image prompts based on the content using LLM."""
        # 优先使用传入的 image_count，否则从用户配置获取
        if image_count is None:
            image_count = get_image_generation_count()
        
        # 如果配置为 0 张，直接返回空列表
        if image_count == 0:
            return []
        
        llm = get_agent_llm("writer") # Use writer's LLM or a dedicated one
        
        user_prompt = f"请根据以下文案生成 {image_count} 条AI绘画提示词：\n\n【文案内容】：\n{content}"
        if insight:
            user_prompt += f"\n\n【核心洞察（Grand Insight）】：\n{insight}\n\n请确保画面元素与此洞察产生共鸣。"

        messages = [
            SystemMessage(content=get_image_prompt_generator_prompt(image_count)),
            HumanMessage(content=user_prompt)
        ]
        response = await llm.ainvoke(messages)
        # Extract text content (handling potential list/dict response)
        from app.core.utils import extract_text_content
        raw = extract_text_content(response.content)
        prompts = self._parse_prompts(raw)
        # Hard guard: cap to configured count
        if len(prompts) > image_count:
            prompts = prompts[:image_count]
        return prompts

    async def submit_task(self, prompt: str) -> Optional[str]:
        """Submit a text-to-image task to Volcengine."""
        if self.visual_service is None:
            print("[IMAGE] volcengine sdk not installed; image generation disabled.")
            return None
        cfg = self._ensure_credentials()
        params = {
            "req_key": cfg["req_key"],
            "prompt": prompt,
            "scale": cfg["scale"],
            "width": cfg["width"],
            "height": cfg["height"],
            "style": cfg["style"],
            "steps": cfg["steps"],
            "seed": -1,
        }
        
        try:
            # Run in thread pool since the SDK is synchronous
            loop = asyncio.get_running_loop()
            resp = await loop.run_in_executor(
                None, 
                lambda: self.visual_service.cv_sync2async_submit_task(params)
            )
            
            if resp.get("code") == 10000:
                return resp.get("data", {}).get("task_id")
            else:
                print(f"[IMAGE] Submit task failed: {resp}")
                return None
        except Exception as e:
            print(f"[IMAGE] Error submitting task: {str(e)}")
            return None

    async def get_result(self, task_id: str) -> List[str]:
        """Poll for the result of a task."""
        if self.visual_service is None:
            return []
        cfg = self._ensure_credentials()
        params = {
            "req_key": cfg["req_key"],
            "task_id": task_id,
            "req_json": json.dumps({"return_url": True})
        }
        
        max_retries = 30
        retry_interval = 2
        
        for i in range(max_retries):
            try:
                loop = asyncio.get_running_loop()
                resp = await loop.run_in_executor(
                    None,
                    lambda: self.visual_service.cv_sync2async_get_result(params)
                )
                
                if resp.get("code") == 10000:
                    data = resp.get("data", {})
                    status = data.get("status")
                    
                    if status == "done":
                        return data.get("image_urls", [])
                    elif status in ["in_queue", "generating"]:
                        print(f"[IMAGE] Task {task_id} is {status}, waiting...")
                        await asyncio.sleep(retry_interval)
                        continue
                    else:
                        print(f"[IMAGE] Task {task_id} failed with status: {status}")
                        return []
                else:
                    print(f"[IMAGE] Get result failed: {resp}")
                    return []
            except Exception as e:
                print(f"[IMAGE] Error getting result: {str(e)}")
                await asyncio.sleep(retry_interval)
        
        print(f"[IMAGE] Task {task_id} timed out.")
        return []

    async def generate_single_image(self, prompt: str) -> Optional[str]:
        """Generate one image for one prompt (one Task ID)."""
        task_id = await self.submit_task(prompt)
        if not task_id:
            return None

        print(f"[IMAGE] Task submitted, ID: {task_id}. Polling...")
        urls = await self.get_result(task_id)
        if not urls:
            return None
        return urls[0]

    async def generate_images(self, content: str, insight: str = "", image_count: Optional[int] = None) -> List[str]:
        """Full workflow: generate N prompts -> submit N tasks -> aggregate results."""
        # 优先使用传入的 image_count，否则从用户配置获取
        if image_count is None:
            image_count = get_image_generation_count()
        
        # 如果配置为 0 张，直接跳过生图
        if image_count == 0:
            print("[IMAGE] Image generation disabled (image_count=0), skipping.")
            return []
        
        if self.visual_service is None:
            print("[IMAGE] volcengine sdk not installed; skip image generation.")
            return []
        cfg = self._effective_cfg()
        if not cfg.get("access_key") or not cfg.get("secret_key"):
            print("[IMAGE] Volcengine keys not configured (env or user-settings).")
            return []
        
        print(f"[IMAGE] Generating prompts (Target: {image_count})...")
        prompts = await self.generate_image_prompts(content, insight=insight, image_count=image_count)
        if not prompts:
            print("[IMAGE] No prompts generated.")
            return []

        # Guard: if LLM returned fewer than expected, still proceed
        if len(prompts) < image_count:
            print(f"[IMAGE] Warning: only {len(prompts)} prompt(s) generated.")

        image_urls: List[str] = []
        for idx, prompt in enumerate(prompts, start=1):
            prompt = (prompt or "").strip().strip('"').strip('“').strip('”')
            if not prompt:
                continue

            print(f"[IMAGE] ({idx}/{len(prompts)}) Prompt: {prompt[:120]}{'...' if len(prompt) > 120 else ''}")
            url = await self.generate_single_image(prompt)
            if url:
                image_urls.append(url)
                print(f"[IMAGE] ({idx}/{len(prompts)}) ✅ Got image URL.")
            else:
                print(f"[IMAGE] ({idx}/{len(prompts)}) ❌ Failed to generate image.")

        print(f"[IMAGE] Generated {len(image_urls)} images (one-task-per-image).")
        return image_urls

image_generator_service = ImageGeneratorService()
