# -*- coding: utf-8 -*-
"""
Kingfool Inc. | LLM Destekli Akıllı İşletme Koçu ve Günlük Bülten Modülü (v1.4)
Yapay zeka satış tahminleri, resmi tatil/etkinlik takvimi ve Menü Mühendisliği matrisini
harmanlayarak kafe sahibine özel günlük operasyonel ve kârlılık aksiyon raporu üretir.
(Google Gemini + Akıllı Çevrimdışı Motor)
"""
import os
import json
import requests
import datetime
from typing import Dict, List, Any, Optional
import calendar_events
import menu_engineering

SYSTEM_PROMPT = """
Sen Kingfool Inc.'in uzman ve samimi Kafe İşletme Koçusun.
Görevin: Bir kafe işletmecisine; yarının yapay zeka satış tahminlerini, hava durumunu, resmi tatil/etkinlik takvimini,
hammadde ihtiyaçlarını ve Menü Mühendisliği kârlılık matrisini (Yıldızlar, Bulmacalar, İş Atları) analiz ederek 
uygulanabilir, motive edici, kârı artıran ve operasyonel aksiyonlara dayalı bir "GÜNLÜK İŞLETME BÜLTENİ" hazırlamaktır.

Rapor Formatı:
1. 🎯 GÜNÜN NABZI & YOĞUNLUK BEKLENTİSİ (Hava durumu, hafta sonu ve resmi tatil/etkinlik etkisini özetle)
2. 💰 SATIŞ & CİRO PROJEKSİYONU (Tahmini toplam bardak ve ciro analizi)
3. ⚡ KRİTİK OPERASYONEL AKSİYONLAR (Barista hazırlığı, tezgah düzeni, buz makinesi, tatil yoğunluğu önlemleri)
4. 🥛 ENVENTER & HAMMADDE UYARILARI (Gereken süt, çekirdek ve bardak miktarı)
5. 💡 GÜNÜN MENÜ MÜHENDİSLİĞİ & UPSELL TÜYOSU (Yüksek kârlı 'Bulmaca' ürünlerini lokomotif 'Yıldız' ürünlerle eşleştirme)

Tonun: Profesyonel, cana yakın, çözüm odaklı ve tam bir kahve/kafe uzmanı gibi olsun.
"""

def _yerel_akilli_bulten_uret(
    kullanici_adi: str,
    yarin_tarih: str,
    yarin_sicaklik: float,
    yarin_haftasonu: int,
    urun_tahminleri: Dict[str, int],
    hammadde_ihtiyaclari: List[Dict[str, Any]],
    ulke: str = "Türkiye"
) -> str:
    """
    Gemini API anahtarı girilmediğinde veya çevrimdışı olunduğunda çalışan
    zengin kural tabanlı işletme koçu ve menü mühendisliği motoru.
    """
    toplam_bardak = sum(urun_tahminleri.values())
    
    # Menü Mühendisliği Analizi
    matris = menu_engineering.menu_matrisi_analiz_et(urun_tahminleri)
    tahmini_ciro = sum(x["satis_fiyati"] * x["satis_adedi"] for x in matris["tum_urunler"])
    tahmini_brut_kar = matris["esikler"]["toplam_brut_kar"]

    # Tatil ve Etkinlik Bilgisi (Ülkeye Duyarlı)
    tatil_bilgi = calendar_events.tarih_tatil_veya_etkinlik_mi(yarin_tarih, ulke=ulke)
    tatil_var_mi = tatil_bilgi["ozel_gun_mu"] == 1

    gun_tipi = "Hafta Sonu" if yarin_haftasonu == 1 else "Hafta İçi"
    if tatil_var_mi:
        gun_tipi += f" ({tatil_bilgi['aciklama']})"

    hava_durumu_yorum = "oldukça sıcak ve güneşli" if yarin_sicaklik >= 26 else "ılıman"
    
    # En çok satan ürün (Yıldız veya İş Atı)
    en_populer = max(urun_tahminleri.items(), key=lambda x: x[1]) if urun_tahminleri else ("Cold Brew", 0)

    # Hammadde özet metinleri
    hammadde_satirlari = []
    for h in hammadde_ihtiyaclari[:5]:
        hammadde_satirlari.append(f"* **{h['hammadde']}:** {h['gosterim']}")
    hammadde_blok = "\n".join(hammadde_satirlari) if hammadde_satirlari else "* Yeterli veri girilmedi."

    # Operasyonel Notlar (Sıcaklık + Tatil + Hafta Sonu)
    operasyonel_notlar = []

    if tatil_var_mi:
        operasyonel_notlar.append(f"🎉 **{tatil_bilgi['aciklama']} Alarmı:** Yarın {tatil_bilgi['kategori']} olması sebebiyle gün boyu aralıksız yüksek doluluk bekleniyor. Barista vardiyasını erken başlatın ve kasa kuyruğunu azaltmak için siparişleri hızlandırın.")

    if yarin_sicaklik >= 25 and (yarin_haftasonu == 1 or tatil_var_mi):
        operasyonel_notlar.append("🔥 **Yüksek Sıcaklık + Tatil Yoğunluğu:** Öğleden sonra 13:30 - 18:30 arasında soğuk içecek akını tavan yapacak. Buz makinelerinin gece boyunca dolu çalışmasını sağla ve yedek buz torbası bulundur.")
        operasyonel_notlar.append("🥛 **Süt & Soğutucu Düzeni:** Soğuk süt tüketimi zirveye çıkacaktır. Dolap soğukluğunu (+4°C) kontrol et.")
    elif yarin_haftasonu == 1 or tatil_var_mi:
        operasyonel_notlar.append("🎉 **Tatil / Hafta Sonu Dinamiği:** Sabah 10:30 sonrası ve ikindi vakti oturma alanlarında doluluk yüksek olacak. 2. baristanın öğleden sonra vardiyasında olması kritik.")
    else:
        operasyonel_notlar.append("💼 **Hafta İçi Dinamiği:** Sabah 08:30 - 10:00 arası 'al-götür' (take-away) trafiği yoğun olacaktır. Karton bardak ve kapakları tezgah altına istifle.")

    if "Cold Brew" in urun_tahminleri and urun_tahminleri["Cold Brew"] >= 30:
        operasyonel_notlar.append(f"❄️ **Cold Brew Partisi:** Yarın tahmini {urun_tahminleri['Cold Brew']} bardak Cold Brew satışı öngörülüyor. Demleme süresi (16-20 saat) nedeniyle bu akşamdan en az 2 partiyi hazırla.")

    operasyon_blok = "\n".join(operasyonel_notlar)

    # 5. Kısım: Menü Mühendisliği ve Upsell Önerisi
    bulmacalar = matris.get("bulmacalar", [])
    yildizlar = matris.get("yildizlar", [])

    if bulmacalar:
        hedef_bulmaca = bulmacalar[0]
        upsell_oneri = f"* 🍰 **Yüksek Kârlı Fırsat (Bulmaca Ürünü):** '{hedef_bulmaca['urun']}' ürününüz porsiyon başına **%{hedef_bulmaca['kar_marji_yuzde']} brüt kâr marjına** sahip! Yarın en çok satan içeceğiniz '{en_populer[0]}' sipariş eden misafirlere baristalarınızın *'{hedef_bulmaca['urun']}' denemek ister misiniz?* sorusunu sormasını sağlayarak sepet kârını katlayabilirsiniz."
    elif yildizlar:
        hedef_yildiz = yildizlar[0]
        upsell_oneri = f"* 🌟 **Yıldız Ürün Gücü:** '{hedef_yildiz['urun']}' hem yüksek hacim hem de yüksek marjla kasanızın lokomotifi. Yanına ikincil bir tamamlayıcı atıştırmalık ekleyerek ciroyu büyütebilirsiniz."
    else:
        upsell_oneri = "* 💡 **Çapraz Satış:** Soğuk içecek alan misafirlere taze atıştırmalık veya kurabiye önererek sepet ortalamasını %20 yukarı çekebilirsiniz."

    tatil_vurgusu = ""
    if tatil_var_mi:
        tatil_vurgusu = f"\n> [!NOTE]\n> **Takvim Bildirimi:** Yarın **{tatil_bilgi['aciklama']}** ({tatil_bilgi['kategori']}) kutlanıyor! Normal bir {gun_tipi} gününe kıyasla satışlarda %25-%40 ivme öngörülmektedir.\n"

    bulten = f"""# 🃏 Kingfool Inc. | Akıllı İşletme Koçu Günlük Bülteni
**Tarih:** {yarin_tarih} | **Kullanıcı:** {kullanici_adi} | **Hava:** {yarin_sicaklik}°C ({gun_tipi})
{tatil_vurgusu}
---

### 1. 🎯 Günün Nabzı & Yoğunluk Beklentisi
Sevgili **{kullanici_adi}**, yarın hava **{yarin_sicaklik}°C** ile {hava_durumu_yorum} seyredecek ve **{gun_tipi}** temposu yaşanacak. Yapay zeka modelimiz toplamda yaklaşık **{toplam_bardak} adet ürün/bardak** satışı öngörüyor. Günün lokomotif ürünü tahmini **{en_populer[1]} adetle {en_populer[0]}** olacak!

### 2. 💰 Satış & Ciro Projeksiyonu (Menü Mühendisliği)
* 📊 **Toplam Beklenen Satış:** ~{toplam_bardak} Adet
* 💵 **Tahmini Günlük Ciro:** ~{tahmini_ciro:,.0f} TL
* 💎 **Tahmini Brüt Kâr Katkısı:** ~{tahmini_brut_kar:,.0f} TL
* 📈 **Trend:** Modelimiz son satış geçmişi, sıcaklık ve tatil takvimini harmanlayarak yüksek talep ivmesi hesapladı.

### 3. ⚡ Kritik Operasyonel Aksiyonlar
{operasyon_blok}

### 4. 🥛 Yarınki Tahmini Hammadde İhtiyacı
Yapay zeka bardak satış tahminlerini reçetelere vurduğumuzda yarın için gereken net sarfiyat:
{hammadde_blok}

### 5. 💡 Menü Mühendisliği & Satış Artırma (Upselling) Tüyosu
{upsell_oneri}
"""
    return bulten.strip()

def gunluk_koc_raporu_uret(
    kullanici_adi: str,
    yarin_tarih: str,
    yarin_sicaklik: float,
    yarin_haftasonu: int,
    urun_tahminleri: Dict[str, int],
    hammadde_ihtiyaclari: List[Dict[str, Any]],
    gemini_api_key: Optional[str] = None,
    ulke: str = "Türkiye"
) -> Dict[str, Any]:
    """
    Rapor üretici ana fonksiyon:
    1. Gemini API Anahtarı varsa Gemini 2.5 Flash ile üretir.
    2. Yoksa veya hata verirse akıllı yerel motorla üretir.
    """
    tatil_info = calendar_events.tarih_tatil_veya_etkinlik_mi(yarin_tarih, ulke=ulke)
    matris = menu_engineering.menu_matrisi_analiz_et(urun_tahminleri)

    api_key = gemini_api_key if isinstance(gemini_api_key, str) else None
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if isinstance(api_key, str) and api_key.strip():
        try:
            user_content = f"""
Kullanıcı / Kafe Sahibi: {kullanici_adi}
Ülke / Konum: {ulke}
Yarınki Tarih: {yarin_tarih}
Yarınki Sıcaklık: {yarin_sicaklik}°C
Hafta Sonu Mu: {'Evet' if yarin_haftasonu == 1 else 'Hayır'}
Resmi Tatil / Etkinlik: {tatil_info['aciklama']} ({tatil_info['kategori']})
Yarın İçin Ürün Satış Tahminleri: {json.dumps(urun_tahminleri, ensure_ascii=False)}
Gereken Hammadde İhtiyaçları: {json.dumps([{'madde': x['hammadde'], 'miktar': x['gosterim']} for x in hammadde_ihtiyaclari], ensure_ascii=False)}
Menü Mühendisliği Yıldızlar: {json.dumps([x['urun'] for x in matris.get('yildizlar', [])], ensure_ascii=False)}
Menü Mühendisliği Bulmacalar (Yüksek Kârlı, Upsell Önerisi): {json.dumps([x['urun'] for x in matris.get('bulmacalar', [])], ensure_ascii=False)}

Lütfen bu verilere göre kafe sahibine özel, tatil yoğunluğunu ve Menü Mühendisliği kâr tavsiyelerini kapsayan Günlük Aksiyon Raporunu hazırla.
"""
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key.strip()}"
            payload = {
                "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "contents": [{"parts": [{"text": user_content}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1000}
            }
            r = requests.post(url, json=payload, timeout=12)
            if r.status_code == 200:
                res_data = r.json()
                text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return {
                    "success": True,
                    "kaynak": "Google Gemini 2.5 Flash",
                    "rapor": text.strip(),
                    "tatil_bilgisi": tatil_info,
                    "menu_matrisi": matris
                }
        except Exception as e:
            print(f"[LLM Coaching] Gemini API çağrısı başarısız, yerel motora geçiliyor: {e}")

    # Yerel Akıllı Motor Fallback
    rapor_metni = _yerel_akilli_bulten_uret(
        kullanici_adi=kullanici_adi,
        yarin_tarih=yarin_tarih,
        yarin_sicaklik=yarin_sicaklik,
        yarin_haftasonu=yarin_haftasonu,
        urun_tahminleri=urun_tahminleri,
        hammadde_ihtiyaclari=hammadde_ihtiyaclari,
        ulke=ulke
    )
    return {
        "success": True,
        "kaynak": "Kingfool Heuristic Business Engine",
        "rapor": rapor_metni,
        "tatil_bilgisi": tatil_info,
        "menu_matrisi": matris
    }
