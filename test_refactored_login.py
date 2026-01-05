#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试重构后的登录功能
验证多平台登录支持和串行抓取模式
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.media_crawler_service import crawler_service

async def test_platform_login(platform: str, keywords: str = "测试"):
    """测试单个平台的登录功能"""
    print(f"\n{'='*60}")
    print(f"[测试开始] 平台: {platform}, 关键词: {keywords}")
    print(f"[时间] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    try:
        # 获取平台配置
        platform_config = crawler_service._get_platform_config(platform)
        print(f"[配置] 平台名称: {platform_config['name']}")
        print(f"[配置] 登录超时: {platform_config['login_timeout']}秒")
        print(f"[配置] 扫码等待: {platform_config['qr_wait_time']}秒")
        print(f"[配置] 双重验证: {platform_config['double_verification']}")
        
        # 执行爬取测试
        start_time = asyncio.get_event_loop().time()
        results = await crawler_service.crawl_platform(
            platform=platform,
            keywords=keywords,
            max_items=5,  # 少量测试
            timeout=platform_config['login_timeout']
        )
        end_time = asyncio.get_event_loop().time()
        
        elapsed = end_time - start_time
        print(f"\n[测试结果] 平台: {platform}")
        print(f"[耗时] {elapsed:.2f}秒")
        print(f"[结果数量] {len(results)} 条")
        
        if results:
            print(f"[示例数据] 第一条结果:")
            sample = results[0]
            print(f"  - 平台: {sample.get('platform', 'unknown')}")
            print(f"  - 标题: {sample.get('title', '无标题')[:50]}...")
            print(f"  - 作者: {sample.get('author', {}).get('nickname', '未知')}")
            print(f"  - 互动: 点赞{sample.get('interactions', {}).get('liked_count', 0)}")
        else:
            print(f"[警告] 未获取到任何数据")
            
        return True, results
        
    except Exception as e:
        print(f"[错误] 平台 {platform} 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, []

async def test_serial_crawling():
    """测试串行抓取模式"""
    print(f"\n{'='*60}")
    print(f"[串行模式测试] 多平台串行抓取")
    print(f"[时间] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    platforms = ["xhs", "dy", "bili"]  # 测试3个平台
    keywords = "人工智能"
    
    try:
        start_time = asyncio.get_event_loop().time()
        platform_data = await crawler_service.crawl_multiple_platforms(
            platforms=platforms,
            keywords=keywords,
            max_items_per_platform=5,
            timeout_per_platform=300,  # 5分钟测试
            max_concurrent=1  # 强制串行
        )
        end_time = asyncio.get_event_loop().time()
        
        total_elapsed = end_time - start_time
        total_items = sum(len(items) for items in platform_data.values())
        
        print(f"\n[串行测试结果]")
        print(f"[总耗时] {total_elapsed:.2f}秒")
        print(f"[总结果] {total_items} 条")
        print(f"[平台详情]:")
        
        for platform, items in platform_data.items():
            print(f"  - {platform}: {len(items)} 条")
            
        # 验证确实是串行执行
        expected_min_time = len(platforms) * 30  # 假设每个平台至少30秒
        if total_elapsed >= expected_min_time:
            print(f"[验证] 串行模式验证通过 (实际{total_elapsed:.0f}s >= 期望{expected_min_time}s)")
        else:
            print(f"[警告] 可能不是纯串行执行")
            
        return True
        
    except Exception as e:
        print(f"[错误] 串行模式测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print(f"{'='*80}")
    print(f"[重构登录功能测试] 多平台登录支持与串行抓取模式")
    print(f"[测试时间] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[Python版本] {sys.version}")
    print(f"[操作系统] {sys.platform}")
    print(f"{'='*80}")
    
    # 测试所有平台的配置
    all_platforms = ["wb", "bili", "xhs", "tieba", "dy", "ks", "zhihu"]
    
    print(f"\n[配置验证] 所有平台配置:")
    for platform in all_platforms:
        config = crawler_service._get_platform_config(platform)
        print(f"  {platform}: {config['name']} (超时:{config['login_timeout']}s, 扫码:{config['qr_wait_time']}s)")
    
    # 测试单个平台（选择B站，因为它需要登录）
    print(f"\n[单项测试] 测试B站登录功能:")
    success, results = await test_platform_login("bili", "编程")
    
    # 测试串行模式
    print(f"\n[串行测试] 测试串行抓取模式:")
    serial_success = await test_serial_crawling()
    
    # 总结
    print(f"\n{'='*80}")
    print(f"[测试总结]")
    print(f"B站登录测试: {'PASS' if success else 'FAIL'}")
    print(f"串行模式测试: {'PASS' if serial_success else 'FAIL'}")
    
    if success and serial_success:
        print(f"[结果] 重构后的登录功能测试通过！")
    else:
        print(f"[结果] 部分功能需要进一步调试")
    
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(main())