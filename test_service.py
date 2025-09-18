#!/usr/bin/env python3
"""
测试Flask服务的脚本
"""
import requests
import json
import os

def test_predict_service():
    """测试预测服务"""
    # 本地测试URL
    base_url = "https://auto-mahjong-service-staging-179677-10-1372684131.sh.run.tcloudbase.com"
    
    # 测试图片路径 - 使用项目中的示例图片
    test_image_paths = [
        "augmented_1.jpg"
    ]
    
    test_image_path = None
    for path in test_image_paths:
        if os.path.exists(path):
            test_image_path = path
            break
    
    if not test_image_path:
        print("未找到测试图片，请将测试图片放在以下位置之一：")
        for path in test_image_paths:
            print(f"  - {path}")
        return
    
    print("开始测试预测服务...")
    print("注意：AI 识别可能需要较长时间，请耐心等待...")
    
    # 准备请求
    url = f"{base_url}/predict_image"
    
    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': f}
            # 设置超时时间为60秒（连接超时5秒，读取超时60秒）
            response = requests.post(url, files=files, timeout=(10, 300))
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 预测成功!")
                print(f"JSON结果: {result.get('json_result')}")
                if result.get('output_image_url'):
                    print(f"结果图片URL: {base_url}{result.get('output_image_url')}")
            else:
                print(f"❌ 预测失败: {result.get('error')}")
        else:
            print(f"❌ 请求失败: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保Flask服务正在运行")
    except requests.exceptions.Timeout:
        print("❌ 请求超时！AI 识别可能需要更长时间，请检查服务状态或增加超时时间")
    except requests.exceptions.ReadTimeout:
        print("❌ 读取响应超时！服务可能正在处理中，请稍后重试")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    test_predict_service()
