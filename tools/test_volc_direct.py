import json
import time
import os
import requests
import base64
from dotenv import load_dotenv

try:
    from volcengine.visual.VisualService import VisualService
except ImportError:
    print("❌ 未找到volcengine SDK，请执行：pip install volcengine --upgrade")
    exit(1)

load_dotenv()

def test_volc_jimeng_t2i():
    ak = os.getenv("VOLC_ACCESS_KEY")
    sk = os.getenv("VOLC_SECRET_KEY")
    
    if not ak or not sk:
        print("❌ 错误: 未找到 VOLC_ACCESS_KEY 或 VOLC_SECRET_KEY")
        return

    print(f"🚀 测试即梦文生图 API（对齐原生HTTP文档）...")
    print(f"🔑 使用 AK: {ak[:10]}...")
    
    # 初始化服务
    visual_service = VisualService()
    visual_service.set_ak(ak)
    visual_service.set_sk(sk)
    visual_service.set_host("visual.volcengineapi.com")

    # 1. 提交任务
    submit_params = {
        "req_key": "jimeng_t2i_v40",
        "prompt": "帮我生成一张图。画面包含：一个精致的玻璃‘围墙花园’，里面生长着发光的数字藤蔓和电路板花朵，但花园被巨大的锁链和半透明的‘数据流墙壁’环绕；一个穿着时尚的都市女性站在花园外，手拿放大镜观察围墙，表情带着思考与警觉；一个极简风格的桌面，上面放着打开的笔记本电脑，屏幕显示着复杂的代码和‘民主化’字样，但键盘被无形的锁链缠绕；一个俯拍视角，展示多巴胺色系的抽象地图，几条明亮的数据河流最终都汇入几个被标注为公司Logo的黑色漩涡。整体风格为赛博朋克美学混合精致小红书生活感，使用高对比度的霓虹色调与柔和的人物打光，强调氛围感和电影感构图，画面中可融入‘围墙花园’、‘控制’等文字元素。",
        "scale": 10.0,
        "width": 1024,
        "height": 1024,
        "style": "小红书",
        "steps": 30,
        "seed": -1
    }
    
    print("\n1️⃣ 提交生图任务...")
    try:
        resp = visual_service.cv_sync2async_submit_task(submit_params)
        print(f"📥 提交响应: {json.dumps(resp, indent=2, ensure_ascii=False)}")
        
        if resp.get("code") != 10000:
            print(f"\n❌ 提交失败: {resp.get('message')}")
            return

        task_id = resp["data"]["task_id"]
        print(f"\n✅ 提交成功！Task ID: {task_id}")
        
    except Exception as e:
        print(f"\n❌ 提交异常: {str(e)}")
        return

    # 2. 轮询结果
    print("\n2️⃣ 轮询结果（最多60秒）...")
    # 要求同时返回URL和Base64
    req_json_str = json.dumps({
        "return_url": True,
        "return_base64": True
    })
    
    get_params = {
        "req_key": "jimeng_t2i_v40",
        "task_id": task_id,
        "req_json": req_json_str
    }
    
    max_retry = 20
    success = False
    
    for i in range(max_retry):
        time.sleep(3)
        try:
            result = visual_service.cv_sync2async_get_result(get_params)
            print(f"⏳ 第{i+1}次查询，响应码: {result.get('code')}")
            
            if result.get("code") != 10000:
                err_msg = result.get("message", "未知错误")
                print(f"⚠️ 查询失败: {err_msg} (Request ID: {result.get('request_id')})")
                continue
            
            data = result.get("data", {})
            status = data.get("status")
            print(f"📊 任务状态: {status}")
            
            if status == "done":
                # 解析Base64图片（优先）
                binary_base64 = data.get("binary_data_base64", [])
                # 解析URL图片（备用）
                image_urls = data.get("image_urls", [])
                
                # 处理Base64图片
                if binary_base64 and len(binary_base64) > 0:
                    print("\n✨ 生成成功！保存Base64图片...")
                    for idx, b64_str in enumerate(binary_base64):
                        try:
                            # 过滤空值
                            if not b64_str:
                                continue
                            # 解码并保存
                            img_data = base64.b64decode(b64_str)
                            save_path = f"jimeng_image_{task_id}_{idx+1}.png"
                            with open(save_path, "wb") as f:
                                f.write(img_data)
                            print(f"   🖼️ 图片 {idx+1} 已保存到: {os.path.abspath(save_path)}")
                        except Exception as e:
                            print(f"   ❌ 图片 {idx+1} 解码失败: {str(e)}")
                
                # 处理URL图片（备用）
                elif image_urls:
                    print("\n✨ 生成成功！图片链接（有效期24h）：")
                    for idx, url in enumerate(image_urls):
                        clean_url = url.strip()
                        print(f"   🖼️ {idx+1}: {clean_url}")
                        # 尝试下载URL图片
                        try:
                            headers = {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                            }
                            resp = requests.get(clean_url, headers=headers, timeout=30)
                            if resp.status_code == 200:
                                save_path = f"jimeng_url_image_{idx+1}.png"
                                with open(save_path, "wb") as f:
                                    f.write(resp.content)
                                print(f"      ✅ 图片已下载到: {os.path.abspath(save_path)}")
                            else:
                                print(f"      ❌ URL访问失败，状态码: {resp.status_code}")
                        except Exception as e:
                            print(f"      ❌ URL下载异常: {str(e)}")
                else:
                    print("\n⚠️ 任务完成但无图片数据")
                
                success = True
                break
            elif status == "failed":
                print(f"\n❌ 任务失败: {data.get('error_msg', '未知原因')}")
                break
            elif status in ["in_queue", "generating"]:
                continue
            elif status in ["not_found", "expired"]:
                print(f"\n❌ 任务{status}，请重新提交")
                break
                
        except Exception as e:
            err_str = str(e)
            if "50400" in err_str and "Access Denied" in err_str:
                print(f"⚠️ 第{i+1}次查询鉴权失败: Access Denied")
            else:
                print(f"⚠️ 第{i+1}次查询出错: {err_str}")
            continue
    
    if not success:
        print(f"\n⏰ 轮询超时，可手动用Task ID {task_id} 查询")
    
    print("\n🏁 测试结束。")

if __name__ == "__main__":
    test_volc_jimeng_t2i()