# 麻将AI识别服务

这是一个基于 Flask 的服务，用于调用 Python 脚本进行麻将图片识别。

## 功能特性

- 接收图片文件上传
- 使用 `mahjong_predictor.py` 与 YOLO 模型进行识别
- 返回 JSON 识别结果（默认不保存结果图片）
- 支持多种图片格式（png, jpg, jpeg, gif）

## 项目结构

```
auto-mahjong-service/
├── mahjong_predictor.py     # AI 识别脚本（可直接通过 Python 运行）
├── best.pt                  # 模型文件（推理所需）
├── manage.py                # 服务启动文件
├── init.py                  # Flask 应用与路由
├── predict.py               # 服务内部调用的预测逻辑
├── requirements.txt         # Python 依赖
├── run/                     # 输出结果目录（JSON等）
├── uploads/                 # 临时上传目录
└── templates/               # 前端模板
```

## 安装和运行

### 本地开发

1. 安装 Python 依赖：
```bash
pip install -r requirements.txt
```

2. 启动服务：
```bash
python manage.py
```

服务将在 `http://localhost:8080` 启动。

### Docker 部署

1. 构建镜像：
```bash
docker build -t mahjong-service:latest .
```

2. 运行容器：
```bash
docker run -d -p 8080:8080 --name mahjong-service mahjong-service:latest
```

## API 接口

### 图片识别接口

**POST** `/predict_image`

- **Content-Type**: `multipart/form-data`
- **参数**:
  - `file`: 图片文件（支持 png, jpg, jpeg, gif）

**响应示例**（默认不返回结果图片 URL）：
```json
{
  "success": true,
  "json_result": [
    {
      "image_path": "uploads/xxx.jpg",
      "total_detections": 3,
      "detections": [
        {
          "id": 1,
          "class_id": 0,
          "class_name": "一饼",
          "confidence": 0.91,
          "bbox": { "x1": 10.0, "y1": 20.0, "x2": 100.0, "y2": 120.0, "width": 90.0, "height": 100.0 }
        }
      ]
    }
  ],
  "message": "成功识别出 3 张麻将牌",
  "output_image_url": null
}
```

说明：服务内部调用 `predict.py`，其默认不保存结果图片（避免字体下载阻塞），因此 `output_image_url` 为 `null`。如果需要保存结果图片，可在直接使用 `mahjong_predictor.py` 的命令行模式下添加 `--save`，或在服务代码中开启保存逻辑。

### 获取结果图片接口（可选）

**GET** `/get_result_image/<filename>`

- **参数**:
  - `filename`: 结果图片文件名

- **响应**: 图片文件

注意：默认服务不生成结果图片，只有在启用保存后该接口才有文件可取。

## 使用示例

### 使用 curl 测试服务

```bash
curl -X POST -F "file=@your_image.jpg" http://localhost:8080/predict_image
```

### 使用 Python 调用服务

```python
import requests

url = "http://localhost:8080/predict_image"
with open("test_image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)
    print(response.json())
```

## 直接使用脚本进行推理（命令行）

`mahjong_predictor.py` 可独立运行：

```bash
python mahjong_predictor.py <image_path> --model best.pt [--conf 0.1] [--output-format json|text] [--save] [--output-dir run/predict] [--save-results]
```

示例：

```bash
# JSON 输出，不保存图片
python mahjong_predictor.py image.jpg --model best.pt

# 文本输出并保存可视化结果图片
python mahjong_predictor.py image.jpg --model best.pt --conf 0.5 --output-format text --save

# 将结果保存为 JSON 文件至 run/predict
python mahjong_predictor.py image.jpg --model best.pt --save-results
```

## 配置说明

- 模型文件路径：默认使用项目根目录下的 `best.pt`（服务中由 `predict.py` 检查）。
- 置信度阈值：服务默认 `0.1`（脚本可通过 `--conf` 覆盖）。
- 输出目录：`run/`（脚本保存结果或服务产出 JSON 等文件时使用）。

## 注意事项

1. 确保 `best.pt` 模型文件存在于项目根目录（或在命令行中通过 `--model` 指定）。
2. 确保有足够的磁盘空间用于临时文件和输出文件。
3. 服务会在处理完成后自动清理上传的临时文件。
4. 仅在启用保存结果时才会生成结果图片至 `run/` 目录。
