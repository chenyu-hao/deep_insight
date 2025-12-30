import asyncio
from typing import List, Dict, Any

class MockCrawler:
    async def crawl(self, inputs: List[str], platforms: List[str] = ["wb"]) -> str:
        print(f"🕷️ [MockCrawler] Pretending to crawl: {inputs} on {platforms}")
        await asyncio.sleep(1) # Simulate network delay
        
        # Return fake data relevant to the topic "AI replacing software engineers"
        return """
        [微博] 用户@科技大V：Devin这个AI程序员太强了，感觉初级码农真的要失业了。 #AI #程序员
        [B站] UP主@代码狂人：实测Devin，虽然能写代码，但在复杂系统设计上还是不如人类。大家不要焦虑，提升核心竞争力才是关键。
        [知乎] 匿名用户：AI取代软件工程师是个伪命题。软件工程不仅仅是写代码，还包括需求分析、沟通、架构设计等。AI目前只能作为辅助工具。
        [微博] 用户@互联网民工：看到Devin的演示，瑟瑟发抖。是不是该转行去卖炒粉了？
        [B站] UP主@AI前沿：GPT-4 Turbo的代码能力又有提升，未来编程门槛会越来越低，人人都是程序员的时代要来了。
        """