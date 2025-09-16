# 麻将AI识别服务部署指南

## Docker部署

```bash
# 构建镜像
docker build -t mahjong-service:latest .

# 运行容器
docker run -d -p 8080:8080 --name mahjong-service mahjong-service:latest
```

## 云服务部署

### 腾讯云容器服务

1. 使用优化后的Dockerfile进行构建
2. 镜像大小优化，使用CPU版本的PyTorch

### 环境变量

- `PYTHONUNBUFFERED=1`: 确保Python输出不被缓冲
- `TZ=Asia/Shanghai`: 设置时区
- `DEBIAN_FRONTEND=noninteractive`: 避免交互式安装

## 故障排除

### OpenCV错误
如果遇到 `libGL.so.1` 错误，确保Dockerfile中包含了必要的系统依赖：
- `libgl1-mesa-glx`
- `libglib2.0-0`
- `libgthread-2.0-0`

### 内存不足
- 使用CPU版本的PyTorch减少内存占用
- 考虑增加容器内存限制

### 模型文件
确保 `best.pt` 模型文件存在于项目根目录

## 性能优化

1. **镜像大小**: 使用 `opencv-python-headless` 替代 `opencv-python`
2. **CPU优化**: 使用CPU版本的PyTorch
3. **缓存**: 利用Docker层缓存优化构建速度

## 监控

服务提供以下端点：
- 主页: `GET /`
- 预测接口: `POST /predict_image`
- 结果图片: `GET /get_result_image/<filename>`
