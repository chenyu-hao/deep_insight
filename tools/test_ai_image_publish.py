#!/usr/bin/env python3
"""
测试 AI 图片生成和发布流程

验证:
1. 后端图片生成是否正常
2. MCP 是否正确接收图片 URL
3. 发布流程是否能正常工作

使用方法:
    python tools/test_ai_image_publish.py
"""

import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_image_generator():
    """测试后端图片生成服务"""
    print("\n" + "=" * 60)
    print("🖼️  测试 1: 后端图片生成服务")
    print("=" * 60)
    
    try:
        from app.services.image.image_generator import image_generator_service
        from app.services.settings.user_settings import get_image_generation_count
        
        # 检查配置
        image_count = get_image_generation_count()
        print(f"✅ 配置的图片数量: {image_count}")
        
        if image_count == 0:
            print("⚠️  图片生成已禁用 (image_count=0)")
            return False
        
        # 检查 Volcengine SDK
        if image_generator_service.visual_service is None:
            print("❌ Volcengine SDK 未安装")
            return False
        print("✅ Volcengine SDK 已安装")
        
        # 检查凭证
        cfg = image_generator_service._effective_cfg()
        if not cfg.get("access_key") or not cfg.get("secret_key"):
            print("❌ Volcengine 凭证未配置")
            return False
        print(f"✅ Volcengine 凭证已配置 (AK: {cfg['access_key'][:6]}...)")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def test_mcp_job_result():
    """测试 MCP 任务结果中的图片"""
    print("\n" + "=" * 60)
    print("📋 测试 2: MCP 任务结果")
    print("=" * 60)
    
    try:
        from opinion_mcp.services.job_manager import job_manager
        
        # 获取最近完成的任务
        from opinion_mcp.schemas import JobStatus
        completed_jobs = job_manager.list_jobs(status=JobStatus.COMPLETED, limit=1)
        
        if not completed_jobs:
            print("⚠️  没有已完成的任务")
            return None
        
        job = completed_jobs[0]
        print(f"✅ 找到任务: {job.job_id}")
        print(f"   话题: {job.topic}")
        
        if not job.result:
            print("❌ 任务没有结果数据")
            return None
        
        result = job.result
        
        # 检查文案
        if result.copywriting:
            print(f"✅ 文案标题: {result.copywriting.title[:30] if result.copywriting.title else 'N/A'}...")
            print(f"   文案内容长度: {len(result.copywriting.content) if result.copywriting.content else 0}")
            print(f"   标签数量: {len(result.copywriting.tags) if result.copywriting.tags else 0}")
        else:
            print("❌ 没有文案数据")
        
        # 检查 AI 图片
        if result.ai_images:
            print(f"✅ AI 图片数量: {len(result.ai_images)}")
            for i, url in enumerate(result.ai_images):
                print(f"   图片 {i+1}: {url[:60]}...")
        else:
            print("❌ 没有 AI 图片")
        
        # 检查数据卡片
        if result.cards:
            print(f"✅ 数据卡片: title_card={bool(result.cards.title_card)}, debate_timeline={bool(result.cards.debate_timeline)}")
        else:
            print("⚠️  没有数据卡片 (阶段 F 正常)")
        
        return job
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_url_validation():
    """测试 URL 验证功能"""
    print("\n" + "=" * 60)
    print("🔗 测试 3: URL 验证功能")
    print("=" * 60)
    
    try:
        from opinion_mcp.utils.url_validator import validate_url, filter_valid_urls
        
        # 测试 URL
        test_urls = [
            "https://p3-sign.douyinpic.com/tos-cn-i-0813/test.jpg",  # 可能有效
            "https://invalid-domain-12345.com/image.jpg",  # 无效
            "not-a-url",  # 无效格式
        ]
        
        print("测试单个 URL 验证:")
        for url in test_urls:
            result = await validate_url(url, timeout=5.0)
            status = "✅" if result.valid else "❌"
            print(f"  {status} {url[:50]}... -> {result.status_code or result.error}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def test_publish_config():
    """测试发布配置"""
    print("\n" + "=" * 60)
    print("⚙️  测试 4: 发布配置")
    print("=" * 60)
    
    try:
        from app.core.config import Config
        
        mode = Config.get_image_publish_mode()
        print(f"✅ 当前发布模式: {mode}")
        
        if mode == "ai_only":
            print("   说明: 仅使用 AI 生成的配图")
        elif mode == "ai_and_cards":
            print("   说明: 使用数据卡片 + AI 配图")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def test_xhs_mcp_service():
    """测试小红书 MCP 服务"""
    print("\n" + "=" * 60)
    print("📱 测试 5: 小红书 MCP 服务")
    print("=" * 60)
    
    try:
        import httpx
        
        # 检查 MCP 服务是否运行
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get("http://localhost:18060/mcp")
                print(f"✅ XHS-MCP 服务响应: {resp.status_code}")
                return True
            except httpx.ConnectError:
                print("❌ XHS-MCP 服务未运行 (端口 18060)")
                print("   请运行: ./scripts/start-xhs-mcp.sh")
                return False
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🧪 AI 图片生成和发布流程测试")
    print("=" * 60)
    
    results = {}
    
    # 测试 1: 图片生成服务
    results["image_generator"] = await test_image_generator()
    
    # 测试 2: MCP 任务结果
    job = await test_mcp_job_result()
    results["mcp_job"] = job is not None
    
    # 测试 3: URL 验证
    results["url_validation"] = await test_url_validation()
    
    # 测试 4: 发布配置
    results["publish_config"] = await test_publish_config()
    
    # 测试 5: XHS MCP 服务
    results["xhs_mcp"] = await test_xhs_mcp_service()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！AI 图片发布流程应该可以正常工作。")
    else:
        print("\n⚠️  部分测试失败，请检查上述问题。")
    
    # 如果有任务结果，显示发布建议
    if job and job.result:
        print("\n" + "=" * 60)
        print("💡 发布建议")
        print("=" * 60)
        
        has_content = job.result.copywriting and job.result.copywriting.content
        has_images = job.result.ai_images and len(job.result.ai_images) > 0
        
        if has_content and has_images:
            print(f"✅ 任务 {job.job_id} 可以发布")
            print(f"   - 标题: {job.result.copywriting.title[:30]}...")
            print(f"   - 图片: {len(job.result.ai_images)} 张")
            print(f"\n   使用 MCP 工具发布:")
            print(f'   publish_to_xhs(job_id="{job.job_id}")')
        elif not has_content:
            print("❌ 缺少文案内容，无法发布")
        elif not has_images:
            print("❌ 缺少图片，无法发布")


if __name__ == "__main__":
    asyncio.run(main())
