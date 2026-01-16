# 🚀 WanderFlow APK打包 - 快速参考

## 一键配置和打包

### 1️⃣ 配置API地址（自动获取IP）
```powershell
cd C:\Users\17182\Desktop\wanderflow_secp\AI_Travel_Planner_Pro\mobile
.\config_api.ps1
```
- 自动检测电脑IP
- 更新Flutter配置
- 检查后端状态

### 2️⃣ 打包APK
```powershell
cd C:\Users\17182\Desktop\wanderflow_secp\AI_Travel_Planner_Pro\mobile
.\build_apk.ps1
```
- 选择打包类型（Debug/Release）
- 自动清理缓存
- 一键生成APK

---

## 手动命令参考

### 快速测试
```powershell
cd mobile/flutter
flutter run --release
```

### 打包Debug版（快速测试）
```powershell
flutter build apk --debug
# 输出: build/app/outputs/flutter-apk/app-debug.apk
```

### 打包Release版（发布）
```powershell
flutter build apk --release --split-per-abi
# 输出: 
# - app-arm64-v8a-release.apk (推荐，约25MB)
# - app-armeabi-v7a-release.apk (兼容老设备)
```

### 安装到手机
```powershell
# USB连接手机后
adb install build/app/outputs/flutter-apk/app-release.apk
```

---

## 📋 环境检查

```powershell
# 检查Flutter环境
flutter doctor

# 检查连接的设备
flutter devices

# 检查电脑IP
ipconfig

# 测试后端连接
curl http://你的IP:8001/docs
```

---

## ⚙️ 关键配置文件

| 文件 | 作用 |
|------|------|
| `lib/config/api_config.dart` | API地址配置 |
| `android/app/build.gradle` | 应用信息、版本号 |
| `android/app/src/main/AndroidManifest.xml` | 应用名称、权限 |
| `android/key.properties` | 签名密钥配置 |

---

## 🐛 常见问题

### 问题1：API连接不上
```dart
// 修改 lib/config/api_config.dart
static const String DEV_BASE_URL = 'http://你的IP:8001';
```

### 问题2：Gradle下载慢
```gradle
// 修改 android/build.gradle
maven { url 'https://maven.aliyun.com/repository/google' }
```

### 问题3：签名失败
```powershell
# 重新生成密钥
cd android
keytool -genkey -v -keystore wanderflow-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias wanderflow
```

### 问题4：后端无法访问
- 确保后端监听 `0.0.0.0:8001` 而非 `127.0.0.1:8001`
- 检查防火墙允许8001端口
- 手机和电脑在同一WiFi

---

## 📱 测试步骤

1. **启动后端**
   ```powershell
   cd backend
   .\venv\Scripts\python.exe .\app.py
   ```

2. **验证后端**
   ```
   浏览器访问: http://你的IP:8001/docs
   ```

3. **配置API**
   ```powershell
   .\config_api.ps1
   ```

4. **打包APK**
   ```powershell
   .\build_apk.ps1
   ```

5. **安装测试**
   - 将APK传到手机
   - 允许未知来源安装
   - 打开应用测试

---

## 🎯 发布前检查

- [ ] API地址改为生产服务器
- [ ] 移除所有调试代码
- [ ] 更新版本号（build.gradle）
- [ ] 生成签名Release APK
- [ ] 在真机测试所有功能
- [ ] 准备应用图标（1024x1024）
- [ ] 准备应用截图（至少4张）
- [ ] 编写应用描述和更新说明

---

## 📚 详细文档

完整指南请参考：
- `APK_BUILD_GUIDE.md` - 详细打包教程
- `FLUTTER_GUIDE.md` - Flutter开发指南
- `backend/.env` - 后端配置

---

## 💡 快捷键

| 命令 | 说明 |
|------|------|
| `flutter clean` | 清理缓存 |
| `flutter pub get` | 安装依赖 |
| `flutter run` | 运行开发版 |
| `flutter build apk` | 打包APK |
| `flutter doctor` | 环境检查 |
| `adb devices` | 查看设备 |

---

**需要帮助？** 查看完整文档 `APK_BUILD_GUIDE.md` 或项目README
