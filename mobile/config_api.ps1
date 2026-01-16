# 🌐 API配置助手 - 自动获取并配置局域网IP

Write-Host "🌐 WanderFlow API配置助手" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# 获取本机局域网IP
Write-Host "🔍 正在获取本机IP地址..." -ForegroundColor Yellow

$ipAddresses = Get-NetIPAddress -AddressFamily IPv4 | 
    Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.*" } |
    Select-Object IPAddress, InterfaceAlias

if ($ipAddresses.Count -eq 0) {
    Write-Host "❌ 未找到可用的IP地址！" -ForegroundColor Red
    Write-Host "💡 请检查网络连接" -ForegroundColor Yellow
    Read-Host "`n按回车键退出"
    exit 1
}

Write-Host "`n📍 找到以下IP地址:`n" -ForegroundColor Green

for ($i = 0; $i -lt $ipAddresses.Count; $i++) {
    $ip = $ipAddresses[$i]
    Write-Host "  $($i + 1). $($ip.IPAddress) ($($ip.InterfaceAlias))" -ForegroundColor White
}

# 选择IP
$selection = 1
if ($ipAddresses.Count -gt 1) {
    Write-Host ""
    $selection = Read-Host "请选择要使用的IP (1-$($ipAddresses.Count))"
    if ([int]$selection -lt 1 -or [int]$selection -gt $ipAddresses.Count) {
        Write-Host "❌ 无效选择！" -ForegroundColor Red
        Read-Host "`n按回车键退出"
        exit 1
    }
}

$selectedIP = $ipAddresses[[int]$selection - 1].IPAddress
Write-Host "`n✅ 已选择IP: $selectedIP" -ForegroundColor Green

# 更新配置文件
$configPath = "C:\Users\17182\Desktop\wanderflow_secp\AI_Travel_Planner_Pro\mobile\flutter\lib\config\api_config.dart"

if (-not (Test-Path $configPath)) {
    Write-Host "❌ 配置文件不存在: $configPath" -ForegroundColor Red
    Read-Host "`n按回车键退出"
    exit 1
}

Write-Host "`n📝 正在更新配置文件..." -ForegroundColor Yellow

$content = Get-Content $configPath -Raw
$newContent = $content -replace "http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:8001", "http://${selectedIP}:8001"

Set-Content -Path $configPath -Value $newContent -Encoding UTF8

Write-Host "✅ 配置文件已更新！`n" -ForegroundColor Green

# 显示完整配置信息
Write-Host "================================" -ForegroundColor Cyan
Write-Host "📋 当前配置信息:" -ForegroundColor Yellow
Write-Host "  - 后端地址: http://${selectedIP}:8001" -ForegroundColor White
Write-Host "  - API端点: http://${selectedIP}:8001/api/v1" -ForegroundColor White
Write-Host "  - API文档: http://${selectedIP}:8001/docs`n" -ForegroundColor White

# 检查后端是否运行
Write-Host "🔍 检查后端服务..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://${selectedIP}:8001/" -Method GET -TimeoutSec 3
    Write-Host "✅ 后端服务正常运行！" -ForegroundColor Green
} catch {
    Write-Host "⚠️  无法连接到后端服务" -ForegroundColor Yellow
    Write-Host "💡 请确保:" -ForegroundColor Cyan
    Write-Host "  1. 后端服务正在运行 (python app.py)" -ForegroundColor White
    Write-Host "  2. 后端监听在 0.0.0.0:8001 而不是 127.0.0.1:8001" -ForegroundColor White
    Write-Host "  3. 防火墙允许8001端口访问`n" -ForegroundColor White
}

Write-Host "================================" -ForegroundColor Cyan
Write-Host "🎯 下一步操作:" -ForegroundColor Cyan
Write-Host "  1. 启动后端: cd backend && python app.py" -ForegroundColor White
Write-Host "  2. 手机连接同一WiFi" -ForegroundColor White
Write-Host "  3. 运行打包脚本: .\build_apk.ps1" -ForegroundColor White
Write-Host "  4. 或直接运行: flutter run`n" -ForegroundColor White

# 询问是否启动后端
$startBackend = Read-Host "是否启动后端服务? (Y/N)"
if ($startBackend -eq "Y" -or $startBackend -eq "y") {
    Write-Host "`n🚀 正在启动后端..." -ForegroundColor Yellow
    $backendPath = "C:\Users\17182\Desktop\wanderflow_secp\AI_Travel_Planner_Pro\backend"
    
    # 在新窗口启动后端
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; .\venv\Scripts\python.exe .\app.py"
    Write-Host "✅ 后端服务已在新窗口启动" -ForegroundColor Green
}

Write-Host "`n✨ 配置完成！" -ForegroundColor Green
Read-Host "`n按回车键退出"
