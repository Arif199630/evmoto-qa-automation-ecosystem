# APK yang diuji

| Aplikasi | Package | Sumber di CI |
|---|---|---|
| EvMoto User (dev) | `com.evmoto.user.app` | Release `apk-dev`, file `evmoto-apk-dev.tar.gz.enc` → `evmoto-user.apk` |
| EvMoto Driver (dev) | `com.evmoto.driver.app` | Release `apk-dev`, file `evmoto-apk-dev.tar.gz.enc` → `evmoto-driver.apk` |

File `.apk` tidak di-commit. Di Release, kedua APK dikemas dalam satu arsip terenkripsi AES-256; workflow membukanya dengan secret `APK_PASSPHRASE`.

Mengganti APK dengan build baru:

```bash
tar -czf evmoto-apk-dev.tar.gz evmoto-user.apk evmoto-driver.apk
openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt -pass env:APK_PASSPHRASE -in evmoto-apk-dev.tar.gz -out evmoto-apk-dev.tar.gz.enc
gh release upload apk-dev evmoto-apk-dev.tar.gz.enc --clobber
```
