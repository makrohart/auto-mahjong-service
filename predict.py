
import subprocess
import json
import os
from pathlib import Path

def predict(image_path: str) -> dict:
    """
    调用mahjong_predictor.exe进行图片识别
    
    Args:
        image_path: 输入图片路径
        
    Returns:
        dict: 包含JSON结果和输出图片路径的字典
    """
    try:
        # 确保run目录存在
        run_dir = Path("run")
        run_dir.mkdir(exist_ok=True)
        
        # 构建命令
        cmd = [
            "mahjong_predictor.exe",
            image_path,
            "--model", "best.pt",
            "--conf", "0.1",
            "--output-format", "json",
            "--output-dir", "run/predict",
            "--save",
            "--save-results"
        ]
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd(), encoding='utf-8', errors='ignore')
        
        if result.returncode != 0:
            raise Exception(f"预测程序执行失败: {result.stderr}")
        
        # 查找输出文件
        # JSON文件在run/predict目录下
        predict_dir = run_dir / "predict"
        json_files = list(predict_dir.glob("*.json"))
        
        if not json_files:
            raise Exception("未找到输出的JSON文件")
        
        # 使用最新的JSON文件
        json_file = json_files[-1]
        
        # 读取JSON结果
        with open(json_file, 'r', encoding='utf-8') as f:
            json_result = json.load(f)
        
        # 查找输出图片 - 图片在run/predict/predictxx子目录下
        output_image_path = None
        predict_subdirs = [d for d in predict_dir.iterdir() if d.is_dir() and d.name.startswith('predict')]
        
        if predict_subdirs:
            # 使用最新的子目录
            latest_subdir = sorted(predict_subdirs)[-1]
            image_files = list(latest_subdir.glob("*.jpg")) + list(latest_subdir.glob("*.png"))
            if image_files:
                output_image_path = str(image_files[-1])  # 使用最新的图片文件
        
        return {
            "success": True,
            "json_result": json_result,
            "output_image_path": output_image_path,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "json_result": None,
            "output_image_path": None
        }