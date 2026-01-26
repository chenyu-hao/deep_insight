#!/usr/bin/env python3
"""
测试 AI 生图张数配置功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.user_settings import (
    get_image_generation_count,
    update_user_settings,
    get_volcengine_settings
)

def test_default_count():
    """测试默认生图张数"""
    count = get_image_generation_count()
    print(f"✓ 默认生图张数: {count}")
    assert count == 2, f"Expected 2, got {count}"

def test_custom_count():
    """测试自定义生图张数"""
    # 保存配置
    update_user_settings(volcengine={"image_count": 5})
    count = get_image_generation_count()
    print(f"✓ 自定义生图张数: {count}")
    assert count == 5, f"Expected 5, got {count}"
    
    # 测试边界值
    update_user_settings(volcengine={"image_count": 1})
    count = get_image_generation_count()
    print(f"✓ 最小生图张数: {count}")
    assert count == 1, f"Expected 1, got {count}"
    
    update_user_settings(volcengine={"image_count": 9})
    count = get_image_generation_count()
    print(f"✓ 最大生图张数: {count}")
    assert count == 9, f"Expected 9, got {count}"

def test_invalid_count():
    """测试无效值时回退到默认值"""
    # 测试超出范围
    update_user_settings(volcengine={"image_count": 10})
    count = get_image_generation_count()
    print(f"✓ 超出范围时使用默认值: {count}")
    assert count == 2, f"Expected 2 (default), got {count}"
    
    # 测试负数
    update_user_settings(volcengine={"image_count": -1})
    count = get_image_generation_count()
    print(f"✓ 负数时使用默认值: {count}")
    assert count == 2, f"Expected 2 (default), got {count}"
    
    # 测试非整数
    update_user_settings(volcengine={"image_count": "abc"})
    count = get_image_generation_count()
    print(f"✓ 非整数时使用默认值: {count}")
    assert count == 2, f"Expected 2 (default), got {count}"

def test_volcengine_settings():
    """测试完整的火山引擎配置"""
    update_user_settings(volcengine={
        "access_key": "test_ak",
        "secret_key": "test_sk",
        "image_count": 3
    })
    
    settings = get_volcengine_settings()
    print(f"✓ 火山引擎配置: {settings}")
    assert settings.get("access_key") == "test_ak"
    assert settings.get("secret_key") == "test_sk"
    assert settings.get("image_count") == 3
    
    count = get_image_generation_count()
    assert count == 3, f"Expected 3, got {count}"

if __name__ == "__main__":
    print("=" * 60)
    print("测试 AI 生图张数配置功能")
    print("=" * 60)
    
    try:
        test_default_count()
        test_custom_count()
        test_invalid_count()
        test_volcengine_settings()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        
        # 恢复默认配置
        update_user_settings(volcengine={"image_count": 2})
        print("\n已恢复默认配置（生图张数: 2）")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
