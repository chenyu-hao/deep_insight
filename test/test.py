# 验证火山SDK核心模块是否可用
try:
    from volcengine.visual.VisualService import VisualService
    print("✅ 火山引擎Visual SDK加载成功")
    
    # 测试初始化服务（不调用接口，仅验证实例化）
    visual_service = VisualService()
    visual_service.set_ak("test")
    visual_service.set_sk("test")
    print("✅ VisualService初始化成功")
    
except ImportError as e:
    print(f"❌ SDK加载失败: {e}")
except Exception as e:
    print(f"❌ 初始化失败: {e}")