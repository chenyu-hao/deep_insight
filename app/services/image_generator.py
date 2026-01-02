import json
import time
import asyncio
import re
from typing import List, Optional, Dict, Any
from volcengine.visual.VisualService import VisualService
from app.config import settings
from app.llm import get_agent_llm
from langchain_core.messages import SystemMessage, HumanMessage

IMAGE_PROMPT_GENERATOR_PROMPT = """
你是一个专业的AI绘画提示词专家，擅长为文生图模型编写高质量的提示词。
你的任务是根据提供的小红书文案内容，生成 **3-4 条彼此不同** 的文生图提示词，每条提示词用于生成 **1 张** 小红书风格图片。

**风格要求**：
- 整体风格：小红书审美风格（精致、高颜值、生活化、氛围感）。
- 画面美学：色彩明亮或有特定氛围感（如：多巴胺色系、奶油风、复古胶片感、极简主义等）。
- 构图：多采用人像、特写、俯拍或具有设计感的构图。

**编写建议**：
- 每条提示词使用连贯的自然语言描述画面内容（主体+行为+环境等）。
- 用短词语描述画面美学（风格、色彩、光影、构图等）。
- 每条提示词应明确为“单张图片”，避免使用“组图/一系列/几张”等会触发多图生成的措辞。
- 提示词中可以包含文字，请用“”引号括起来。
- 提升指令响应：专业词汇尽量使用英文（English），效果更准确。

**输出格式要求（必须严格遵守）**：
只输出一个 JSON 数组（list），数组中是 3-4 个字符串，每个字符串是一条提示词。
不要输出任何解释、序号、Markdown 代码块标记。

示例（仅示意格式）：
["一张小红书风格的图片：...", "一张小红书风格的图片：...", "一张小红书风格的图片：..."]
"""

DEFAULT_REQ_KEY = "jimeng_t2i_v40"
MAX_IMAGES = 4
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 1024
DEFAULT_STEPS = 30
DEFAULT_SCALE = 10.0
DEFAULT_STYLE = "小红书"

class ImageGeneratorService:
    def __init__(self):
        self.visual_service = VisualService()
        if settings.VOLC_ACCESS_KEY and settings.VOLC_SECRET_KEY:
            self.visual_service.set_ak(settings.VOLC_ACCESS_KEY)
            self.visual_service.set_sk(settings.VOLC_SECRET_KEY)
            self.visual_service.set_host("visual.volcengineapi.com")
        
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

    async def generate_image_prompts(self, content: str) -> List[str]:
        """Generate multiple single-image prompts based on the content using LLM."""
        llm = get_agent_llm("writer") # Use writer's LLM or a dedicated one
        messages = [
            SystemMessage(content=IMAGE_PROMPT_GENERATOR_PROMPT),
            HumanMessage(content=f"请根据以下文案生成AI绘画提示词：\n\n{content}")
        ]
        response = await llm.ainvoke(messages)
        # Extract text content (handling potential list/dict response)
        from app.services.workflow import extract_text_content
        raw = extract_text_content(response.content)
        prompts = self._parse_prompts(raw)
        # Hard guard: cap to MAX_IMAGES
        if len(prompts) > MAX_IMAGES:
            prompts = prompts[:MAX_IMAGES]
        return prompts

    async def submit_task(self, prompt: str) -> Optional[str]:
        """Submit a text-to-image task to Volcengine."""
        params = {
            "req_key": DEFAULT_REQ_KEY,
            "prompt": prompt,
            "scale": DEFAULT_SCALE,
            "width": DEFAULT_WIDTH,
            "height": DEFAULT_HEIGHT,
            "style": DEFAULT_STYLE,
            "steps": DEFAULT_STEPS,
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
        params = {
            "req_key": DEFAULT_REQ_KEY,
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

    async def generate_images(self, content: str) -> List[str]:
        """Full workflow: generate N prompts -> submit N tasks -> aggregate results."""
        if not settings.VOLC_ACCESS_KEY or not settings.VOLC_SECRET_KEY:
            print("[IMAGE] Volcengine keys not configured.")
            return []
            
        print(f"[IMAGE] Generating prompts (3-{MAX_IMAGES})...")
        prompts = await self.generate_image_prompts(content)
        if not prompts:
            print("[IMAGE] No prompts generated.")
            return []

        # Guard: if LLM returned fewer than 3, still proceed (avoid blocking)
        if len(prompts) < 3:
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
