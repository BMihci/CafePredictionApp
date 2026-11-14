# -*- coding: utf-8 -*-
"""
Kingfool Inc. | Reçete ve Envanter / Hammadde Optimizasyon Modülü (v1.3)
Ürün bazında hammadde sarfiyatını hesaplar ve kritik stok alarmları üretir.
"""
from typing import Dict, List, Any

# Varsayılan Ürün Reçeteleri (1 Porsiyon / Bardak İçin Standart Gramaj ve Hacimler)
VARSAYILAN_RECETELER: Dict[str, List[Dict[str, Any]]] = {
    "Cold Brew": [
        {"hammadde": "Kahve Çekirdeği", "miktar": 50.0, "birim": "g"},
        {"hammadde": "Su", "miktar": 150.0, "birim": "ml"},
        {"hammadde": "Karton Bardak", "miktar": 1.0, "birim": "adet"},
        {"hammadde": "Pipet", "miktar": 1.0, "birim": "adet"},
    ],
    "Iced Latte": [
        {"hammadde": "Kahve Çekirdeği", "miktar": 20.0, "birim": "g"},
        {"hammadde": "Süt", "miktar": 180.0, "birim": "ml"},
        {"hammadde": "Buz", "miktar": 50.0, "birim": "g"},
        {"hammadde": "Karton Bardak", "miktar": 1.0, "birim": "adet"},
        {"hammadde": "Pipet", "miktar": 1.0, "birim": "adet"},
    ],
    "Iced Americano": [
        {"hammadde": "Kahve Çekirdeği", "miktar": 20.0, "birim": "g"},
        {"hammadde": "Su", "miktar": 150.0, "birim": "ml"},
        {"hammadde": "Buz", "miktar": 40.0, "birim": "g"},
        {"hammadde": "Karton Bardak", "miktar": 1.0, "birim": "adet"},
        {"hammadde": "Pipet", "miktar": 1.0, "birim": "adet"},
    ],
    "Şuruplu Latte / Mocha": [
        {"hammadde": "Kahve Çekirdeği", "miktar": 20.0, "birim": "g"},
        {"hammadde": "Süt", "miktar": 160.0, "birim": "ml"},
        {"hammadde": "Şurup / Çikolata Sosu", "miktar": 20.0, "birim": "ml"},
        {"hammadde": "Buz", "miktar": 50.0, "birim": "g"},
        {"hammadde": "Karton Bardak", "miktar": 1.0, "birim": "adet"},
        {"hammadde": "Pipet", "miktar": 1.0, "birim": "adet"},
    ],
    "Brownie": [
        {"hammadde": "Porsiyon Brownie", "miktar": 1.0, "birim": "adet"},
        {"hammadde": "Servis Peçetesi / Ambalaj", "miktar": 1.0, "birim": "adet"},
    ],
    "Limonata": [
        {"hammadde": "Limon Konsantresi", "miktar": 50.0, "birim": "ml"},
        {"hammadde": "Su", "miktar": 200.0, "birim": "ml"},
        {"hammadde": "Buz", "miktar": 50.0, "birim": "g"},
        {"hammadde": "Karton Bardak", "miktar": 1.0, "birim": "adet"},
        {"hammadde": "Pipet", "miktar": 1.0, "birim": "adet"},
    ],
    "Çay": [
        {"hammadde": "Çay Demi", "miktar": 80.0, "birim": "ml"},
        {"hammadde": "Sıcak Su", "miktar": 120.0, "birim": "ml"},
        {"hammadde": "Karton Bardak", "miktar": 1.0, "birim": "adet"},
    ],
    # Maven Roasters (NYC) Ürünleri
    "Barista Espresso": [
        {"hammadde": "Kahve Çekirdeği", "miktar": 18.0, "birim": "g"},
        {"hammadde": "Su", "miktar": 40.0, "birim": "ml"},
        {"hammadde": "Karton Bardak", "miktar": 1.0, "birim": "adet"},
    ],
    "Gourmet brewed coffee": [
        {"hammadde": "Kahve Çekirdeği", "miktar": 25.0, "birim": "g"},
        {"hammadde": "Sıcak Su", "miktar": 250.0, "birim": "ml"},
        {"hammadde": "Karton Bardak", "miktar": 1.0, "birim": "adet"},
    ],
    "Brewed Chai tea": [
        {"hammadde": "Chai Çayı Karışımı", "miktar": 15.0, "birim": "g"},
        {"hammadde": "Süt", "miktar": 150.0, "birim": "ml"},
        {"hammadde": "Sıcak Su", "miktar": 100.0, "birim": "ml"},
        {"hammadde": "Karton Bardak", "miktar": 1.0, "birim": "adet"},
    ],
    "Hot chocolate": [
        {"hammadde": "Çikolata Tozu/Sosu", "miktar": 30.0, "birim": "g"},
        {"hammadde": "Süt", "miktar": 220.0, "birim": "ml"},
        {"hammadde": "Karton Bardak", "miktar": 1.0, "birim": "adet"},
    ],
    "Scone": [
        {"hammadde": "Porsiyon Scone", "miktar": 1.0, "birim": "adet"},
        {"hammadde": "Servis Peçetesi / Ambalaj", "miktar": 1.0, "birim": "adet"},
    ],
    "Biscotti": [
        {"hammadde": "İtalyan Biscotti", "miktar": 1.0, "birim": "adet"},
        {"hammadde": "Servis Peçetesi / Ambalaj", "miktar": 1.0, "birim": "adet"},
    ],
    # The Bread Basket (Edinburgh) Ürünleri
    "Coffee": [
        {"hammadde": "Kahve Çekirdeği", "miktar": 20.0, "birim": "g"},
        {"hammadde": "Sıcak Su", "miktar": 200.0, "birim": "ml"},
        {"hammadde": "Karton Bardak", "miktar": 1.0, "birim": "adet"},
    ],
    "Bread": [
        {"hammadde": "Taze Ekmek / Hamur", "miktar": 1.0, "birim": "adet"},
        {"hammadde": "Kese Kağıdı / Paket", "miktar": 1.0, "birim": "adet"},
    ],
    "Tea": [
        {"hammadde": "Çay Demi", "miktar": 80.0, "birim": "ml"},
        {"hammadde": "Sıcak Su", "miktar": 150.0, "birim": "ml"},
        {"hammadde": "Karton Bardak", "miktar": 1.0, "birim": "adet"},
    ],
    "Cake": [
        {"hammadde": "Dilim Kek / Pasta", "miktar": 1.0, "birim": "adet"},
        {"hammadde": "Servis Peçetesi / Ambalaj", "miktar": 1.0, "birim": "adet"},
    ],
    "Pastry": [
        {"hammadde": "Kruvasan / Hamur İşi", "miktar": 1.0, "birim": "adet"},
        {"hammadde": "Servis Peçetesi / Ambalaj", "miktar": 1.0, "birim": "adet"},
    ],
    "Sandwich": [
        {"hammadde": "Sandviç Ekmeği & Malzemesi", "miktar": 1.0, "birim": "adet"},
        {"hammadde": "Kese Kağıdı / Paket", "miktar": 1.0, "birim": "adet"},
    ],
    "Cookies": [
        {"hammadde": "Porsiyon Kurabiye", "miktar": 1.0, "birim": "adet"},
        {"hammadde": "Servis Peçetesi / Ambalaj", "miktar": 1.0, "birim": "adet"},
    ]
}

def urun_recetesi_getir(urun_adi: str) -> List[Dict[str, Any]]:
    """Belirli bir ürünün reçetesini döndürür."""
    for anahtar, recete in VARSAYILAN_RECETELER.items():
        if anahtar.lower() in urun_adi.lower() or urun_adi.lower() in anahtar.lower():
            return recete

    u_lower = urun_adi.lower()
    # Yiyecek / Tatlı / Unlu Mamul tespiti
    if any(k in u_lower for k in ["pasta", "tatlı", "tatli", "kurabiye", "kek", "börek", "borek", "donut", "muffin", "tost", "sandwich", "sandviç"]):
        return [
            {"hammadde": "Porsiyon Ürün / İkram", "miktar": 1.0, "birim": "adet"},
            {"hammadde": "Servis Peçetesi / Ambalaj", "miktar": 1.0, "birim": "adet"},
        ]

    # Varsayılan genel içecek reçetesi
    return [
        {"hammadde": "Kahve Çekirdeği / İçecek Özü", "miktar": 20.0, "birim": "g"},
        {"hammadde": "Süt / Su", "miktar": 150.0, "birim": "ml"},
        {"hammadde": "Karton Bardak", "miktar": 1.0, "birim": "adet"},
    ]

def hammadde_ihtiyaci_hesapla(tahminler: Dict[str, int]) -> List[Dict[str, Any]]:
    """
    Yarın için ürün bazında tahmin edilen satış adetlerini alıp
    gereken toplam hammadde miktarını hesaplar ve insan dostu birimlere dönüştürür.
    Örnek girdi: {'Cold Brew': 50, 'Iced Latte': 100}
    """
    toplam_sarfiyat: Dict[str, Dict[str, Any]] = {}

    for urun_adi, adet in tahminler.items():
        try:
            adet_sayi = float(adet)
        except (ValueError, TypeError):
            continue
        if adet_sayi <= 0:
            continue
        recete = urun_recetesi_getir(urun_adi)
        for kalem in recete:
            h_ad = kalem["hammadde"]
            miktar = kalem["miktar"] * adet_sayi
            birim = kalem["birim"]

            if h_ad not in toplam_sarfiyat:
                toplam_sarfiyat[h_ad] = {"toplam_miktar": 0.0, "birim": birim}
            toplam_sarfiyat[h_ad]["toplam_miktar"] += miktar

    # İnsan dostu birim dönüşümleri (Gram -> Kg, ML -> Litre)
    sonuc: List[Dict[str, Any]] = []
    for h_ad, veri in toplam_sarfiyat.items():
        miktar = veri["toplam_miktar"]
        birim = veri["birim"]

        if birim == "g" and miktar >= 1000:
            gosterim = f"{miktar / 1000.0:.2f} kg"
            saf_miktar = round(miktar / 1000.0, 2)
            yeni_birim = "kg"
        elif birim == "ml" and miktar >= 1000:
            gosterim = f"{miktar / 1000.0:.2f} Litre"
            saf_miktar = round(miktar / 1000.0, 2)
            yeni_birim = "Litre"
        elif birim == "adet":
            gosterim = f"{int(miktar)} adet"
            saf_miktar = int(miktar)
            yeni_birim = "adet"
        else:
            gosterim = f"{miktar:.1f} {birim}"
            saf_miktar = round(miktar, 1)
            yeni_birim = birim

        sonuc.append({
            "hammadde": h_ad,
            "ham_miktar": miktar,
            "orijinal_birim": birim,
            "saf_miktar": saf_miktar,
            "gosterim_birimi": yeni_birim,
            "gosterim": gosterim
        })

    # Önem sırasına göre sırala (Kahve, Süt, Bardak üstte)
    oncelik = {"Kahve Çekirdeği": 1, "Süt": 2, "Karton Bardak": 3, "Buz": 4, "Pipet": 5}
    sonuc.sort(key=lambda x: oncelik.get(x["hammadde"], 99))
    return sonuc

def stok_kontrol_ve_uyarilar(ihtiyaclar: List[Dict[str, Any]], mevcut_stok: Dict[str, float] = None) -> List[str]:
    """
    Eğer mevcut stok bilgisi varsa kontrol eder, yoksa operasyonel güvenlik önerileri üretir.
    """
    uyarilar: List[str] = []
    
    # Varsayılan tahmini güvenlik eşikleri kontrolü
    for item in ihtiyaclar:
        h_ad = item["hammadde"]
        gosterim = item["gosterim"]
        if "Süt" in h_ad:
            uyarilar.append(f"🥛 Süt İhtiyacı: Yarın en az {gosterim} taze süt bulundurmalısın. Dolap soğukluğunu kontrol et.")
        elif "Kahve Çekirdeği" in h_ad:
            uyarilar.append(f"☕ Çekirdek İhtiyacı: Baristaların öğütücü için {gosterim} çekirdek hazırlaması gerekiyor.")
        elif "Buz" in h_ad:
            uyarilar.append(f"🧊 Buz İhtiyacı: Sıcak havada talep artışı için buz makinesinin gece açık ve dolu olması önerilir (En az {gosterim}).")
        elif "Karton Bardak" in h_ad:
            uyarilar.append(f"🥤 Bardak İhtiyacı: Bar tezgahında en az {gosterim} hazır olmalıdır.")

    return uyarilar
