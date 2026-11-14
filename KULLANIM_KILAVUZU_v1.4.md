# 🃏 Kingfool Inc. v1.4 | Tam Sistem & Kullanım Kılavuzu

Kingfool Inc., modern kafe işletmeleri için geliştirilmiş; **yapay zeka destekli talep tahmini, otomatik model eğitimi (MLOps), hammadde envanter optimizasyonu, F&B Menü Mühendisliği kâr matrisi, resmi tatil/etkinlik takvimi ve LLM işletme koçluğu bültenini** tek bir çatı altında toplayan uçtan uca akıllı bir kafe yönetim platformudur.

---

## 🏛️ 1. Mimari Genel Bakış

Platform 4 ana katmandan oluşmaktadır:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        KULLANICI ARAYÜZLERİ                            │
│  Masaüstü Uygulaması (dist/app.exe)  │  Native Android Uygulaması      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST
┌───────────────────────────────────▼────────────────────────────────────┐
│                    MERKEZİ REST API (FastAPI v1.4)                     │
│  /api/predict      /api/sales        /api/coaching/daily-report        │
│  /api/inventory/*  /api/calendar/*   /api/menu-engineering/*           │
└───────────────────┬───────────────────────────────┬────────────────────┘
                    │                               │
┌───────────────────▼──────────────────┐ ┌──────────▼────────────────────┐
│      BULUT VERİTABANI (Supabase)     │ │        ZEKA & MOTORLAR        │
│  - kullanicilar (Auth, roller, ürün) │ │  - MLOps Pipeline (RandomF.) │
│  - urunler (Reçeteler & birimler)    │ │  - Menü Mühendisliği (BCG)   │
│  - satislar (Zaman serisi geçmişi)   │ │  - Envanter & Sarfiyat Hesabı │
│  - Yerel Fallback: Excel & JSON      │ │  - Gemini & Kural Tabanlı LLM │
└──────────────────────────────────────┘ └───────────────────────────────┘
```

---

## 🚀 2. Nasıl Başlatılır? (Kısayollar)

Masaüstünüzde hazır iki kısayol bulunmaktadır:

1. **`Kingfool Inc.` Kısayolu:**
   - Masaüstü uygulamasını (`dist/app.exe`) başlatır.
   - İnternet olmasa dahi yerel Excel ve çevrimdışı yapay zeka motoruyla kesintisiz çalışır.
2. **`Kingfool API` Kısayolu:**
   - FastAPI REST API sunucusunu `http://localhost:8000` adresinde ayağa kaldırır.
   - Android mobil uygulamasının ve harici entegrasyonların veri alışverişini sağlar.
   - Swagger Arayüzü: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 👥 3. Kullanıcı Hesapları ve Rolleri

| Kullanıcı Adı | Şifre | Rol | Açıklama |
| :--- | :--- | :--- | :--- |
| **admin** | `admin1234` | **Yönetici** | Tüm sistemi yönetir, kullanıcı ekler/siler, şifre değiştirir, kafe paneline erişir. |
| **ornekkafe** | `kafe1234` | **Kullanıcı** | Standart kafe kullanıcısı. Kendi ürünlerini ve satışlarını yönetir. |

*(Yeni kullanıcılar admin paneli üzerinden anında eklenebilir. Eklenen her kullanıcı Supabase bulut veritabanına anında senkronize olur.)*

---

## 📋 4. Günlük Kafe İş Akışı (Step-by-Step)

### A. Sabah Açılışı (08:00 - 09:00)
1. **Kingfool Inc.** uygulamasını açıp giriş yapın.
2. Hava durumu ve tatil rozetini kontrol edin (Örn: *📍 Kadıköy \| Bugün: 25°C \| Yarın: 26°C \| 🎉 Cumhuriyet Bayramı*).
3. **"Tahminleri Hesapla"** butonuna basarak yarın hangi üründen kaç bardak satılacağını görün.
4. **"📦 Yarınki Hammadde İhtiyacı"** satırını inceleyin: Baristalarınızın kaç kg çekirdek öğütmesi, kaç litre taze süt ve kaç adet bardak hazırlaması gerektiği ekranda özetlenir.
5. **"🧠 Akıllı İşletme Koçu Günlük Bülteni (Oku)"** butonuna tıklayın:
   - Günün beklenen cirosunu, operasyonel barista hazırlıklarını ve Menü Mühendisliği'nin önerdiği **Günün Upsell Fırsatını** okuyun.
   - İsterseniz **"📋 Panoya Kopyala"** diyerek bülteni kafe WhatsApp grubuna gönderin.

### B. Gün İçinde Menü ve Fiyat Takibi
- **"📊 Menü Mühendisliği ve Kâr Matrisi"** butonuna tıklayın:
  - Ürünlerinizin hammadde maliyetlerini (COGS) ve kâr marjlarını (%) görün.
  - Hangi ürünün kasanızı besleyen **Yıldız**, hangisinin satış ekibiyle desteklenmesi gereken **Bulmaca** olduğunu inceleyin.
  - İhtiyaç halinde tablonun altındaki kutucuktan satış fiyatını güncelleyip anında yeni kâr projeksiyonunu test edin.

### C. Gün Sonu Kapanışı (22:00 - 23:00)
1. **"2. GÜN SONU SATIŞ GİRİŞİ"** kartına gelin.
2. Gün içinde kasada kesilen fişlere göre 4 ürünün gerçekleşen net satış adetlerini girin.
3. Bugün kampanya veya özel indirim uygulandıysa *"Bugün özel indirim/promosyon uygulandı"* kutucuğunu işaretleyin.
4. **"💾 Günlük Satışları Kaydet & Yapay Zekayı Güncelle"** butonuna basın.
5. **Otomatik MLOps Devreye Girer:** Sistem bu yeni verileri hem Supabase bulutuna hem yerel Excel'e işler, ardından arka planda Random Forest modelini yeniden eğiterek (.pkl) bir sonraki günün tahmin doğruluğunu artırır.

---

## 🧠 5. Modüller ve Çalışma Prensipleri

### 1. MLOps Makine Öğrenmesi Hattı (`ml_ops.py`)
- **Algoritma:** `RandomForestRegressor (100 ağaç, max_depth=5)`
- **Feature Engineering (9 Gelişmiş Öznitelik):**
  1. `Sicaklik`: Hava sıcaklığı (°C)
  2. `Haftasonu_Mu`: Hafta sonu dinamiği (1/0)
  3. `Promosyon_Var_Mi`: Kampanya etkisi (1/0)
  4. `Ay`: Yıllık mevsimsellik (1-12)
  5. `Haftanin_Gunu`: Haftalık tüketim döngüsü (0-6)
  6. `Satis_Lag1`: Dünün gerçekleşen satış adedi (Momentum)
  7. `Satis_Lag7`: Geçen haftanın aynı günündeki satış adedi (Haftalık döngü)
  8. `Sicaklik_x_Promosyon`: Sıcak hava ile indirimin çarpan etkisi
  9. `Tatil_Mi`: Resmi tatil veya dini bayram etkisi (1/0)
- **Model Kalıcılığı:** Modeller `KafeProjesi/models/{kullanici}_{urun}_rf.pkl` olarak `joblib` ile saklanır ve RAM önbelleğinde mikrosaniyede çıkarım üretir.

### 2. Menü Mühendisliği Matrisi (`menu_engineering.py`)
Klasik Boston Consulting Group & Kasavana-Smith yeme-içme modelini uygular:
- **Porsiyon Maliyeti (COGS):** Reçetedeki her bileşenin (çekirdek, süt, su, buz, bardak, pipet, şurup, ambalaj) gramaj maliyeti toplanır.
- **Birim Katkı Payı (Contribution Margin):** $\text{Satış Fiyatı} - \text{Hammadde Maliyeti}$
- **4 Kadran Sınıflandırması:**
  - 🌟 **YILDIZLAR (Star):** Yüksek Popülarite + Yüksek Kâr $\rightarrow$ Korumalı, reçetesi değiştirilmemeli.
  - 🐴 **İŞ ATLARI (Plowhorse):** Yüksek Popülarite + Düşük Kâr $\rightarrow$ Fiyatı %5-10 artırılabilir veya reçete maliyeti optimize edilebilir.
  - 🧩 **BULMACALAR (Puzzle):** Düşük Popülarite + Yüksek Kâr $\rightarrow$ Baristalara tavsiye ettirilmeli, bültende upsell eşleştirmesi yapılır.
  - 🐕 **KÖPEKLER (Dog):** Düşük Popülarite + Düşük Kâr $\rightarrow$ Menüden çıkarma veya baştan tasarlanma adayı.

### 3. Resmi Tatil ve Etkinlik Takvimi (`calendar_events.py`)
- Türkiye resmi tatilleri (23 Nisan, 19 Mayıs, 29 Ekim vb.) ve dini bayramları (Ramazan ve Kurban 2024-2027) otomatik tanır.
- Kafe sahipleri `ozel_etkinlikler.json` üzerinden konser, maç veya yerel festival gibi özel günleri tanımlayabilir.

### 4. LLM Destekli İşletme Koçu (`llm_coaching.py`)
- `GEMINI_API_KEY` tanımlandığında en güncel **Google Gemini 2.5 Flash** modeline bağlanır.
- API anahtarı girilmediğinde veya internet kesildiğinde **Kingfool Heuristic Business Engine** devreye girer; asla hata vermez ve zengin Türkçe aksiyon raporu üretir.

---

## 📱 6. Android Mobil Uygulaması

`android_app/` dizininde tam teşekküllü native Jetpack/Kotlin Android projesi yer alır:
1. **Android Studio** ile `android_app` klasörünü açın.
2. Emülatör veya gerçek cihaz seçip yeşil **Run** butonuna basın.
3. Telefondan satış girebilir ve anlık tahminleri alabilirsiniz.

---

## 🔧 7. Hata Ayıklama & Sıkça Sorulan Sorular

- **S: `dist/app.exe` açılmıyor veya terminal hatası veriyor mu?**  
  C: Hayır. `dist/app.exe` PyInstaller ile konsolsuz (`--noconsole`) ve tüm kütüphaneler içine gömülü olarak derlenmiştir. Çift tıklamanız yeterlidir.
- **S: İnternetim kesilirse program çalışır mı?**  
  C: Evet! Sistem "Offline-First" mimaridedir. Supabase'e erişilemediğinde yerel Excel ve JSON veritabanına yazar, internet geldiğinde verileri korur.
- **S: Ürünlerimin fiyatını veya reçetesini değiştirebilir miyim?**  
  C: Evet. Masaüstünde "Menü Mühendisliği" penceresinden istediğiniz ürünün fiyatını girip "Fiyatı Kaydet"e basabilirsiniz.
