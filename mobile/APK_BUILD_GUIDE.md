# 📱 WanderFlow APK 打包完整指南

## 📋 目录
- [环境准备](#环境准备)
- [项目初始化](#项目初始化)
- [API配置修改](#api配置修改)
- [打包APK](#打包apk)
- [常见问题解决](#常见问题解决)

---

## 🔧 环境准备

### 1. 安装 Flutter SDK

#### Windows 系统：

1. **下载 Flutter SDK**
   ```powershell
   # 访问官网下载最新稳定版
   # https://docs.flutter.dev/get-started/install/windows
   ```

2. **解压到指定目录**（建议路径不包含空格和中文）
   ```
   C:\flutter
   ```

3. **配置环境变量**
   - 打开"系统属性" → "高级" → "环境变量"
   - 在"系统变量"中找到 `Path`，点击"编辑"
   - 添加：`C:\flutter\bin`

4. **验证安装**
   ```powershell
   flutter --version
   flutter doctor
   ```

### 2. 安装 Android Studio

1. **下载安装 Android Studio**
   - 官网：https://developer.android.com/studio
   - 下载最新稳定版（建议 2022.1 以上）

2. **安装 Android SDK**
   - 打开 Android Studio
   - Tools → SDK Manager
   - 安装以下组件：
     - ✅ Android SDK Platform 33 (Android 13.0)
     - ✅ Android SDK Build-Tools
     - ✅ Android SDK Command-line Tools
     - ✅ Android Emulator（可选，用于测试）

3. **配置环境变量**
   - 添加 `ANDROID_HOME` 环境变量：
     ```
     C:\Users\你的用户名\AppData\Local\Android\Sdk
     ```
   - 在 `Path` 中添加：
     ```
     %ANDROID_HOME%\platform-tools
     %ANDROID_HOME%\cmdline-tools\latest\bin
     ```

### 3. 安装 Java JDK

1. **下载 JDK 17**（Flutter 推荐）
   - Oracle JDK: https://www.oracle.com/java/technologies/downloads/
   - 或使用 OpenJDK

2. **配置环境变量**
   - 添加 `JAVA_HOME`：
     ```
     C:\Program Files\Java\jdk-17
     ```
   - 在 `Path` 中添加：
     ```
     %JAVA_HOME%\bin
     ```

3. **验证安装**
   ```powershell
   java -version
   ```

### 4. 运行 Flutter Doctor

```powershell
flutter doctor
```

**期望输出（全部打勾✓）：**
```
[✓] Flutter (Channel stable, 3.x.x)
[✓] Android toolchain - develop for Android devices (Android SDK version 33.0.0)
[✓] Chrome - develop for the web
[✓] Android Studio (version 2022.1)
[✓] VS Code (version 1.x.x)
[✓] Connected device (1 available)
```

如果有 [!] 或 [✗]，按提示修复。

---

## 🚀 项目初始化

### 1. 检查项目结构

确认你的Flutter项目有以下结构：

```
mobile/flutter/
├── android/           # Android配置（重要！）
├── lib/              # Dart源代码
├── pubspec.yaml      # 依赖配置
└── web/              # Web构建目录
```

### 2. 创建完整的Flutter项目

如果 `android/` 文件夹不存在，需要重新初始化：

```powershell
cd C:\Users\17182\Desktop\wanderflow_secp\AI_Travel_Planner_Pro\mobile

# 方案1：创建新项目（保留现有代码）
flutter create flutter_new
# 将 flutter_new/android 文件夹复制到 flutter/ 目录

# 方案2：直接在现有项目中创建平台文件
cd flutter
flutter create --platforms=android .
```

### 3. 安装依赖

```powershell
cd C:\Users\17182\Desktop\wanderflow_secp\AI_Travel_Planner_Pro\mobile\flutter
flutter pub get
```

---

## 🔌 API配置修改

### 问题1：本地API无法访问

在手机上运行时，`localhost` 或 `127.0.0.1` 无法访问电脑的后端服务。

### 解决方案

#### 方案A：使用电脑局域网IP（推荐用于开发测试）

1. **获取电脑IP**
   ```powershell
   ipconfig
   # 找到 "无线局域网适配器 WLAN" 或 "以太网适配器"
   # 记录 IPv4 地址，例如：192.168.1.100
   ```

2. **修改Flutter API配置**

创建配置文件 `lib/config/api_config.dart`：

```dart
class ApiConfig {
  // 开发环境：使用局域网IP
  static const String DEV_BASE_URL = 'http://192.168.1.100:8001';
  
  // 生产环境：使用云服务器地址
  static const String PROD_BASE_URL = 'https://your-domain.com';
  
  // 当前使用的URL（根据环境切换）
  static const String BASE_URL = DEV_BASE_URL;
  
  // API端点
  static const String API_PREFIX = '/api/v1';
  
  // 完整API地址
  static String get apiUrl => '$BASE_URL$API_PREFIX';
}
```

3. **更新网络请求代码**

在 `lib/services/api_service.dart` 中使用配置：

```dart
import 'package:dio/dio.dart';
import '../config/api_config.dart';

class ApiService {
  late Dio dio;

  ApiService() {
    dio = Dio(BaseOptions(
      baseUrl: ApiConfig.apiUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
      },
    ));
  }
}
```

#### 方案B：部署到云服务器（推荐用于生产）

1. 将后端部署到阿里云/腾讯云/AWS
2. 获取公网域名（如 `https://api.wanderflow.com`）
3. 在 `ApiConfig` 中设置 `PROD_BASE_URL`

### 问题2：跨域问题

Flutter原生应用**不存在跨域问题**（这是浏览器的限制），所以无需担心CORS配置。

### 问题3：HTTPS证书问题

如果后端使用自签名证书，需要在开发时忽略证书验证：

```dart
// 仅用于开发环境！生产环境必须使用有效证书
class ApiService {
  ApiService() {
    dio = Dio(BaseOptions(
      baseUrl: ApiConfig.apiUrl,
    ));
    
    // 开发环境忽略证书验证
    if (ApiConfig.BASE_URL == ApiConfig.DEV_BASE_URL) {
      (dio.httpClientAdapter as DefaultHttpClientAdapter).onHttpClientCreate = 
        (client) {
          client.badCertificateCallback = 
            (X509Certificate cert, String host, int port) => true;
          return client;
        };
    }
  }
}
```

---

## 📦 打包APK

### 1. 配置应用信息

#### 修改 `android/app/build.gradle`

```gradle
android {
    namespace "com.wanderflow.app"
    compileSdk 34
    
    defaultConfig {
        applicationId "com.wanderflow.app"  // 应用唯一标识
        minSdk 21                           // 最低支持Android 5.0
        targetSdk 34                        // 目标Android版本
        versionCode 1                       // 版本号（整数）
        versionName "1.0.0"                 // 版本名称
    }
}
```

#### 修改应用名称 `android/app/src/main/AndroidManifest.xml`

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:label="WanderFlow"           <!-- 应用显示名称 -->
        android:icon="@mipmap/ic_launcher">  <!-- 应用图标 -->
    </application>
    
    <!-- 添加网络权限 -->
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
</manifest>
```

### 2. 生成应用图标（可选）

1. 准备一张 1024x1024 的PNG图标
2. 使用在线工具生成各尺寸图标：
   - https://icon.kitchen/
   - https://romannurik.github.io/AndroidAssetStudio/

3. 将生成的图标文件放入：
   ```
   android/app/src/main/res/
   ├── mipmap-hdpi/ic_launcher.png
   ├── mipmap-mdpi/ic_launcher.png
   ├── mipmap-xhdpi/ic_launcher.png
   ├── mipmap-xxhdpi/ic_launcher.png
   └── mipmap-xxxhdpi/ic_launcher.png
   ```

### 3. 打包Debug APK（用于测试）

```powershell
cd C:\Users\17182\Desktop\wanderflow_secp\AI_Travel_Planner_Pro\mobile\flutter

# 打包Debug版本（快速，体积大）
flutter build apk --debug
```

**生成位置：**
```
build/app/outputs/flutter-apk/app-debug.apk
```

### 4. 打包Release APK（用于发布）

#### 步骤1：配置签名密钥

1. **生成密钥文件**
   ```powershell
   cd C:\Users\17182\Desktop\wanderflow_secp\AI_Travel_Planner_Pro\mobile\flutter\android

   # 使用 keytool 生成密钥（JDK自带工具）
   keytool -genkey -v -keystore wanderflow-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias wanderflow
   
   # 按提示输入：
   # - 密钥库口令：输入密码（记住！）
   # - 再次输入：重复密码
   # - 姓名：你的名字
   # - 组织单位：你的公司/团队
   # - 组织：公司名称
   # - 城市：城市名
   # - 省份：省份名
   # - 国家代码：CN
   # - 密钥口令：直接回车（使用相同密码）
   ```

2. **创建密钥配置文件**

在 `android/key.properties` 创建文件：

```properties
storePassword=你的密钥库口令
keyPassword=你的密钥口令
keyAlias=wanderflow
storeFile=wanderflow-key.jks
```

**⚠️ 重要：将 `key.properties` 和 `*.jks` 添加到 `.gitignore`**

3. **修改 `android/app/build.gradle`**

在文件顶部添加：

```gradle
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    // ... 现有配置
    
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            shrinkResources true
        }
    }
}
```

#### 步骤2：执行打包

```powershell
cd C:\Users\17182\Desktop\wanderflow_secp\AI_Travel_Planner_Pro\mobile\flutter

# 打包Release版本（优化，体积小）
flutter build apk --release

# 或者生成分包APK（不同CPU架构）
flutter build apk --split-per-abi
```

**生成位置：**
```
build/app/outputs/flutter-apk/
├── app-release.apk           # 通用APK（约40-50MB）
├── app-armeabi-v7a-release.apk   # ARM 32位（约20MB）
├── app-arm64-v8a-release.apk     # ARM 64位（约25MB）推荐
└── app-x86_64-release.apk        # x86 64位（约25MB）
```

### 5. 打包App Bundle（Google Play发布）

```powershell
flutter build appbundle --release
```

生成文件：`build/app/outputs/bundle/release/app-release.aab`

---

## 📲 安装测试

### 方法1：USB连接真机

1. **开启手机开发者模式**
   - 设置 → 关于手机 → 连续点击"版本号"7次
   - 返回设置 → 开发者选项 → 开启"USB调试"

2. **连接手机并安装**
   ```powershell
   # 检测设备
   flutter devices
   
   # 直接安装运行
   flutter run --release
   
   # 或手动安装APK
   adb install build/app/outputs/flutter-apk/app-release.apk
   ```

### 方法2：通过文件传输

1. 将APK文件复制到手机
2. 在手机上点击安装（需允许"未知来源安装"）

---

## 🛠 常见问题解决

### 问题1：Flutter Doctor 显示错误

**Android license not accepted**
```powershell
flutter doctor --android-licenses
# 一路输入 y 接受协议
```

**cmdline-tools component is missing**
```powershell
# 打开 Android Studio → SDK Manager
# 勾选 "Android SDK Command-line Tools"
```

### 问题2：Gradle下载慢

**修改镜像源：**

在 `android/build.gradle` 中：

```gradle
buildscript {
    repositories {
        // 替换为阿里云镜像
        maven { url 'https://maven.aliyun.com/repository/google' }
        maven { url 'https://maven.aliyun.com/repository/public' }
        google()
        mavenCentral()
    }
}

allprojects {
    repositories {
        maven { url 'https://maven.aliyun.com/repository/google' }
        maven { url 'https://maven.aliyun.com/repository/public' }
        google()
        mavenCentral()
    }
}
```

### 问题3：API连接超时

1. **检查后端是否运行**
   ```powershell
   # 在浏览器访问
   http://你的IP:8001/docs
   ```

2. **检查防火墙**
   - Windows防火墙允许8001端口
   - 路由器允许局域网访问

3. **确认手机和电脑在同一网络**
   - 都连接相同的WiFi

### 问题4：打包失败 - Java版本问题

```
Unsupported class file major version 61
```

**解决：** 使用 JDK 17

```powershell
java -version
# 应显示 "17.0.x"
```

### 问题5：签名错误

```
INSTALL_PARSE_FAILED_NO_CERTIFICATES
```

**解决：** 检查 `key.properties` 配置是否正确

---

## 📋 快速命令参考

```powershell
# 查看设备
flutter devices

# 清理构建缓存
flutter clean

# 重新获取依赖
flutter pub get

# 运行开发版本
flutter run

# 打包Debug APK
flutter build apk --debug

# 打包Release APK
flutter build apk --release

# 打包分架构APK
flutter build apk --split-per-abi

# 查看APK大小分析
flutter build apk --analyze-size

# 安装APK到设备
adb install app-release.apk

# 查看日志
flutter logs
```

---

## 🎯 生产发布检查清单

- [ ] API地址改为生产服务器
- [ ] 移除所有调试代码（print语句）
- [ ] 测试所有功能正常
- [ ] 更新版本号（versionCode和versionName）
- [ ] 生成签名APK
- [ ] 测试安装和运行
- [ ] 准备应用截图和描述
- [ ] 上传到应用商店

---

## 🔗 参考资料

- [Flutter官方文档](https://docs.flutter.dev/)
- [Android开发者文档](https://developer.android.com/)
- [Flutter中国镜像](https://flutter.cn/)

---

## 💡 下一步

完成APK打包后，你可以：

1. ✅ 在真机上测试所有功能
2. ✅ 收集用户反馈优化体验
3. ✅ 准备上架应用商店（Google Play、华为应用市场等）
4. ✅ 配置自动化CI/CD流程

如有问题，参考本文档或查看项目的 `FLUTTER_GUIDE.md` 了解更多详情。
