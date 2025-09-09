FROM ubuntu:latest

# 设置上海时区（Ubuntu方式）
RUN apt-get update && \
    apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata

# 使用阿里云镜像源（Ubuntu版）
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 拷贝项目文件
COPY . /app
WORKDIR /app

# 配置pip镜像源并安装依赖
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn && \
    # pip install --upgrade pip --break-system-packages && \
    pip install --user -r requirements.txt --break-system-packages

# 启动命令
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080"]