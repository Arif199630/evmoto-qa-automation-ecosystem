# Mobile Application Packages (APKs) & Build Specifications

Folder ini mendokumentasikan spesifikasi teknis dan artefak APK yang digunakan dalam pengujian otomasi ekosistem **eVMOTO & ECGO**.

> ⚠️ **Catatan Ukuran File (GitHub 100MB Limit):**
> File binary `.apk` tidak disimpan langsung di Git repository untuk mematuhi kebijakan batas ukuran file GitHub (khususnya `ECGO SuperApps.apk` yang berukuran 146 MB). Seluruh APK dapat diunduh langsung melalui **GitHub Releases** atau repositori penyimpanan build resmi.

---

## 📱 Daftar Paket Aplikasi Teruji

| Aplikasi | Nama File Build | Versi | Package Name | Ukuran | Status Verifikasi |
| :--- | :--- | :---: | :--- | :---: | :---: |
| **EvMoto User** | `evmoto-user-1.2.33-env-dev_golang-20261020-v8a.apk` | `1.2.33` | `com.evmoto.user.app` | 28.2 MB | ✅ Verified (257 TC) |
| **EvMoto Driver** | `evmoto-driver-1.9.27-env-dev_golang-20261020-v7a.apk` | `1.9.27` | `com.evmoto.driver.app` | 28.9 MB | ✅ Verified (339 TC) |
| **ECGO SuperApps** | `ECGO SuperApps.apk` | `Latest` | `pk.krave.flutter_app` | 146.0 MB | ✅ Verified (Interkoneksi) |

---

## 🔑 Desired Capabilities Template (Appium)

### 1. Driver App:
```json
{
  "platformName": "Android",
  "appium:automationName": "UiAutomator2",
  "appium:deviceName": "Medium_Phone_API_37.0",
  "appium:appPackage": "com.evmoto.driver.app",
  "appium:appActivity": "com.evmoto.driver.app.MainActivity",
  "appium:noReset": false
}
```

### 2. User App:
```json
{
  "platformName": "Android",
  "appium:automationName": "UiAutomator2",
  "appium:deviceName": "Medium_Phone_API_37.0",
  "appium:appPackage": "com.evmoto.user.app",
  "appium:appActivity": "com.evmoto.user.app.MainActivity",
  "appium:noReset": false
}
```
