#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
麻将识别可执行程序
输入：图片路径
输出：识别结果（类型和位置）
"""

import argparse
import sys
import os
import json
from pathlib import Path
from ultralytics import YOLO
import cv2

# 类别名称映射
CLASS_NAMES = [
    '一饼', '二饼', '三饼', '四饼', '五饼', '六饼', '七饼', '八饼', '九饼',
    '一条', '二条', '三条', '四条', '五条', '六条', '七条', '八条', '九条',
    '一万', '二万', '三万', '四万', '五万', '六万', '七万', '八万', '九万',
    '东风', '南风', '西风', '北风', '红中', '发财', '白板'
]

def get_model_path():
    """获取模型文件路径，支持相对路径和绝对路径"""
    # 尝试多个可能的模型路径
    possible_paths = [
        'mj-train/runs/train3/weights/best.pt',
        'models/best_single_mahjong.pt',
        'best.pt'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # 如果都找不到，返回默认路径
    return 'mj-train/runs/train3/weights/best.pt'

def predict_mahjong(image_path: str, model_path: str = None, conf_threshold: float = 0.1, 
                   save_result: bool = False, output_dir: str = 'run/predict') -> list:
    """
    预测麻将牌
    
    Args:
        image_path: 输入图片路径
        model_path: 模型文件路径
        conf_threshold: 置信度阈值
        save_result: 是否保存结果图片
        output_dir: 输出目录
    
    Returns:
        识别结果列表
    """
    try:
        # 检查图片文件是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        # 获取模型路径
        if model_path is None:
            model_path = get_model_path()
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        
        # 加载模型
        print(f"正在加载模型: {model_path}")
        model = YOLO(model_path)
        
        # 读取图片
        print(f"正在读取图片: {image_path}")
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        # 进行推理
        print("正在进行推理...")
        results = model.predict(
            source=image,
            save=save_result,
            show=False,
            conf=conf_threshold,
            project=output_dir
        )
        
        # 处理结果
        output = []
        for result in results:
            # 提取类别ID和边界框数据
            cls_data = result.boxes.cls  # 类别ID
            box_data = result.boxes.data  # 边界框数据 [x1, y1, x2, y2, conf, cls]
            
            # 转换为列表
            cls_list = cls_data.tolist() if hasattr(cls_data, 'tolist') else cls_data
            box_list = box_data.tolist() if hasattr(box_data, 'tolist') else box_data
            
            # 格式化输出
            detections = []
            for i, (cls_id, box) in enumerate(zip(cls_list, box_list)):
                x1, y1, x2, y2, conf, cls = box
                class_name = CLASS_NAMES[int(cls)] if int(cls) < len(CLASS_NAMES) else f"未知类别_{int(cls)}"
                
                detection = {
                    'id': i + 1,
                    'class_id': int(cls),
                    'class_name': class_name,
                    'confidence': float(conf),
                    'bbox': {
                        'x1': float(x1),
                        'y1': float(y1),
                        'x2': float(x2),
                        'y2': float(y2),
                        'width': float(x2 - x1),
                        'height': float(y2 - y1)
                    }
                }
                detections.append(detection)
            
            output.append({
                'image_path': image_path,
                'total_detections': len(detections),
                'detections': detections
            })
        
        return output
        
    except Exception as e:
        print(f"预测过程中发生错误: {str(e)}", file=sys.stderr)
        return []

def format_output(results: list, output_format: str = 'json', save_to_file: bool = False, output_dir: str = 'run/predict') -> str:
    """格式化输出结果"""
    if not results:
        return "未检测到任何麻将牌"
    
    if output_format == 'json':
        output_str = json.dumps(results, ensure_ascii=False, indent=2)
    elif output_format == 'text':
        output_lines = []
        for result in results:
            output_lines.append(f"图片: {result['image_path']}")
            output_lines.append(f"检测到 {result['total_detections']} 张麻将牌:")
            
            for detection in result['detections']:
                bbox = detection['bbox']
                output_lines.append(
                    f"  {detection['id']}. {detection['class_name']} "
                    f"(置信度: {detection['confidence']:.3f}) "
                    f"位置: ({bbox['x1']:.1f}, {bbox['y1']:.1f}) - "
                    f"({bbox['x2']:.1f}, {bbox['y2']:.1f}) "
                    f"尺寸: {bbox['width']:.1f}x{bbox['height']:.1f}"
                )
            output_lines.append("")
        
        output_str = "\n".join(output_lines)
    else:
        output_str = str(results)
    
    # 保存到文件
    if save_to_file:
        import os
        from datetime import datetime
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_format == 'json':
            filename = f"mahjong_results_{timestamp}.json"
        else:
            filename = f"mahjong_results_{timestamp}.txt"
        
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(output_str)
            print(f"\n结果已保存到: {filepath}")
        except Exception as e:
            print(f"保存文件失败: {e}")
    
    return output_str

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='麻将牌识别程序',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python mahjong_predictor.py image.jpg
  python mahjong_predictor.py image.jpg --model models/best.pt
  python mahjong_predictor.py image.jpg --model models/best.pt --conf 0.5 --output-format text
  python mahjong_predictor.py image.jpg --model models/best.pt --save
        """
    )
    
    parser.add_argument('image_path', help='输入图片路径')
    parser.add_argument('--model', '-m', required=True, help='模型文件路径 (必需)')
    parser.add_argument('--conf', '-c', type=float, default=0.1, 
                       help='置信度阈值 (默认: 0.1)')
    parser.add_argument('--output-format', '-f', choices=['json', 'text'], 
                       default='json', help='输出格式 (默认: json)')
    parser.add_argument('--save', '-s', action='store_true', 
                       help='保存结果图片')
    parser.add_argument('--output-dir', '-o', default='run/predict', 
                       help='结果图片保存目录 (默认: run/predict)')
    parser.add_argument('--quiet', '-q', action='store_true', 
                       help='静默模式，只输出结果')
    parser.add_argument('--save-results', action='store_true', 
                       help='保存结果到文件')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("=== 麻将牌识别程序 ===")
        print(f"输入图片: {args.image_path}")
        print(f"模型文件: {args.model}")
        print(f"置信度阈值: {args.conf}")
        print(f"输出格式: {args.output_format}")
        print()
    
    # 执行预测
    results = predict_mahjong(
        image_path=args.image_path,
        model_path=args.model,
        conf_threshold=args.conf,
        save_result=args.save,
        output_dir=args.output_dir
    )
    
    # 输出结果
    if results:
        output = format_output(results, args.output_format, args.save_results, args.output_dir)
        print(output)
        
        if not args.quiet:
            print(f"\n检测完成！共识别出 {sum(r['total_detections'] for r in results)} 张麻将牌")
    else:
        print("未检测到任何麻将牌")
        sys.exit(1)

if __name__ == '__main__':
    main()
