# -*- coding: utf-8 -*-
"""
Kingfool Inc. | Uluslararası Resmi Tatil ve Etkinlik Takvimi Modülü (v1.5)
Tüm dünya ülkelerinin (Türkiye, ABD, İngiltere, Almanya vb.) milli ve dini resmi tatillerini dinamik olarak çeker.
Ayrıca yerel kafe etkinliklerini ve özel ticari günleri (Sevgililer Günü, Kara Cuma vb.) yönetir.
Yapay zeka modellerine 'Tatil_Mi' özniteliği ve LLM koçuna takvim bağlamı sağlar.
"""
import os
import json
import datetime
from typing import Dict, List, Any, Optional

try:
    import holidays
except ImportError:
    holidays = None

from locations import ulke_kodu_bul

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ETKINLIK_DOSYASI = os.path.join(BASE_DIR, "ozel_etkinlikler.json")

# Türkiye Sabit Resmi Tatiller (Fallback ve Hızlı Referans)
SABIT_TATILLER_TR = {
    (1, 1): "Yılbaşı",
    (4, 23): "Ulusal Egemenlik ve Çocuk Bayramı",
    (5, 1): "Emek ve Dayanışma Günü",
    (5, 19): "Atatürk'ü Anma, Gençlik ve Spor Bayramı",
    (7, 15): "15 Temmuz Demokrasi ve Milli Birlik Günü",
    (8, 30): "Zafer Bayramı",
    (10, 29): "Cumhuriyet Bayramı",
}

# Türkiye Dini Bayram Tarihleri (2023-2027 Fallback)
DINI_BAYRAMLAR_TR = {
    # 2023
    "2023-04-21": "Ramazan Bayramı 1. Gün",
    "2023-04-22": "Ramazan Bayramı 2. Gün",
    "2023-04-23": "Ramazan Bayramı 3. Gün",
    "2023-06-28": "Kurban Bayramı 1. Gün",
    "2023-06-29": "Kurban Bayramı 2. Gün",
    "2023-06-30": "Kurban Bayramı 3. Gün",
    "2023-07-01": "Kurban Bayramı 4. Gün",
    # 2024
    "2024-04-09": "Ramazan Bayramı Arifesi",
    "2024-04-10": "Ramazan Bayramı 1. Gün",
    "2024-04-11": "Ramazan Bayramı 2. Gün",
    "2024-04-12": "Ramazan Bayramı 3. Gün",
    "2024-06-15": "Kurban Bayramı Arifesi",
    "2024-06-16": "Kurban Bayramı 1. Gün",
    "2024-06-17": "Kurban Bayramı 2. Gün",
    "2024-06-18": "Kurban Bayramı 3. Gün",
    "2024-06-19": "Kurban Bayramı 4. Gün",
    # 2025
    "2025-03-29": "Ramazan Bayramı Arifesi",
    "2025-03-30": "Ramazan Bayramı 1. Gün",
    "2025-03-31": "Ramazan Bayramı 2. Gün",
    "2025-04-01": "Ramazan Bayramı 3. Gün",
    "2025-06-05": "Kurban Bayramı Arifesi",
    "2025-06-06": "Kurban Bayramı 1. Gün",
    "2025-06-07": "Kurban Bayramı 2. Gün",
    "2025-06-08": "Kurban Bayramı 3. Gün",
    "2025-06-09": "Kurban Bayramı 4. Gün",
    # 2026
    "2026-03-19": "Ramazan Bayramı Arifesi",
    "2026-03-20": "Ramazan Bayramı 1. Gün",
    "2026-03-21": "Ramazan Bayramı 2. Gün",
    "2026-03-22": "Ramazan Bayramı 3. Gün",
    "2026-05-26": "Kurban Bayramı Arifesi",
    "2026-05-27": "Kurban Bayramı 1. Gün",
    "2026-05-28": "Kurban Bayramı 2. Gün",
    "2026-05-29": "Kurban Bayramı 3. Gün",
    "2026-05-30": "Kurban Bayramı 4. Gün",
    # 2027
    "2027-03-09": "Ramazan Bayramı Arifesi",
    "2027-03-10": "Ramazan Bayramı 1. Gün",
    "2027-03-11": "Ramazan Bayramı 2. Gün",
    "2027-03-12": "Ramazan Bayramı 3. Gün",
    "2027-05-16": "Kurban Bayramı Arifesi",
    "2027-05-17": "Kurban Bayramı 1. Gün",
    "2027-05-18": "Kurban Bayramı 2. Gün",
    "2027-05-19": "Kurban Bayramı 3. Gün",
    "2027-05-20": "Kurban Bayramı 4. Gün",
}

# Özel Ticari Günler (Satış patlaması yaratan küresel/yerel günler)
OZEL_TICARI_GUNLER = {
    (2, 14): "Sevgililer Günü",
    (10, 31): "Cadılar Bayramı (Halloween)",
    (12, 31): "Yılbaşı Gecesi",
}

# Önbellek: Her ülke ve yıl için tatil nesneleri
_TATIL_ONBELLEK: Dict[str, Any] = {}

def _ulke_tatilleri_getir(ulke_kodu: str, yil: int):
    """Holidays kütüphanesinden ilgili ülke ve yıl için tatil listesini döner."""
    key = f"{ulke_kodu}_{yil}"
    if key in _TATIL_ONBELLEK:
        return _TATIL_ONBELLEK[key]

    if holidays:
        try:
            h_obj = holidays.country_holidays(ulke_kodu, years=[yil - 1, yil, yil + 1])
            _TATIL_ONBELLEK[key] = h_obj
            return h_obj
        except Exception:
            pass
    return None

def ozel_etkinlikleri_yukle() -> Dict[str, str]:
    """Kullanıcının yerel olarak tanımladığı özel etkinlikleri döner."""
    if os.path.exists(ETKINLIK_DOSYASI):
        try:
            with open(ETKINLIK_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def ozel_etkinlik_kaydet(tarih: str, etkinlik_adi: str) -> bool:
    """Yeni bir yerel kafe etkinliği kaydeder (Örn: '2026-11-05', 'Canlı Müzik')."""
    veriler = ozel_etkinlikleri_yukle()
    veriler[tarih] = etkinlik_adi
    try:
        with open(ETKINLIK_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(veriler, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def tarih_tatil_veya_etkinlik_mi(tarih_str_or_date, ulke: str = "Türkiye") -> Dict[str, Any]:
    """
    Verilen tarihin resmi tatil, milli/dini bayram veya özel etkinlik olup olmadığını kontrol eder.
    Holidays kütüphanesi ile ülkeye özel tatilleri tam olarak çeker.
    Dönüş: {
        'tarih': 'YYYY-MM-DD',
        'tatil_mi': 1 or 0,
        'ozel_gun_mu': 1 or 0,
        'aciklama': 'Cumhuriyet Bayramı' / 'Memorial Day' vb.,
        'kategori': 'Resmi Tatil' | 'Dini Bayram' | 'Özel Gün' | 'Yerel Etkinlik' | 'Normal Gün'
    }
    """
    if isinstance(tarih_str_or_date, (datetime.date, datetime.datetime)):
        t_obj = tarih_str_or_date
        t_str = t_obj.strftime("%Y-%m-%d")
    else:
        t_str = str(tarih_str_or_date).strip()
        try:
            t_obj = datetime.datetime.strptime(t_str, "%Y-%m-%d").date()
        except Exception:
            t_obj = datetime.date.today()
            t_str = t_obj.strftime("%Y-%m-%d")

    ay, gun, yil = t_obj.month, t_obj.day, t_obj.year
    ulke_kodu = ulke_kodu_bul(ulke)

    # 1. Holidays Kütüphanesi ile Ülke Tatili Kontrolü
    h_obj = _ulke_tatilleri_getir(ulke_kodu, yil)
    if h_obj and t_str in h_obj:
        tatil_adi = h_obj.get(t_str)
        # Kategori tespiti (Dini / Resmi)
        t_lower = tatil_adi.lower()
        dini_kelimeler = ["ramazan", "kurban", "şeker", "eid", "sacrifice", "easter", "paskalya", "christmas", "noel", "hanukkah", "epiphany", "ascension", "pentecost", "assumption", "all saints"]
        kategori = "Dini Bayram" if any(w in t_lower for w in dini_kelimeler) else "Resmi Tatil"

        return {
            "tarih": t_str,
            "tatil_mi": 1,
            "ozel_gun_mu": 1,
            "aciklama": tatil_adi,
            "kategori": kategori
        }

    # 2. Türkiye Fallback Kontrolü (Holidays kütüphanesi yoksa veya ek TR günleri için)
    if ulke_kodu == "TR":
        if (ay, gun) in SABIT_TATILLER_TR:
            return {
                "tarih": t_str,
                "tatil_mi": 1,
                "ozel_gun_mu": 1,
                "aciklama": SABIT_TATILLER_TR[(ay, gun)],
                "kategori": "Resmi Tatil"
            }
        if t_str in DINI_BAYRAMLAR_TR:
            return {
                "tarih": t_str,
                "tatil_mi": 1,
                "ozel_gun_mu": 1,
                "aciklama": DINI_BAYRAMLAR_TR[t_str],
                "kategori": "Dini Bayram"
            }

    # 3. Özel Ticari Gün Kontrolü
    if (ay, gun) in OZEL_TICARI_GUNLER:
        return {
            "tarih": t_str,
            "tatil_mi": 0,
            "ozel_gun_mu": 1,
            "aciklama": OZEL_TICARI_GUNLER[(ay, gun)],
            "kategori": "Özel Ticari Gün"
        }

    # 4. Kullanıcı Tanımlı Özel Etkinlik Kontrolü
    ozel_etkinlikler = ozel_etkinlikleri_yukle()
    if t_str in ozel_etkinlikler:
        return {
            "tarih": t_str,
            "tatil_mi": 0,
            "ozel_gun_mu": 1,
            "aciklama": ozel_etkinlikler[t_str],
            "kategori": "Yerel Etkinlik"
        }

    # Normal Gün
    return {
        "tarih": t_str,
        "tatil_mi": 0,
        "ozel_gun_mu": 0,
        "aciklama": "Normal Gün",
        "kategori": "Normal Gün"
    }

def yillik_tatil_listesi(yil: int = 2026, ulke: str = "Türkiye") -> List[Dict[str, Any]]:
    """Belirtilen ülkenin ve yılın tüm resmi tatil ve bayramlarını liste olarak döner."""
    ulke_kodu = ulke_kodu_bul(ulke)
    h_obj = _ulke_tatilleri_getir(ulke_kodu, yil)
    liste = []

    dini_kelimeler = ["ramazan", "kurban", "şeker", "eid", "sacrifice", "easter", "paskalya", "christmas", "noel", "hanukkah", "epiphany"]
    if h_obj:
        for t_date, name in sorted(h_obj.items()):
            if t_date.year == yil:
                t_str = t_date.strftime("%Y-%m-%d")
                kategori = "Dini Bayram" if any(w in name.lower() for w in dini_kelimeler) else "Resmi Tatil"
                liste.append({"tarih": t_str, "ad": name, "kategori": kategori})
    else:
        # Fallback TR
        for (ay, gun), ad in SABIT_TATILLER_TR.items():
            t_str = f"{yil:04d}-{ay:02d}-{gun:02d}"
            liste.append({"tarih": t_str, "ad": ad, "kategori": "Resmi Tatil"})
        for t_str, ad in DINI_BAYRAMLAR_TR.items():
            if t_str.startswith(str(yil)):
                liste.append({"tarih": t_str, "ad": ad, "kategori": "Dini Bayram"})

    liste.sort(key=lambda x: x["tarih"])
    return liste
