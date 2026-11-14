# Google MLCC ve Özellik Mühendisliği (Feature Engineering) Temel Kılavuzu
**NotebookLM İçin Yapılandırılmış Eğitim Kaynağı ve Vaka İncelemesi**

---

## BÖLÜM 1: GOOGLE MACHINE LEARNING CRASH COURSE (MLCC) TEMELLERİ

### 1.1. Makine Öğrenmesi Çerçevesi (Supervised Learning)
* **Girdi Özellikleri (Features - X):** Modele karar vermesi için sunulan ölçülebilir değişkenler (Örn: Hava sıcaklığı, günün haftasonu olup olmaması, promosyon durumu).
* **Hedef Etiket (Label / Target - y):** Modelin tahmin etmeye çalıştığı gerçek dünya çıktısı (Örn: Günlük satılan bardak sayısı).
* **Eğitim (Training / Fit):** Modelin geçmiş girdiler ($X$) ile geçmiş sonuçlar ($y$) arasındaki ağırlıkları ve karar kurallarını matematiksel olarak optimize etme süreci.
* **Çıkarım (Inference / Predict):** Eğitilmiş modelin henüz görmediği yeni senaryolara (Örn: Yarınki hava 32°C olursa) tahmin üretmesi.

---

### 1.2. Model Başarısı ve Hata Fonksiyonları (Loss Functions)
Modelin tahminlerinin gerçek dünyadan ne kadar saptığını ölçen temel metrikler:
1. **MAE (Mean Absolute Error - Ortalama Mutlak Hata):**
   * Tahmin edilen bardak sayısı ile gerçek satış arasındaki mutlak bardak farklarının ortalamasıdır.
   * Yorumu son derece sezgiseldir: *"Modelimiz ortalama ±3.2 bardak sapma yapıyor."*
2. **MSE / RMSE (Root Mean Squared Error):**
   * Hataların karelerinin ortalamasının kareköküdür. Büyük hataları daha sert cezalandırır. Uç hataları (outliers) tespit etmek için kritiktir.
3. **$R^2$ Skoru (Belirlilik Katsayısı):**
   * Satışlardaki toplam dalgalanmanın yüzde kaçının model tarafından açıklandığını gösterir. 1.0 mükemmel tahmin, 0.0 ise ortalama almaktan farksız bir modeli ifade eder.

---

### 1.3. Aşırı Öğrenme (Overfitting) ve Yetersiz Öğrenme (Underfitting)
* **Underfitting (Yetersiz Öğrenme):** Modelin verideki temel trendleri bile yakalayamayacak kadar basit kalmasıdır (Örn: Sıcaklık arttıkça soğuk içeceğin arttığını görememesi).
* **Overfitting (Ezberleme / Aşırı Uyum):** Modelin eğitim verisindeki rastgele gürültüleri dahi "kural" sanıp ezberlemesidir. Geçmiş veride %99 başarılı olurken, yarın gerçek dünyayla karşılaştığında çuvallar.
* **Bias-Variance Dengesi:**
  * **High Bias:** Basit model, underfitting.
  * **High Variance:** Karmaşık model, overfitting.
* **Random Forest Neden Overfitting'e Dirençlidir?:**
  `RandomForestRegressor`, tek bir derin ağaç yerine yüzlerce sığ ağacın (`max_depth=5`, `n_estimators=100`) bağımsız tahminlerinin ortalamasını alır (Bagging / Bootstrap Aggregating). Bu sayede varyansı düşürür ve ezberlemeyi engeller.

---

### 1.4. Veri Ayrımı (Train / Validation / Test Split)
Modelin gerçek dünya sınavından geçmesi için veriler asla tek bir torbada eğitilip test edilmez:
* **Eğitim Seti (%70 - %80):** Modelin kuralları keşfettiği çalışma alanı.
* **Test Seti (%20 - %30):** Modelin eğitim sırasında hiç görmediği, başarısının tarafsızca sınandığı sınav alanı.

---

## BÖLÜM 2: ÖZELLİK MÜHENDİSLİĞİ (FEATURE ENGINEERING)

Özellik mühendisliği; ham veri tablolarından yapay zekânın daha rahat anlayabileceği ve örüntü yakalayabileceği yeni matematiksel değişkenler üretme sanatıdır. Veri biliminde **"Kaliteli özellik, karmaşık algoritmadan üstündür"** ilkesi geçerlidir.

---

### 2.1. Zaman ve Tarih Tabanlı Özellik Türetme (Datetime Features)
Ham bir `Tarih` sütunu (Örn: `2026-09-08`) modele doğrudan sayı olarak verilemez. Buradan şu alt özellikler türetilir:
1. **Haftanın Günü (Day of Week):** 0=Pazartesi, 6=Pazar. (Kafelerde Cuma-Cumartesi-Pazar satışları sıçrama yapar).
2. **Ay ve Mevsim (Month / Season):** Yaz aylarında dondurucu ve soğuk içecek talebi, kış aylarına göre taban olarak daha yüksektir.
3. **Maaş Günleri / Ay Başı Etkisi:** Ayın 1'i ve 15'i gibi günlerde tüketim harcamaları artar.

---

### 2.2. Gecikmeli Özellikler (Lag Features & Rolling Windows)
Zaman serisi ve perakende tahminlerinde bugünkü satışın en büyük habercisi geçmiş günlerin performansıdır:
1. **Dünkü Satış ($Lag_1$):** Dün kaç bardak satıldı?
2. **Geçen Haftaki Aynı Gün ($Lag_7$):** Geçen hafta Salı günü kaç bardak satıldı?
3. **Hareketli Ortalama (Rolling Mean - 7 Gün):** Son 7 günün ortalama satış trendi artıyor mu, azalıyor mu?

---

### 2.3. Etkileşim Özellikleri (Interaction Features)
İki değişken bir araya geldiğinde çarpan etkisi yaratıyorsa bu iki değişken çarpılarak yeni bir özellik üretilir:
* **Örnek:** `Sicaklik_X_Haftasonu = Sicaklik * Haftasonu_Mu`
* **Gerekçe:** 35 derece sıcaklık hafta içi ofis saatinde satışı %20 artırırken, hafta sonu sahil kenarında %80 artırabilir.

---

### 2.4. Kategorik Değişkenlerin Kodlanması (Encoding)
Metin halindeki kategoriler (Örn: Şehir isimleri, İçecek türleri) makine öğrenmesine doğrudan verilemez:
* **One-Hot Encoding:** Her kategori için 0 ve 1'lerden oluşan ayrı sütun açılması (Örn: `Sehir_Istanbul`, `Sehir_Budva`).
* **Binary Encoding:** 0 veya 1 (Örn: Promosyon var mı: 1, yok: 0).

---

## BÖLÜM 3: KINGFOOL INC. V1.2 İÇİN GELECEK VİZYONU

Bu ilkeler doğrultusunda Kingfool Inc. mimarisine eklenebilecek 3 üst düzey özellik:
1. **Yağış Durumu (Precipitation):** Açık kaynak Open-Meteo'dan yağmur miktarı çekilerek "Yağmurlu günlerde soğuk içecek düşüşü" modellenebilir.
2. **Son 3 Günün Satış Ortalaması (Rolling 3-Day Average):** Trend takip edilebilir.
3. **Hissedilen Sıcaklık (Apparent Temperature):** Nem ile birleşen bunaltıcı sıcaklığın satışa etkisi ölçülebilir.

---

## BÖLÜM 4: RESMİ ONLİNE REFERANS KAYNAKLARI (URL'LER)
NotebookLM'e doğrudan web bağlantısı olarak da ekleyebileceğiniz resmi dokümanlar:
* Google MLCC Ana Sayfa: `https://developers.google.com/machine-learning/crash-course`
* Google MLCC Temsil ve Özellik Mühendisliği: `https://developers.google.com/machine-learning/crash-course/representation`
* Google MLCC Genelleme ve Overfitting: `https://developers.google.com/machine-learning/crash-course/generalization`
* Scikit-Learn Random Forest Resmi Kılavuzu: `https://scikit-learn.org/stable/modules/ensemble.html#forests-of-randomized-trees`
* Kaggle Feature Engineering Rehberi: `https://www.kaggle.com/learn/feature-engineering`
