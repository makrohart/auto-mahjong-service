#!/usr/bin/env python3
"""
测试Flask服务的脚本
"""
import requests
import json
import os

def test_predict_service():
    """测试预测服务"""
    base_url = "http://localhost:8080"
    
    # 测试图片路径（你需要提供一个测试图片）
    test_image_path = "D:/Projects/autoMahjong/mahjong-dataset/dataset/augumented/images/val/augmented_1.jpg"  # 请替换为实际的测试图片路径
    
    if not os.path.exists(test_image_path):
        print(f"测试图片 {test_image_path} 不存在，请提供测试图片")
        return
    
    print("开始测试预测服务...")
    
    # 准备请求
    url = f"{base_url}/predict_image"
    
    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
        
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
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    test_predict_service()
