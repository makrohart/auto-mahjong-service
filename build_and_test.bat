@echo off
echo ========================================
echo 麻将AI识别服务 - 本地构建和测试脚本
echo ========================================

echo.
echo [1/4] 清理旧的容器和镜像...
docker stop mahjong-service 2>nul
docker rm mahjong-service 2>nul
docker rmi mahjong-service:latest 2>nul

echo.
echo [2/4] 构建Docker镜像（使用国内镜像源）...
docker build -t mahjong-service:latest .

if %errorlevel% neq 0 (
    echo 构建失败！请检查Dockerfile配置
    pause
    exit /b 1
)

echo.
echo [3/4] 启动容器...
docker run -d -p 8080:8080 --name mahjong-service mahjong-service:latest

if %errorlevel% neq 0 (
    echo 启动失败！请检查端口8080是否被占用
    pause
    exit /b 1
)

echo.
echo [4/4] 等待服务启动...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 服务启动完成！
echo ========================================
echo 访问地址: http://localhost:8080
echo 容器状态: 
docker ps --filter name=mahjong-service
echo.
echo 查看日志: docker logs mahjong-service
echo 停止服务: docker stop mahjong-service
echo 删除容器: docker rm mahjong-service
echo ========================================

echo.
echo 按任意键打开浏览器测试服务...
pause >nul
start http://localhost:8080
