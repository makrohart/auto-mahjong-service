# 麻将AI识别服务 - 本地构建和测试脚本 (PowerShell版本)

Write-Host "========================================" -ForegroundColor Green
Write-Host "麻将AI识别服务 - 本地构建和测试脚本" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`n[1/4] 清理旧的容器和镜像..." -ForegroundColor Yellow
docker stop mahjong-service 2>$null
docker rm mahjong-service 2>$null
docker rmi mahjong-service:latest 2>$null

Write-Host "`n[2/4] 构建Docker镜像（使用国内镜像源）..." -ForegroundColor Yellow
docker build -t mahjong-service:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "构建失败！请检查Dockerfile配置" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "`n[3/4] 启动容器..." -ForegroundColor Yellow
docker run -d -p 8080:8080 --name mahjong-service mahjong-service:latest

if ($LASTEXITCODE -ne 0) {
    Write-Host "启动失败！请检查端口8080是否被占用" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "`n[4/4] 等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "服务启动完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "访问地址: http://localhost:8080" -ForegroundColor Cyan
Write-Host "容器状态:" -ForegroundColor Cyan
docker ps --filter name=mahjong-service
Write-Host "`n查看日志: docker logs mahjong-service" -ForegroundColor Gray
Write-Host "停止服务: docker stop mahjong-service" -ForegroundColor Gray
Write-Host "删除容器: docker rm mahjong-service" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Green

Write-Host "`n按任意键打开浏览器测试服务..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Start-Process "http://localhost:8080"
