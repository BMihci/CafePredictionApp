# -*- coding: utf-8 -*-
"""
Kingfool Inc. | Supabase Bulut Veritabanı Sürücüsü (v1.2 Cloud Edition)
"""
import os
import requests
import guvenlik
import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# Bağlantı bilgileri ortam değişkenlerinden okunur (bkz. README > Supabase).
# Tanımlı değilse uygulama yerel Excel/JSON dosyalarıyla çevrimdışı çalışır.
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def baglanti_kontrol():
    """Supabase veritabanı tablolarının hazır olup olmadığını test eder."""
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/kullanicilar?limit=1", headers=HEADERS, timeout=5)
        if r.status_code == 200:
            return True, "Supabase bulut veritabanı bağlı ve hazır!"
        elif r.status_code == 404:
            return False, "Tablolar henüz oluşturulmadı. Lütfen supabase_schema.sql dosyasını SQL Editor'de çalıştırın."
        else:
            return False, f"Supabase Hatası ({r.status_code}): {r.text}"
    except Exception as e:
        return False, f"Ağ Bağlantı Hatası: {e}"

def kullanicilari_yukle():
    """Tüm kullanıcıları ve tanımlı ürünlerini Supabase'den çeker."""
    try:
        r_user = requests.get(f"{SUPABASE_URL}/rest/v1/kullanicilar", headers=HEADERS, timeout=6)
        if r_user.status_code != 200:
            return {}
        
        users_list = r_user.json()
        
        r_prod = requests.get(f"{SUPABASE_URL}/rest/v1/urunler", headers=HEADERS, timeout=6)
        products_list = r_prod.json() if r_prod.status_code == 200 else []
        
        sonuc = {}
        for u in users_list:
            k_adi = u["kullanici_adi"]
            prods = [p["urun_adi"] for p in products_list if p["kullanici_adi"] == k_adi]
            sonuc[k_adi] = {
                "password": u["sifre"],
                "role": u.get("rol", "user"),
                "urunler": prods,
                "kurulum_tamam": u.get("kurulum_tamam", False)
            }
        return sonuc
    except Exception as e:
        print(f"[Supabase] Kullanıcılar yüklenirken hata: {e}")
        return {}

def kullanici_ekle(kullanici_adi, sifre, rol="user"):
    """Kullanıcıyı ekler; şifre özetlenmemişse özetleyerek saklar."""
    payload = {
        "kullanici_adi": kullanici_adi,
        "sifre": sifre if guvenlik.ozetli_mi(sifre) else guvenlik.sifre_ozetle(sifre),
        "rol": rol,
        "kurulum_tamam": False
    }
    r = requests.post(f"{SUPABASE_URL}/rest/v1/kullanicilar", headers=HEADERS, json=payload, timeout=6)
    return r.status_code in (200, 201)

def kullanici_sil(kullanici_adi):
    r = requests.delete(f"{SUPABASE_URL}/rest/v1/kullanicilar?kullanici_adi=eq.{kullanici_adi}", headers=HEADERS, timeout=6)
    return r.status_code in (200, 204)

def kullanici_sifre_guncelle(kullanici_adi, yeni_sifre):
    """Şifreyi günceller; özetlenmemişse özetleyerek saklar."""
    sifre = yeni_sifre if guvenlik.ozetli_mi(yeni_sifre) else guvenlik.sifre_ozetle(yeni_sifre)
    payload = {"sifre": sifre}
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/kullanicilar?kullanici_adi=eq.{kullanici_adi}", headers=HEADERS, json=payload, timeout=6)
    return r.status_code in (200, 204)

def kullanici_urunleri_kaydet(kullanici_adi, urunler):
    """Kullanıcının ürünlerini günceller ve kurulum_tamam'ı true yapar."""
    try:
        # Önceki ürünleri temizle
        requests.delete(f"{SUPABASE_URL}/rest/v1/urunler?kullanici_adi=eq.{kullanici_adi}", headers=HEADERS, timeout=6)
        
        # Yeni ürünleri ekle
        payload = [{"kullanici_adi": kullanici_adi, "urun_adi": u} for u in urunler if u.strip()]
        if payload:
            requests.post(f"{SUPABASE_URL}/rest/v1/urunler", headers=HEADERS, json=payload, timeout=6)
            
        # Kullanıcının kurulum_tamam bilgisini güncelle
        requests.patch(f"{SUPABASE_URL}/rest/v1/kullanicilar?kullanici_adi=eq.{kullanici_adi}", 
                       headers=HEADERS, json={"kurulum_tamam": True}, timeout=6)
        return True
    except Exception as e:
        print(f"[Supabase] Ürün kaydetme hatası: {e}")
        return False

def satis_kaydet(kullanici_adi, tarih, urun_adi, adet, sicaklik=25.0, haftasonu=0, promosyon=0):
    """Yeni satış kaydını Supabase'e ekler veya o güne ait kaydı günceller."""
    headers_upsert = HEADERS.copy()
    headers_upsert["Prefer"] = "resolution=merge-duplicates"
    
    payload = {
        "kullanici_adi": kullanici_adi,
        "urun_adi": urun_adi,
        "tarih": str(tarih),
        "satis_adedi": float(adet),
        "sicaklik": float(sicaklik),
        "haftasonu_mu": int(haftasonu),
        "promosyon_var_mi": int(promosyon)
    }
    r = requests.post(f"{SUPABASE_URL}/rest/v1/satislar", headers=headers_upsert, json=payload, timeout=6)
    return r.status_code in (200, 201)

def satis_gecmisi_df(kullanici_adi, urun_adi):
    """
    Belirli bir kullanıcı ve ürün için satış geçmişini çeker.
    Mevcut makine öğrenmesi motoruyla tam uyumlu Pandas DataFrame döndürür.
    Sütunlar: ['Tarih', 'Sicaklik', 'Haftasonu_Mu', 'Promosyon_Var_Mi', urun_adi]
    """
    try:
        url = f"{SUPABASE_URL}/rest/v1/satislar?kullanici_adi=eq.{kullanici_adi}&urun_adi=eq.{urun_adi}&order=tarih.asc"
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code != 200 or not r.json():
            return pd.DataFrame()
            
        data = r.json()
        df = pd.DataFrame(data)
        
        # Sütun isimlerini ve tiplerini standartlaştıralım
        df = df.rename(columns={
            "tarih": "Tarih",
            "sicaklik": "Sicaklik",
            "haftasonu_mu": "Haftasonu_Mu",
            "promosyon_var_mi": "Promosyon_Var_Mi",
            "satis_adedi": urun_adi
        })
        df["Tarih"] = pd.to_datetime(df["Tarih"])
        return df[["Tarih", "Sicaklik", "Haftasonu_Mu", "Promosyon_Var_Mi", urun_adi]]
    except Exception as e:
        print(f"[Supabase] Satış geçmişi çekilirken hata: {e}")
        return pd.DataFrame()

def yapay_zeka_tahmin(kullanici_adi, urun_kolonu, yarin_sicaklik, yarin_haftasonu):
    """
    Supabase'den çekilen canlı veri üzerinde Feature Engineering + RandomForest çalıştırır.
    """
    df = satis_gecmisi_df(kullanici_adi, urun_kolonu)
    if df.empty or urun_kolonu not in df.columns or len(df) < 8:
        return None, len(df)

    # Tarihe göre sırala
    df = df.sort_values("Tarih").reset_index(drop=True)

    # 1. Zaman Değişkenleri
    df["Ay"] = df["Tarih"].dt.month
    df["Haftanin_Gunu"] = df["Tarih"].dt.dayofweek

    # 2. Gecikmeli Değişkenler (Lag Features)
    df["Satis_Lag1"] = df[urun_kolonu].shift(1)
    df["Satis_Lag7"] = df[urun_kolonu].shift(7)

    # 3. Etkileşim Değişkeni (Interaction)
    promo = df["Promosyon_Var_Mi"].fillna(0)
    df["Sicaklik_x_Promosyon"] = df["Sicaklik"] * promo

    feature_cols = [
        "Sicaklik", "Haftasonu_Mu", "Promosyon_Var_Mi",
        "Ay", "Haftanin_Gunu", "Satis_Lag1", "Satis_Lag7",
        "Sicaklik_x_Promosyon"
    ]

    # 4. Eksik Veri Temizliği
    df_train = df.dropna(subset=feature_cols + [urun_kolonu]).reset_index(drop=True)
    veri_sayisi = len(df_train)

    if veri_sayisi < 5:
        return None, veri_sayisi

    X = df_train[feature_cols]
    y = df_train[urun_kolonu]

    model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X, y)

    # 5. Yarın İçin Çıkarım (Inference) Vektörü
    yarin_tarih = datetime.date.today() + datetime.timedelta(days=1)
    son_satislar = df[urun_kolonu].dropna().values
    lag1_val = son_satislar[-1] if len(son_satislar) >= 1 else y.mean()
    lag7_val = son_satislar[-7] if len(son_satislar) >= 7 else son_satislar[0]

    yarin_df = pd.DataFrame([{
        "Sicaklik": yarin_sicaklik,
        "Haftasonu_Mu": yarin_haftasonu,
        "Promosyon_Var_Mi": 0,
        "Ay": yarin_tarih.month,
        "Haftanin_Gunu": yarin_tarih.weekday(),
        "Satis_Lag1": lag1_val,
        "Satis_Lag7": lag7_val,
        "Sicaklik_x_Promosyon": 0.0
    }])[feature_cols]

    tahmin = round(model.predict(yarin_df)[0])
    return tahmin, veri_sayisi
