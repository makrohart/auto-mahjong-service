# 使用国内镜像源的Python官方slim镜像，更轻量化
FROM python:3.9-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# 设置工作目录
WORKDIR /app

# 安装系统依赖（OpenCV和PyTorch所需的完整依赖）
RUN apt-get update && \
    apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    libgl1-mesa-dri \
    libgthread-2.0-0 \
    libx11-6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 配置国内镜像源并升级pip（增加超时时间）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn && \
    pip config set global.timeout 300 && \
    pip install --upgrade pip --timeout 300

# 先复制requirements文件并安装依赖（利用Docker缓存）
COPY requirements-docker.txt /app/requirements.txt

# 安装基础Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装CPU版本的PyTorch以减小镜像大小（使用国内镜像，增加超时时间）
RUN pip install --no-cache-dir torch torchvision --index-url https://pypi.tuna.tsinghua.edu.cn/simple --timeout 300

# 复制项目文件
COPY . /app/

# 创建必要的目录
RUN mkdir -p /app/uploads /app/run/predict

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "manage.py"]