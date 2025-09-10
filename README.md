# 麻将AI识别服务

这是一个基于Flask的微信云后台服务，用于调用AI识别程序进行麻将图片识别。

## 功能特性

- 接收图片文件上传
- 调用 `mahjong_predictor.exe` 进行AI识别
- 返回JSON识别结果和结果图片
- 支持多种图片格式（png, jpg, jpeg, gif）

## 项目结构

```
auto-mahjong-service/
├── mahjong_predictor.exe    # AI识别可执行程序
├── best.pt                  # 模型文件
├── manage.py               # 服务启动文件
├── init.py                 # Flask应用配置
├── predict.py              # 预测功能实现
├── requirements.txt        # Python依赖
├── run/                    # 输出结果目录
├── uploads/                # 临时上传目录
└── templates/              # 前端模板
```

## 安装和运行

1. 安装Python依赖：
```bash
pip install -r requirements.txt
```

2. 启动服务：
```bash
python manage.py
```

服务将在 `http://localhost:8080` 启动。

## API接口

### 图片识别接口

**POST** `/predict_image`

- **Content-Type**: `multipart/form-data`
- **参数**: 
  - `file`: 图片文件（支持png, jpg, jpeg, gif）

**响应示例**:
```json
{
  "success": true,
  "json_result": {
    // AI识别的JSON结果
  },
  "output_image_url": "/get_result_image/result.jpg"
}
```

### 获取结果图片接口

**GET** `/get_result_image/<filename>`

- **参数**: 
  - `filename`: 结果图片文件名

- **响应**: 图片文件

## 使用示例

### 使用curl测试

```bash
curl -X POST -F "file=@your_image.jpg" http://localhost:8080/predict_image
```

### 使用Python测试

```python
import requests

url = "http://localhost:8080/predict_image"
with open("test_image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)
    print(response.json())
```

## 配置说明

- 模型文件路径: `best.pt`
- 置信度阈值: `0.5`
- 输出格式: `json`
- 输出目录: `run/`

## 注意事项

1. 确保 `mahjong_predictor.exe` 和 `best.pt` 文件在项目根目录
2. 确保有足够的磁盘空间用于临时文件和输出文件
3. 服务会自动清理上传的临时文件
4. 结果图片会保存在 `run/` 目录下
