#!/usr/bin/env python3
"""
测试 AI 生图张数配置的持久化
"""
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.settings.user_settings import (
    get_image_generation_count,
    update_user_settings,
    get_volcengine_settings,
    load_user_settings,
    _SETTINGS_FILE
)

def test_persistence():
    """测试配置持久化"""
    print("=" * 60)
    print("测试 AI 生图张数配置持久化")
    print("=" * 60)
    
    # 1. 保存配置
    print("\n1. 保存配置: image_count = 5")
    update_user_settings(volcengine={
        "access_key": "test_ak",
        "secret_key": "test_sk",
        "image_count": 5
    })
    
    # 2. 验证内存中的值
    count = get_image_generation_count()
    print(f"   内存中的值: {count}")
    assert count == 5, f"Expected 5, got {count}"
    
    # 3. 读取文件内容
    print(f"\n2. 读取配置文件: {_SETTINGS_FILE}")
    if _SETTINGS_FILE.exists():
        with open(_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            file_content = json.load(f)
        print(f"   文件内容: {json.dumps(file_content, indent=2, ensure_ascii=False)}")
        
        if 'volcengine' in file_content:
            volc = file_content['volcengine']
            print(f"\n   volcengine 配置:")
            print(f"   - access_key: {volc.get('access_key', 'N/A')}")
            print(f"   - secret_key: {volc.get('secret_key', 'N/A')}")
            print(f"   - image_count: {volc.get('image_count', 'N/A')}")
            
            assert volc.get('image_count') == 5, f"文件中的 image_count 应该是 5，实际是 {volc.get('image_count')}"
        else:
            print("   ❌ 文件中没有 volcengine 配置！")
            return False
    else:
        print(f"   ❌ 配置文件不存在: {_SETTINGS_FILE}")
        return False
    
    # 4. 重新加载配置（模拟重启）
    print("\n3. 重新加载配置（模拟重启）")
    settings = load_user_settings()
    volc_settings = settings.get('volcengine', {})
    print(f"   重新加载的 volcengine: {volc_settings}")
    
    count_after_reload = get_image_generation_count()
    print(f"   重新加载后的 image_count: {count_after_reload}")
    assert count_after_reload == 5, f"重新加载后应该是 5，实际是 {count_after_reload}"
    
    # 5. 测试修改为其他值
    print("\n4. 修改配置: image_count = 3")
    update_user_settings(volcengine={
        "access_key": "test_ak",
        "secret_key": "test_sk",
        "image_count": 3
    })
    
    count = get_image_generation_count()
    print(f"   修改后的值: {count}")
    assert count == 3, f"Expected 3, got {count}"
    
    # 6. 再次验证文件
    with open(_SETTINGS_FILE, 'r', encoding='utf-8') as f:
        file_content = json.load(f)
    volc = file_content.get('volcengine', {})
    print(f"   文件中的 image_count: {volc.get('image_count')}")
    assert volc.get('image_count') == 3, f"文件中应该是 3，实际是 {volc.get('image_count')}"
    
    print("\n" + "=" * 60)
    print("✅ 持久化测试通过！")
    print("=" * 60)
    
    # 恢复默认值
    update_user_settings(volcengine={"image_count": 2})
    print("\n已恢复默认配置（生图张数: 2）")
    
    return True

if __name__ == "__main__":
    try:
        success = test_persistence()
        if not success:
            sys.exit(1)
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
