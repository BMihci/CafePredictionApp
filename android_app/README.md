# 📱 Kingfool Inc. | Native Android Mobil Uygulaması

Bu klasör, Kingfool Inc. kafe talep tahmin sisteminin **Native Android (Kotlin + Jetpack Compose)** mobil uygulamasını içerir.

---

## 🎨 Tasarım & Özellikler

- **Galatasaray Renk Paleti:** `#A6192E` (Kırmızı) ve `#FDB913` (Sarı) odaklı Dark Mode arayüz.
- **Kullanıcı Girişi:** `ornekkafe`, `limon` veya `admin` kullanıcıları ile giriş yapma.
- **Canlı Hava Durumu:** Otomatik sıcaklık verisi (`Open-Meteo`).
- **Ürünler & Günlük Satış Girişi:** Tek dokunuşla ürün seçip günün satış miktarını bulut veritabanına gönderme.
- **Yapay Zeka Tahmini:** Telefondan tek tıkla Python backend API'sindeki `RandomForestRegressor + Feature Engineering` modelini tetikleyerek yarının talep tahminini alma.

---

## 🚀 Android Studio ile Çalıştırma Adımları

1. **Android Studio** programını açın.
2. **Open** diyerek bu klasörü seçin: `android_app`
3. Gradle senkronizasyonunun tamamlanmasını bekleyin.
4. **Çalıştırma (Run):**
   - **Emülatörde çalıştırıyorsanız:** Giriş ekranında API URL varsayılan olarak `http://10.0.2.2:8000/` gelir (bilgisayarın localhost'una bağlanır).
   - **Gerçek telefonunuzda çalıştırıyorsanız:** Telefonunuz ve bilgisayarınız aynı Wi-Fi ağına bağlıyken bilgisayarınızın yerel IP adresini yazın:
     Örnek: `http://192.168.1.35:8000/`

---

## 🐍 Python API Backend'ini Başlatma

Android uygulamasının tahmin ve veri alabilmesi için bilgisayarınızda FastAPI servisini başlatın:

```powershell
cd CafePredictionApp
python api/main.py
```

API başladığında Swagger test arayüzüne tarayıcınızdan erişebilirsiniz:
`http://localhost:8000/docs`
