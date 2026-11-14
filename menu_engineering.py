# -*- coding: utf-8 -*-
"""
Kingfool Inc. | Menü Mühendisliği ve Kâr Marjı Matrisi Modülü (v1.4)
Kasavana & Smith F&B Menü Mühendisliği modelini uygulayarak ürünlerin
hammadde maliyetini (COGS), brüt kâr katkısını ve popülaritesini analiz eder.
Ürünleri 4 kadrana ayırır: Yıldızlar, İş Atları, Bulmacalar, Köpekler.
"""
import os
import json
from typing import Dict, List, Any, Optional
import inventory_manager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIYATLAR_DOSYASI = os.path.join(BASE_DIR, "urun_fiyatlari.json")

# Varsayılan Hammadde Birim Maliyetleri (TL cinsinden)
# Gram başına, ml başına ve adet başına maliyetler
HAMMADDE_BIRIM_MALIYETLERI = {
    "Kahve Çekirdeği": 0.65,          # 650 TL / kg -> 0.65 TL / g
    "Süt": 0.038,                     # 38 TL / Litre -> 0.038 TL / ml
    "Su": 0.005,                      # Şebeke/Arıtma suyu
    "Buz": 0.015,                     # Buz makinesi su + elektrik maliyeti / g
    "Karton Bardak": 2.75,            # Baskılı çift duvar bardak / adet
    "Pipet": 0.50,                    # Biyobozunur pipet / adet
    "Şurup / Çikolata Sosu": 0.25,    # Monin/Torani şurup / ml
    "Porsiyon Brownie": 45.00,        # Üretim/tedarik maliyeti / porsiyon
    "Servis Peçetesi / Ambalaj": 1.25,# Kutu + peçete / adet
    "Limon Konsantresi": 0.12,        # Sıkma limon suyu konsantresi / ml
    "Çay Demi": 0.04,                 # Dökme çay demi / ml
    "Sıcak Su": 0.005,                # Kaynar su
    "Chai Çayı Karışımı": 0.30,       # Chai özü / g
    "Porsiyon Scone": 35.00,          # Scone / adet
    "İtalyan Biscotti": 25.00,        # Biscotti / adet
    "Taze Ekmek / Hamur": 15.00,      # Ekmek / adet
    "Kese Kağıdı / Paket": 1.50,      # Paketleme / adet
    "Dilim Kek / Pasta": 40.00,       # Kek / adet
    "Kruvasan / Hamur İşi": 30.00,    # Kruvasan / adet
    "Sandviç Ekmeği & Malzemesi": 45.00, # Sandviç / adet
    "Porsiyon Kurabiye": 20.00,       # Kurabiye / adet
    "Porsiyon Ürün / İkram": 25.00,   # Genel yiyecek
    "Kahve Çekirdeği / İçecek Özü": 0.60, # Genel içecek
    "Süt / Su": 0.030                 # Genel sıvı
}

# Varsayılan Satış Fiyatları (Kullanıcı dilerse arayüzden veya JSON'dan güncelleyebilir)
VARSAYILAN_SATIS_FIYATLARI = {
    "Cold Brew": 125.0,
    "Iced Latte": 135.0,
    "Iced Americano": 115.0,
    "Şuruplu Latte / Mocha": 145.0,
    "Brownie": 150.0,
    "Limonata": 105.0,
    "Çay": 45.0,
    # Maven Roasters (NYC) Fiyatları
    "Barista Espresso": 95.0,
    "Gourmet brewed coffee": 110.0,
    "Brewed Chai tea": 120.0,
    "Hot chocolate": 125.0,
    "Scone": 90.0,
    "Biscotti": 65.0,
    # Bread Basket (Edinburgh) Fiyatları
    "Coffee": 100.0,
    "Bread": 55.0,
    "Tea": 50.0,
    "Cake": 110.0,
    "Pastry": 85.0,
    "Sandwich": 130.0,
    "Cookies": 60.0
}

def kullanici_fiyatlarini_yukle() -> Dict[str, float]:
    """Kullanıcının özelleştirdiği satış fiyatlarını yükler."""
    fiyatlar = dict(VARSAYILAN_SATIS_FIYATLARI)
    if os.path.exists(FIYATLAR_DOSYASI):
        try:
            with open(FIYATLAR_DOSYASI, "r", encoding="utf-8") as f:
                ozel = json.load(f)
                fiyatlar.update(ozel)
        except Exception:
            pass
    return fiyatlar

def satis_fiyati_kaydet(urun_adi: str, fiyat: float) -> bool:
    """Belirli bir ürünün satış fiyatını günceller."""
    fiyatlar = kullanici_fiyatlarini_yukle()
    fiyatlar[urun_adi] = float(fiyat)
    try:
        with open(FIYATLAR_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(fiyatlar, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def porsiyon_maliyeti_hesapla(urun_adi: str) -> Dict[str, Any]:
    """
    Belirli bir ürünün reçetesinden tek porsiyon hammadde maliyetini (COGS) hesaplar.
    Dönüş: {
        'urun': 'Cold Brew',
        'toplam_maliyet': 36.25,
        'kalemler': [{'madde': 'Kahve Çekirdeği', 'miktar': 50g, 'maliyet': 32.50}, ...]
    }
    """
    recete = inventory_manager.urun_recetesi_getir(urun_adi)
    toplam = 0.0
    kalem_detaylari = []

    for k in recete:
        h_ad = k["hammadde"]
        miktar = k["miktar"]
        birim = k["birim"]
        birim_maliyet = HAMMADDE_BIRIM_MALIYETLERI.get(h_ad, 1.0)
        tutar = round(miktar * birim_maliyet, 2)
        toplam += tutar
        kalem_detaylari.append({
            "hammadde": h_ad,
            "miktar": miktar,
            "birim": birim,
            "kalem_maliyeti": tutar
        })

    return {
        "urun": urun_adi,
        "porsiyon_maliyeti": round(toplam, 2),
        "kalemler": kalem_detaylari
    }

def menu_matrisi_analiz_et(urun_satis_adetleri: Dict[str, int]) -> Dict[str, Any]:
    """
    Kasavana & Smith Menü Mühendisliği Matrisi Analizi.
    Girdi: {'Cold Brew': 60, 'Iced Latte': 120, 'Brownie': 40, ...}
    
    4 Kadran:
    1. 🌟 YILDIZ (Star): Yüksek Popülarite, Yüksek Kâr
    2. 🐴 İŞ ATI (Plowhorse): Yüksek Popülarite, Düşük Kâr
    3. 🧩 BULMACA (Puzzle): Düşük Popülarite, Yüksek Kâr
    4. 🐕 KÖPEK (Dog): Düşük Popülarite, Düşük Kâr
    """
    fiyatlar = kullanici_fiyatlarini_yukle()
    if not urun_satis_adetleri:
        urun_satis_adetleri = {u: 50 for u in fiyatlar.keys()}

    urun_metrikleri = []
    toplam_adet = 0
    toplam_katki_payi = 0.0

    for urun_adi, adet in urun_satis_adetleri.items():
        if adet is None or adet < 0:
            adet = 0
        maliyet_bilgi = porsiyon_maliyeti_hesapla(urun_adi)
        maliyet = maliyet_bilgi["porsiyon_maliyeti"]
        fiyat = fiyatlar.get(urun_adi, 120.0)
        katki_payi = max(0.0, round(fiyat - maliyet, 2))  # Birim Brüt Kâr (Margin)
        kar_marji_yuzde = round((katki_payi / fiyat) * 100, 1) if fiyat > 0 else 0.0

        toplam_adet += adet
        toplam_katki_payi += katki_payi * adet

        urun_metrikleri.append({
            "urun": urun_adi,
            "satis_adedi": adet,
            "satis_fiyati": fiyat,
            "porsiyon_maliyeti": maliyet,
            "katki_payi": katki_payi,
            "kar_marji_yuzde": kar_marji_yuzde,
            "toplam_urun_kari": round(katki_payi * adet, 2)
        })

    # Eşik Değerlerin Hesaplanması
    urun_sayisi = len(urun_metrikleri) if len(urun_metrikleri) > 0 else 1
    esik_adet = toplam_adet / urun_sayisi
    esik_katki_payi = (toplam_katki_payi / toplam_adet) if toplam_adet > 0 else (sum(x["katki_payi"] for x in urun_metrikleri) / urun_sayisi)

    analiz_sonuclari = {
        "yildizlar": [],
        "is_atlari": [],
        "bulmacalar": [],
        "kopekler": [],
        "tum_urunler": []
    }

    for item in urun_metrikleri:
        adet = item["satis_adedi"]
        kp = item["katki_payi"]

        yuksek_hacim = adet >= esik_adet
        yuksek_kar = kp >= esik_katki_payi

        if yuksek_hacim and yuksek_kar:
            sinif = "YILDIZ"
            ikon = "🌟"
            tavsiye = "Menünün lokomotifi! Kaliteden ödün verme, menüde ve vitrinde göz hizasında tut."
            kategori_key = "yildizlar"
        elif yuksek_hacim and not yuksek_kar:
            sinif = "İŞ ATI"
            ikon = "🐴"
            tavsiye = "Çok satıyor ama kârı düşük. Fiyatı %5-10 artırabilir veya porsiyon hammadde maliyetini optimize edebilirsin."
            kategori_key = "is_atlari"
        elif not yuksek_hacim and yuksek_kar:
            sinif = "BULMACA"
            ikon = "🧩"
            tavsiye = "Birim kârı harika ancak az satıyor! Baristalara/garsonlara öneri yaptır, kahve yanında kombin teklifi olarak sun."
            kategori_key = "bulmacalar"
        else:
            sinif = "KÖPEK"
            ikon = "🐕"
            tavsiye = "Hem az satıyor hem de kârı düşük. Reçetesini tamamen yenilemeyi veya menüden kaldırmayı değerlendir."
            kategori_key = "kopekler"

        islenmis_item = {
            **item,
            "sinif": sinif,
            "ikon": ikon,
            "tavsiye": tavsiye,
            "yuksek_hacim": yuksek_hacim,
            "yuksek_kar": yuksek_kar
        }

        analiz_sonuclari[kategori_key].append(islenmis_item)
        analiz_sonuclari["tum_urunler"].append(islenmis_item)

    analiz_sonuclari["esikler"] = {
        "ortalama_satis_adedi": round(esik_adet, 1),
        "ortalama_katki_payi": round(esik_katki_payi, 2),
        "toplam_adet": toplam_adet,
        "toplam_brut_kar": round(toplam_katki_payi, 2)
    }

    return analiz_sonuclari
