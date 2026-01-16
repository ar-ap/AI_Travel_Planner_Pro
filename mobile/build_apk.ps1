# 📱 WanderFlow APK 快速打包脚本

Write-Host "🚀 WanderFlow APK 打包工具" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

$projectRoot = "C:\Users\17182\Desktop\wanderflow_secp\AI_Travel_Planner_Pro\mobile\flutter"

# 检查Flutter是否安装
Write-Host "📋 步骤 1/5: 检查环境..." -ForegroundColor Yellow
try {
    $flutterVersion = flutter --version 2>&1 | Select-String "Flutter"
    Write-Host "  ✅ Flutter已安装: $flutterVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Flutter未安装！请先安装Flutter SDK" -ForegroundColor Red
    Write-Host "  💡 参考文档: mobile\APK_BUILD_GUIDE.md" -ForegroundColor Yellow
    exit 1
}

# 检查项目是否存在
if (-not (Test-Path $projectRoot)) {
    Write-Host "  ❌ 项目目录不存在: $projectRoot" -ForegroundColor Red
    exit 1
}

Write-Host "  ✅ 项目目录存在`n" -ForegroundColor Green

# 进入项目目录
Set-Location $projectRoot

# 询问打包类型
Write-Host "📦 步骤 2/5: 选择打包类型..." -ForegroundColor Yellow
Write-Host "  1. Debug APK (快速测试，体积大)" -ForegroundColor White
Write-Host "  2. Release APK (优化版本，需要签名)" -ForegroundColor White
Write-Host "  3. Release APK 分架构 (推荐，体积小)`n" -ForegroundColor White

$choice = Read-Host "请选择 (1/2/3)"

# 清理缓存
Write-Host "`n🧹 步骤 3/5: 清理构建缓存..." -ForegroundColor Yellow
flutter clean
Write-Host "  ✅ 缓存已清理`n" -ForegroundColor Green

# 获取依赖
Write-Host "📦 步骤 4/5: 安装依赖..." -ForegroundColor Yellow
flutter pub get
Write-Host "  ✅ 依赖安装完成`n" -ForegroundColor Green

# 执行打包
Write-Host "🔨 步骤 5/5: 开始打包APK..." -ForegroundColor Yellow

switch ($choice) {
    "1" {
        Write-Host "  打包 Debug APK..." -ForegroundColor Cyan
        flutter build apk --debug
        $apkPath = "build\app\outputs\flutter-apk\app-debug.apk"
    }
    "2" {
        Write-Host "  打包 Release APK..." -ForegroundColor Cyan
        flutter build apk --release
        $apkPath = "build\app\outputs\flutter-apk\app-release.apk"
    }
    "3" {
        Write-Host "  打包 Release APK (分架构)..." -ForegroundColor Cyan
        flutter build apk --split-per-abi
        $apkPath = "build\app\outputs\flutter-apk"
    }
    default {
        Write-Host "  ❌ 无效选择！" -ForegroundColor Red
        exit 1
    }
}

# 检查是否成功
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ APK打包成功！" -ForegroundColor Green
    Write-Host "================================`n" -ForegroundColor Cyan
    Write-Host "📂 APK位置: $apkPath" -ForegroundColor Yellow
    Write-Host "`n🎯 下一步:" -ForegroundColor Cyan
    Write-Host "  1. 将APK复制到手机" -ForegroundColor White
    Write-Host "  2. 在手机上点击安装" -ForegroundColor White
    Write-Host "  3. 允许'未知来源安装'" -ForegroundColor White
    Write-Host "`n💡 提示:" -ForegroundColor Cyan
    Write-Host "  - 手机需开启'开发者模式'并允许'USB调试'" -ForegroundColor White
    Write-Host "  - 确保后端服务正在运行: http://你的IP:8001" -ForegroundColor White
    Write-Host "  - 修改 lib/config/api_config.dart 中的IP地址`n" -ForegroundColor White
    
    # 询问是否打开文件夹
    $open = Read-Host "是否打开APK所在文件夹? (Y/N)"
    if ($open -eq "Y" -or $open -eq "y") {
        explorer.exe "$projectRoot\build\app\outputs\flutter-apk"
    }
} else {
    Write-Host "`n❌ 打包失败！" -ForegroundColor Red
    Write-Host "💡 常见问题:" -ForegroundColor Yellow
    Write-Host "  1. Java版本不对 → 需要JDK 17" -ForegroundColor White
    Write-Host "  2. Gradle下载慢 → 配置镜像源" -ForegroundColor White
    Write-Host "  3. 缺少Android SDK → 安装Android Studio" -ForegroundColor White
    Write-Host "`n📖 详细文档: mobile\APK_BUILD_GUIDE.md`n" -ForegroundColor Yellow
}

Read-Host "按回车键退出"
