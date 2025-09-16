# 使用Python官方镜像（非slim版本，包含更多系统库）
FROM python:3.9

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 设置工作目录
WORKDIR /app

# 升级pip并配置国内镜像源
RUN pip install --upgrade pip && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 先复制requirements文件并安装依赖（利用Docker缓存）
COPY requirements-docker.txt /app/requirements.txt

# 安装基础Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装CPU版本的PyTorch以减小镜像大小
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 复制项目文件
COPY . /app/

# 创建必要的目录
RUN mkdir -p /app/uploads /app/run/predict

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "manage.py"]