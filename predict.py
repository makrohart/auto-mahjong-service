import os
import json
from pathlib import Path
from mahjong_predictor import predict_mahjong

def predict(image_path: str) -> dict:
    """
    使用YOLO模型进行麻将牌识别
    
    Args:
        image_path: 输入图片路径
        
    Returns:
        dict: 包含JSON结果和输出图片路径的字典
    """
    try:
        # 检查输入文件是否存在
        if not os.path.exists(image_path):
            raise Exception(f"输入图片文件不存在: {image_path}")
        
        # 确保run目录存在
        run_dir = Path("run")
        run_dir.mkdir(exist_ok=True)
        
        # 检查模型文件是否存在
        model_path = "best.pt"
        if not os.path.exists(model_path):
            raise Exception(f"找不到模型文件: {model_path}")
        
        # 使用YOLO模型进行预测
        results = predict_mahjong(
            image_path=image_path,
            model_path=model_path,
            conf_threshold=0.1,
            save_result=True,
            output_dir="run/predict"
        )
        
        if not results:
            return {
                "success": True,
                "json_result": [],
                "output_image_path": None,
                "message": "未检测到任何麻将牌"
            }
        
        # 查找输出图片 - 图片在run/predict/predictxx子目录下
        output_image_path = None
        predict_dir = run_dir / "predict"
        
        if predict_dir.exists():
            predict_subdirs = [d for d in predict_dir.iterdir() if d.is_dir() and d.name.startswith('predict')]
            
            if predict_subdirs:
                # 使用最新的子目录
                latest_subdir = sorted(predict_subdirs)[-1]
                image_files = list(latest_subdir.glob("*.jpg")) + list(latest_subdir.glob("*.png"))
                if image_files:
                    output_image_path = str(image_files[-1])  # 使用最新的图片文件
        
        return {
            "success": True,
            "json_result": results,
            "output_image_path": output_image_path,
            "message": f"成功识别出 {sum(r['total_detections'] for r in results)} 张麻将牌"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "json_result": None,
            "output_image_path": None
        }