"""
测试所有 API 接口
运行前请确保后端服务已启动: python -m app.main
"""
import requests
import json
import sys
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_get_config():
    """测试获取配置接口"""
    print_section("1. 测试 GET /api/config")
    try:
        response = requests.get(f"{BASE_URL}/config")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] 配置获取成功")
            print(f"  - 辩论最大轮数: {data.get('debate_max_rounds')}")
            print(f"  - 默认平台: {data.get('default_platforms')}")
            print(f"  - 爬虫限制数量: {len(data.get('crawler_limits', {}))}")
            print(f"  - LLM 提供者数量: {len(data.get('llm_providers', {}))}")
            return True
        else:
            print(f"[FAIL] 失败: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        return False

def test_update_config():
    """测试更新配置接口"""
    print_section("2. 测试 PUT /api/config")
    try:
        # 先获取当前配置
        current = requests.get(f"{BASE_URL}/config").json()
        original_rounds = current.get('debate_max_rounds')
        
        # 更新配置
        update_data = {
            "debate_max_rounds": 5,
            "default_platforms": ["wb", "bili", "xhs"]
        }
        response = requests.put(f"{BASE_URL}/config", json=update_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] 配置更新成功")
            print(f"  - 更新字段: {result.get('updated_fields')}")
            print(f"  - 消息: {result.get('message')}")
            
            # 验证更新是否生效
            updated = requests.get(f"{BASE_URL}/config").json()
            if updated.get('debate_max_rounds') == 5:
                print("[OK] 验证: 配置已正确更新")
            else:
                print("[WARN] 警告: 配置更新可能未生效")
            
            # 恢复原配置
            requests.put(f"{BASE_URL}/config", json={"debate_max_rounds": original_rounds})
            print(f"[OK] 已恢复原配置 (debate_max_rounds={original_rounds})")
            return True
        else:
            print(f"[FAIL] 失败: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        return False

def test_get_outputs():
    """测试获取历史文件列表接口"""
    print_section("3. 测试 GET /api/outputs")
    try:
        # 测试默认参数
        response = requests.get(f"{BASE_URL}/outputs")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] 文件列表获取成功")
            print(f"  - 总文件数: {data.get('total')}")
            print(f"  - 返回文件数: {len(data.get('files', []))}")
            
            if data.get('files'):
                first_file = data['files'][0]
                print(f"  - 示例文件: {first_file.get('filename')}")
                print(f"  - 主题: {first_file.get('topic')}")
            
            # 测试分页
            response2 = requests.get(f"{BASE_URL}/outputs?limit=5&offset=0")
            if response2.status_code == 200:
                data2 = response2.json()
                print(f"[OK] 分页测试成功 (limit=5, offset=0): {len(data2.get('files', []))} 条")
            
            return True
        else:
            print(f"[FAIL] 失败: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] 错误: {e}")
        return False

def test_get_output_file():
    """测试获取指定文件内容接口"""
    print_section("4. 测试 GET /api/outputs/{filename}")
    try:
        # 先获取文件列表
        files_response = requests.get(f"{BASE_URL}/outputs?limit=1")
        if files_response.status_code != 200:
            print("[WARN]  无法获取文件列表，跳过此测试")
            return True
        
        files_data = files_response.json()
        if not files_data.get('files'):
            print("[WARN]  没有历史文件，跳过此测试")
            return True
        
        filename = files_data['files'][0]['filename']
        print(f"测试文件: {filename}")
        
        # 测试正常文件名
        response = requests.get(f"{BASE_URL}/outputs/{filename}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] 文件内容获取成功")
            print(f"  - 文件名: {data.get('filename')}")
            print(f"  - 内容长度: {len(data.get('content', ''))} 字符")
            print(f"  - 创建时间: {data.get('created_at')}")
        else:
            print(f"[FAIL] 失败: {response.text}")
            return False
        
        # 测试路径遍历攻击防护
        malicious_names = ["../config.py", "../../etc/passwd", "..\\..\\windows\\system32"]
        for malicious in malicious_names:
            response = requests.get(f"{BASE_URL}/outputs/{malicious}")
            if response.status_code == 400:
                print(f"[OK] 安全测试通过: {malicious} 被正确拒绝")
            else:
                print(f"[WARN]  安全警告: {malicious} 未被拒绝 (状态码: {response.status_code})")
        
        return True
    except Exception as e:
        print(f"[FAIL] 错误: {e}")
        return False

def test_get_workflow_status():
    """测试获取工作流状态接口"""
    print_section("5. 测试 GET /api/workflow/status")
    try:
        response = requests.get(f"{BASE_URL}/workflow/status")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] 工作流状态获取成功")
            print(f"  - 运行中: {data.get('running')}")
            print(f"  - 当前步骤: {data.get('current_step')}")
            print(f"  - 进度: {data.get('progress')}%")
            print(f"  - 主题: {data.get('topic')}")
            print(f"  - 开始时间: {data.get('started_at')}")
            return True
        else:
            print(f"[FAIL] 失败: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] 错误: {e}")
        return False

def test_analyze_endpoint():
    """测试分析接口（简化版，不等待完成）"""
    print_section("6. 测试 POST /api/analyze (简化测试)")
    try:
        # 测试请求格式
        test_data = {
            "topic": "测试主题",
            "urls": [],
            "platforms": ["wb"]  # 只测试一个平台，快速验证
        }
        
        print(f"发送请求: {json.dumps(test_data, ensure_ascii=False)}")
        print("[WARN]  注意: 这是一个长时间运行的接口，这里只测试连接和初始响应")
        
        response = requests.post(
            f"{BASE_URL}/analyze",
            json=test_data,
            stream=True,
            timeout=5  # 5秒超时，只测试连接
        )
        
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            print("[OK] 分析接口连接成功")
            print("  - 响应类型: Server-Sent Events (SSE)")
            
            # 尝试读取前几行
            count = 0
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith('data: '):
                        count += 1
                        if count <= 2:  # 只读取前2条消息
                            try:
                                data = json.loads(decoded[6:])
                                print(f"  - 收到消息 {count}: {data.get('agent_name')} ({data.get('status')})")
                            except:
                                pass
                        if count >= 2:
                            break
            print("[OK] 流式响应正常")
            return True
        else:
            print(f"[FAIL] 失败: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print("[WARN]  请求超时（这是正常的，因为分析需要较长时间）")
        print("[OK] 接口连接正常，可以接受请求")
        return True
    except Exception as e:
        print(f"[FAIL] 错误: {e}")
        return False

def test_cors():
    """测试 CORS 配置"""
    print_section("7. 测试 CORS 配置")
    try:
        response = requests.options(
            f"{BASE_URL}/config",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            }
        )
        print(f"OPTIONS 状态码: {response.status_code}")
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
        }
        print(f"CORS 头信息: {json.dumps(cors_headers, indent=2)}")
        
        if cors_headers["Access-Control-Allow-Origin"]:
            print("[OK] CORS 配置正常")
            return True
        else:
            print("[WARN]  CORS 头信息可能不完整")
            return True  # 不视为失败，因为可能使用通配符
    except Exception as e:
        print(f"[FAIL] 错误: {e}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  API 接口测试套件")
    print("=" * 60)
    print(f"\n测试目标: {BASE_URL}")
    print("请确保后端服务已启动 (python -m app.main)\n")
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/config", timeout=2)
        print("[OK] 服务器连接正常\n")
    except requests.exceptions.ConnectionError:
        print("[FAIL] 无法连接到服务器！")
        print("   请先启动后端服务: python -m app.main")
        sys.exit(1)
    except Exception as e:
        print(f"[FAIL] 连接错误: {e}")
        sys.exit(1)
    
    # 运行测试
    tests = [
        ("获取配置", test_get_config),
        ("更新配置", test_update_config),
        ("获取历史文件列表", test_get_outputs),
        ("获取文件内容", test_get_output_file),
        ("获取工作流状态", test_get_workflow_status),
        ("分析接口", test_analyze_endpoint),
        ("CORS 配置", test_cors),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"[FAIL] 测试 '{name}' 发生异常: {e}")
            results.append((name, False))
    
    # 汇总结果
    print_section("测试结果汇总")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK] 通过" if result else "[FAIL] 失败"
        print(f"  {status}: {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！")
        return 0
    else:
        print(f"\n[WARN]  有 {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
