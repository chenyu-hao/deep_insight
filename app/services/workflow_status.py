"""
工作流状态管理器
用于跟踪当前运行的工作流状态
"""
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio

class WorkflowStatusManager:
    """管理工作流状态"""
    
    def __init__(self):
        self._status: Dict[str, Any] = {
            "running": False,
            "current_step": None,
            "progress": 0,
            "started_at": None,
            "topic": None,
        }
        self._lock = asyncio.Lock()
    
    async def start_workflow(self, topic: str):
        """开始工作流"""
        async with self._lock:
            self._status = {
                "running": True,
                "current_step": "crawler_agent",
                "progress": 0,
                "started_at": datetime.now().isoformat(),
                "topic": topic,
            }
    
    async def update_step(self, step: str, progress: int = None):
        """更新当前步骤"""
        async with self._lock:
            self._status["current_step"] = step
            if progress is not None:
                self._status["progress"] = progress
            else:
                # 根据步骤自动计算进度
                step_progress = {
                    "crawler_agent": 10,
                    "reporter": 30,
                    "analyst": 50,
                    "debater": 70,
                    "writer": 90,
                }
                self._status["progress"] = step_progress.get(step, self._status["progress"])
    
    async def finish_workflow(self):
        """完成工作流"""
        async with self._lock:
            self._status = {
                "running": False,
                "current_step": None,
                "progress": 100,
                "started_at": self._status.get("started_at"),
                "topic": self._status.get("topic"),
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        async with self._lock:
            return self._status.copy()
    
    async def reset(self):
        """重置状态"""
        async with self._lock:
            self._status = {
                "running": False,
                "current_step": None,
                "progress": 0,
                "started_at": None,
                "topic": None,
            }


# 全局实例
workflow_status = WorkflowStatusManager()
